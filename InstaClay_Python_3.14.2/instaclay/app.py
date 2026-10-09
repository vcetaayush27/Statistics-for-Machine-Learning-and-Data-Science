from datetime import datetime, time
from zoneinfo import ZoneInfo
import json, html
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from core import ROOT, FEATURES, post_features, predict, intervals

st.set_page_config(page_title='InstaClay · Engagement Studio', page_icon='◉',layout='wide')
st.markdown('''<style>
:root{color-scheme:light;} .stApp{background:radial-gradient(ellipse at 95% 5%,#fbe5ee 0,transparent 35%),radial-gradient(ellipse at 5% 60%,#e9e5fb 0,transparent 40%),#f7f5fc;color:#302943;}
.block-container{max-width:1350px;padding-top:2.1rem;padding-bottom:3rem;}
h1,h2,h3{letter-spacing:-.035em!important;color:#302943;} h1{font-size:2.8rem!important;} p{line-height:1.6;}
[data-testid="stSidebar"]{background:#eeebf8;border-right:1px solid #fff;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#fff,#f0ebfb);border:1px solid white;border-radius:24px;padding:22px;box-shadow:9px 9px 22px #dcd6e766,-6px -6px 18px #fff,inset 2px 2px 5px #fff;}
[data-testid="stMetricValue"]{color:#72529d;font-weight:750;}
[data-testid="stForm"],.clay{background:linear-gradient(135deg,#fffcff,#f0ebf8);border:1px solid #fff!important;border-radius:26px!important;padding:26px!important;box-shadow:10px 10px 26px #dad3e766,-8px -8px 24px #fff,inset 2px 2px 5px white;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px!important;border:1px solid #fff!important;box-shadow:5px 5px 12px #d4cbe6,-3px -3px 8px #fff;transition:transform .18s,box-shadow .18s;min-height:44px;}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);box-shadow:7px 7px 16px #ccc1df;}
button[kind="primary"]{background:#9267cd!important;color:white!important;}
textarea,input{color:#302943!important;background:#fcfaff!important;}
[data-baseweb="select"]>div{background:#fcfaff!important;color:#302943!important;border-radius:12px;}
[data-testid="stPlotlyChart"]{border-radius:24px;background:#ffffffa8;padding:10px;box-shadow:5px 5px 16px #ded8e84d;}
.kicker{color:#9673be;font-size:12px;letter-spacing:.18em;font-weight:800;text-transform:uppercase;}
.hero{display:flex;align-items:center;justify-content:space-between;padding:30px 34px;margin-bottom:25px;border-radius:30px;background:linear-gradient(110deg,#eee4fc,#ffedf2);box-shadow:10px 10px 26px #d8cfe555,inset 2px 2px 5px white;border:1px solid white;}
.hero h1{margin:4px 0 10px;} .hero p{margin:0;max-width:620px;color:#72627e;}
.orb{width:112px;height:112px;border-radius:34px;display:flex;align-items:center;justify-content:center;font-size:57px;color:white;transform:rotate(-9deg);background:linear-gradient(135deg,#c09ded,#ea9fc5);box-shadow:12px 14px 24px #c5acd466,inset 5px 5px 12px #fff8,inset -5px -5px 12px #a368a855;}
.pill{display:inline-block;background:#fff8;border:1px solid white;border-radius:30px;padding:5px 12px;font-size:12px;color:#7d5b98;margin-top:14px;}
.small{color:#80738c;font-size:13px;} .result{font-size:3.5rem;font-weight:800;color:#8151b9;letter-spacing:-.04em;}
@media(max-width:700px){.orb{display:none}.hero{padding:22px}.hero h1{font-size:2rem!important}.block-container{padding:1rem;}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;}}
</style>''',unsafe_allow_html=True)

@st.cache_resource
def assets():
    report=json.loads((ROOT/'artifacts/report.json').read_text(encoding='utf-8'))
    bundle=joblib.load(ROOT/'artifacts/model.joblib')
    return report,bundle

@st.cache_data
def table(name):return pd.read_csv(ROOT/'artifacts'/name)

if not (ROOT/'artifacts/model.joblib').exists():
    st.error('Model files are missing. Run: python train.py');st.stop()
try:
    r,b=assets();d=table('cleaned_posts.csv');metrics=table('test_metrics.csv');cv=table('cross_validation.csv')
