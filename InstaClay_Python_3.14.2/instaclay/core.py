from pathlib import Path
import json, re, unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
NUMERIC = ['caption_length', 'word_count', 'hashtag_count', 'mention_count', 'exclamation_count', 'question_count', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos']
FEATURES = NUMERIC + ['content_type']


def text_clean(value):
    if pd.isna(value):
        return ''
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(value))).strip()


def extract_tags(caption, serialized=''):
    tags = re.findall(r'(?<!\w)#(\w+)', caption, flags=re.UNICODE)
    if isinstance(serialized, str) and serialized.strip():
        try:
            extra = json.loads(serialized)
            if isinstance(extra, list):
                tags += [str(t).lstrip('#').strip() for t in extra if isinstance(t, str)]
        except (ValueError, TypeError):
            tags += re.findall(r'#(\w+)', serialized)
    return sorted({t.casefold() for t in tags if t})


def post_features(caption, hashtags, content_type, timestamp):
    caption = text_clean(caption)
    timestamp = pd.Timestamp(timestamp)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize('UTC')
    timestamp = timestamp.tz_convert('UTC')
    tags = extract_tags(caption, hashtags)
    hour = timestamp.hour + timestamp.minute / 60
    day = timestamp.dayofweek
    return dict(caption_length=len(caption), word_count=len(caption.split()),
                hashtag_count=len(tags), mention_count=len(re.findall(r'(?<!\w)@\w+', caption)),
                exclamation_count=caption.count('!'), question_count=caption.count('?'),
                hour_sin=np.sin(2*np.pi*hour/24), hour_cos=np.cos(2*np.pi*hour/24),
                day_sin=np.sin(2*np.pi*day/7), day_cos=np.cos(2*np.pi*day/7),
                content_type=content_type)


def clean_data(path):
    raw = pd.read_csv(path, dtype={'post_id':'string', 'user_posted_id':'string'})
    required = {'post_id','user_posted_id','description','hashtags','date_posted','content_type','likes','num_comments'}
    if required-set(raw.columns):
        raise ValueError('Missing required columns: '+', '.join(sorted(required-set(raw.columns))))
    audit = {'input_rows':len(raw), 'missing_captions':int(raw.description.isna().sum()),
             'missing_hashtag_fields':int(raw.hashtags.isna().sum())}
    d = raw.drop_duplicates('post_id').copy()
    audit['duplicate_post_ids_removed'] = len(raw)-len(d)
    for c in ['likes','num_comments']:
        d[c] = pd.to_numeric(d[c],errors='coerce')
        d.loc[(d[c]<0)|(~np.isfinite(d[c]))|(d[c]%1!=0),c] = np.nan
    d['timestamp'] = pd.to_datetime(d.date_posted,utc=True,errors='coerce')
    valid_target = d[['likes','num_comments']].notna().all(axis=1)
    audit['missing_or_invalid_targets_removed'] = int((~valid_target).sum())
    valid_meta = d.timestamp.notna() & d.content_type.notna() & d.user_posted_id.notna() & d.post_id.notna()
    audit['invalid_metadata_removed_after_targets'] = int((valid_target & ~valid_meta).sum())
    d = d.loc[valid_target & valid_meta].copy().reset_index(drop=True)
    d['caption'] = d.description.map(text_clean)
    rows = [post_features(r.caption,r.hashtags,r.content_type,r.timestamp) for r in d.itertuples()]
    f = pd.DataFrame(rows)
    for c in FEATURES: d[c] = f[c]
    d['engagement'] = d.likes + d.num_comments
    d['hour_utc'] = d.timestamp.dt.hour
    d['weekday'] = d.timestamp.dt.day_name()
    d['time_block'] = pd.cut(d.hour_utc,[-1,5,11,17,23],labels=['Night','Morning','Afternoon','Evening']).astype(str)
    # Retain only relevant analysis fields; account identifiers are only for splitting.
    keep = ['post_id','user_posted_id','timestamp','caption','likes','num_comments','engagement','hour_utc','weekday','time_block']+FEATURES
    audit.update(clean_rows=len(d),accounts=int(d.user_posted_id.nunique()),
                 oldest_post=str(d.timestamp.min()),newest_post=str(d.timestamp.max()),
                 median_engagement=float(d.engagement.median()),max_engagement=float(d.engagement.max()))
    return d[keep],audit


def predict(model, rows):
    # Models learn log1p engagement. Bound inversion to avoid numerical overflow.
    return np.maximum(0,np.expm1(np.clip(model.predict(rows[FEATURES]),0,30)))


def intervals(model, rows, radius):
    logp = np.clip(model.predict(rows[FEATURES]),0,30)
    return np.expm1(np.maximum(0,logp-radius)),np.expm1(np.minimum(30,logp+radius))