except Exception as exc:
    st.error('Project assets could not load. Stop Streamlit and run retrain_windows.bat, then restart.')
    st.caption(str(exc))
    st.stop()
COLORS=['#a683db','#eda6c6','#8ecac2','#f0c481']

def chart(fig):
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#63536f',family='Arial'),margin=dict(l=25,r=25,t=50,b=25),colorway=COLORS)
    st.plotly_chart(fig,width='stretch')

def hero(title,description,icon='♡'):
    st.markdown(f'<div class="hero"><div><div class="kicker">InstaClay / engagement studio</div><h1>{title}</h1><p>{description}</p><span class="pill">INSTAGRAM · STATISTICS + MACHINE LEARNING</span></div><div class="orb">{icon}</div></div>',unsafe_allow_html=True)

def form_fields(prefix):
    caption=st.text_area('Caption',value='A little moment worth sharing ✨ #creativity #inspiration',max_chars=2200,key=prefix+'caption',height=125)
    tags=st.text_input('Additional hashtags',value='',placeholder='#design #photography',key=prefix+'tags')
    a,c=st.columns(2)
    kind=a.selectbox('Post format',b['types'],key=prefix+'type')
    tz=c.selectbox('Your timezone',['Asia/Kolkata','UTC','America/New_York','Europe/London'],key=prefix+'tz')
    a,c=st.columns(2)
    day=a.date_input('Planned date',value=datetime.now().date(),key=prefix+'date')
    hour=c.time_input('Planned time',value=time(18,0),key=prefix+'time')
    stamp=pd.Timestamp(datetime.combine(day,hour)).tz_localize(tz,ambiguous=False,nonexistent='shift_forward').tz_convert('UTC')
    f=post_features(caption,tags,kind,stamp)
    return pd.DataFrame([f]),caption,stamp

def prediction_card(frame,label):
    p=float(predict(b['model'],frame)[0]);lo,hi=intervals(b['model'],frame,b['radius'])
    st.markdown(f'<div class="clay"><div class="kicker">{html.escape(label)}</div><div class="result">{p:,.0f}</div><b>estimated likes + comments</b><p class="small">80% model range: {lo[0]:,.0f} – {hi[0]:,.0f}</p></div>',unsafe_allow_html=True)
    return p,float(lo[0]),float(hi[0])

with st.sidebar:
    st.markdown('## ◉ InstaClay')
    st.caption('Plan thoughtfully. Measure honestly.')
    page=st.radio('Workspace',['Overview','Predict a post','Compare two posts','Statistics','Model performance','Data & methods'],label_visibility='collapsed')
    st.divider()
    st.caption(f"{r['clean_rows']:,} usable posts · {r['accounts']:,} accounts")
    st.caption('Light studio / academic edition')

if page=='Overview':
    hero('A clearer view of engagement.','Explore your Instagram sample, test a post idea, and compare plans with evidence.')
    cols=st.columns(4)
    for col,label,value in zip(cols,['Usable posts','Median engagement','Content formats','Selected model'],[f"{len(d):,}",f"{d.engagement.median():,.0f}",str(d.content_type.nunique()),b['selected']]):col.metric(label,value)
    st.write('')
    a,c=st.columns([1.35,1])
    with a:
        st.subheader('Most posts are small. A few go big.')
        chart(px.histogram(d.assign(log_engagement=np.log1p(d.engagement)),x='log_engagement',nbins=35,color_discrete_sequence=COLORS,labels={'log_engagement':'log(1 + likes + comments)'}))
    with c:
        st.subheader('Your content mix')
        counts=d.content_type.value_counts().rename_axis('Format').reset_index(name='Posts')
        chart(px.pie(counts,names='Format',values='Posts',hole=.68,color_discrete_sequence=COLORS))
    st.info('These are experimental historical estimates. Audience size and the time engagement was measured are unavailable as reliable pre-post inputs, so prediction ranges may be wide.')

elif page=='Predict a post':
    hero('Give your next idea a first look.','Enter the details you know before publishing. Caption length, hashtags, format and timing shape this estimate.','✧')
    a,c=st.columns([1.2,1])
    with a:
        with st.form('prediction'):
            f,caption,stamp=form_fields('p')
            submit=st.form_submit_button('Estimate engagement',type='primary',width='stretch')
    with c:
        st.subheader('Your post estimate')
        if submit:
            prediction_card(f,'Planned post')
            st.caption(f"{int(f.hashtag_count.iloc[0])} unique hashtags · {int(f.caption_length.iloc[0])} caption characters · {stamp.strftime('%a %H:%M')} UTC")
            if any(f[col].iloc[0]<limits[0] or f[col].iloc[0]>limits[1] for col,limits in b['numeric_ranges'].items()):st.warning('Some details fall outside the training range; the estimate is less reliable.')
            p=float(predict(b['model'],f)[0]);result=f.assign(predicted_engagement=p)
            st.download_button('Download prediction',result.to_csv(index=False),'prediction.csv','text/csv')
        else:
            st.markdown('<div class="clay"><div class="kicker">Ready when you are</div><div class="result">✧</div><p>Your estimate and uncertainty range will appear here.</p></div>',unsafe_allow_html=True)
        st.caption('No guaranteed outcome. This model measures caption structure, not the meaning of the text or image quality. The range is not a seven-day forecast.')

elif page=='Compare two posts':
    hero('Two ideas. One honest comparison.','Compare planned posts under the same model. A higher estimate is a model preference, not proof that a change causes better engagement.','↔')
    with st.form('compare'):
        a,c=st.columns(2)
        with a:st.subheader('Post A');fa,_,_=form_fields('a')
        with c:st.subheader('Post B');fb,_,_=form_fields('b')
        submit=st.form_submit_button('Compare these posts',type='primary',width='stretch')
    if submit:
        a,c=st.columns(2)
        with a:pa,la,ha=prediction_card(fa,'Post A')
        with c:pb,lb,hb=prediction_card(fb,'Post B')
        if abs(pa-pb)<.5:st.info('The model gives these posts effectively the same estimate.')
        else:st.info(f"Post {'A' if pa>pb else 'B'} has the higher estimate by {abs(pa-pb):,.0f} interactions.")
        if max(la,lb)<=min(ha,hb):st.warning('The prediction ranges overlap. There is no clear winner within this uncertainty.')
        comparison=pd.concat([fa.assign(post='A',prediction=pa,lower=la,upper=ha),fb.assign(post='B',prediction=pb,lower=lb,upper=hb)])
        st.download_button('Download comparison',comparison.to_csv(index=False),'comparison.csv','text/csv')

elif page=='Statistics':
    hero('Find patterns behind the posts.','Explore distributions and statistical associations. These results describe the uploaded sample; they do not establish cause and effect.','∿')
    chosen=st.multiselect('Explore formats',b['types'],default=b['types'])
    view=d[d.content_type.isin(chosen)]
    if view.empty:st.info('Select at least one format.');st.stop()
    a,c=st.columns(2)
    with a:chart(px.box(view,x='content_type',y='engagement',color='content_type',log_y=True,color_discrete_sequence=COLORS,title='Engagement by format (log scale)',points=False))
    with c:
        hourly=view.groupby('hour_utc').agg(median=('engagement','median'),posts=('engagement','size')).reset_index()
        chart(px.line(hourly,x='hour_utc',y='median',markers=True,hover_data=['posts'],title='Median engagement by posting hour · UTC',color_discrete_sequence=COLORS))
    st.caption('Zero engagement is omitted by a logarithmic axis. Hourly groups may be small; unadjusted comparisons can reflect different audiences.')
    correlations=view[['engagement','caption_length','word_count','hashtag_count','mention_count']].corr(method='spearman')
    chart(px.imshow(correlations,text_auto='.2f',zmin=-1,zmax=1,color_continuous_scale=['#89bdb6','#fffafc','#b18adc'],title='Spearman rank correlations'))
    st.subheader('Hypothesis tests · full cleaned sample')
    st.caption('H₀: engagement distributions are equal across groups. H₁: at least one differs. Kruskal–Wallis; Holm correction across three tests; α = 0.05. These tests do not identify which pairs differ.')
    st.dataframe(table('hypothesis_tests.csv'),hide_index=True,width='stretch')
    st.caption('Epsilon squared estimates rank-based effect size. With one post per account, account repetition is absent, but representativeness and confounding remain concerns.')
    st.subheader('Descriptive statistics')
    st.dataframe(table('descriptive_statistics.csv'),hide_index=True,width='stretch')
    ci=r['statistics']['median_95_bootstrap_ci'];st.caption(f"Median engagement: {r['median_engagement']:.0f}; 95% bootstrap interval: {ci[0]:.0f}–{ci[1]:.0f} (2,000 resamples).")

elif page=='Model performance':
    hero('Performance you can inspect.','Models were selected by five-fold cross-validation on training data. The test set was kept separate from tuning.','◎')
    st.success('Selected model: '+b['selected'])
    if float(metrics.loc[metrics.model==b['selected'],'R2'].iloc[0]) < 0:
        st.warning('Low predictive reliability: raw test R² is below zero. The model does not beat the test-mean benchmark on squared count error.')
    a,c=st.columns(2)
    with a:
        st.subheader('Training cross-validation')
        st.dataframe(cv[['model','cv_rmsle','cv_sd']],hide_index=True,width='stretch')
    with c:
        st.subheader('Untouched test set')
        st.dataframe(metrics,hide_index=True,width='stretch')
    st.caption('Lower MAE, RMSE and RMSLE are better. R² can be negative: that means worse than predicting the test mean. Regression has no honest single “accuracy %”. Selection emphasizes RMSLE to reduce domination by viral outliers.')
    predictions=table('test_predictions.csv')
    a,c=st.columns(2)
    with a:
        plot=predictions.assign(actual_log=np.log1p(predictions.actual),predicted_log=np.log1p(predictions[b['selected']]))
        fig=px.scatter(plot,x='actual_log',y='predicted_log',opacity=.6,color_discrete_sequence=COLORS,title='Actual vs predicted · log(1 + engagement)')
        limit=max(plot.actual_log.max(),plot.predicted_log.max());fig.add_shape(type='line',x0=0,y0=0,x1=limit,y1=limit,line=dict(color='#ed9fc3',dash='dash'));chart(fig)
    with c:
        importance=table('feature_importance.csv').sort_values('importance')
        chart(px.bar(importance,x='importance',y='feature',orientation='h',error_x='std',color_discrete_sequence=COLORS,title='Permutation importance · test set'))
    st.caption(f"80% interval observed test coverage: {r['observed_test_coverage']:.1%}. Wide intervals reflect limited predictive information; they are not a promise of future coverage.")
    st.download_button('Download model results',metrics.to_csv(index=False),'model_results.csv','text/csv')

else:
    hero('Know what powers the estimate.','A transparent view of cleaning, feature choices and the limits of this dataset.','✓')
    st.subheader('Cleaning audit')
    st.json({k:r[k] for k in ['input_rows','duplicate_post_ids_removed','missing_or_invalid_targets_removed','invalid_metadata_removed_after_targets','missing_captions','missing_hashtag_fields','clean_rows','accounts']})
    st.write('Missing likes are excluded from supervised learning. Captions are Unicode-normalized, whitespace is cleaned, hashtag lists are parsed and deduplicated, timestamps are converted to UTC. Valid viral outliers are retained.')
    st.subheader('What goes into the model')
    st.write('Caption character and word counts, unique hashtags, mentions, punctuation, cyclic posting hour/day, and content format. All can be specified before publication.')
    st.write('Likes and comments form the target only. Views, engagement scores, post IDs, account IDs and collection-time follower counts are excluded from model inputs.')
    st.subheader('Validation design');st.json(r['split_counts'])
    st.write('Accounts do not overlap across training, calibration and test sets. All learned preprocessing runs inside cross-validation. Calibration sets the 80% prediction range. The deployed model is the same one evaluated on the test set.')
    for note in r['limitations']:st.markdown('• '+note)
    st.download_button('Download cleaned dataset',(ROOT/'artifacts/cleaned_posts.csv').read_bytes(),'cleaned_posts.csv','text/csv')
    st.download_button('Download audit and methodology',(ROOT/'artifacts/report.json').read_bytes(),'report.json','application/json')
    st.caption('No external APIs, credentials, or network calls are required while using the app. Keep raw data local when sharing the project publicly.')

st.markdown('<p class="small" style="text-align:center;margin-top:40px">InstaClay · Built for thoughtful experiments, not guaranteed virality.</p>',unsafe_allow_html=True)
