import json, hashlib, platform
import numpy as np
import pandas as pd
import joblib, sklearn
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, make_scorer
from sklearn.inspection import permutation_importance
from core import ROOT, NUMERIC, FEATURES, clean_data, predict, intervals


def clipped_log_rmse(actual, predicted):
    return float(np.sqrt(mean_squared_error(actual, np.clip(predicted, 0, 30))))


LOG_SCORER = make_scorer(clipped_log_rmse, greater_is_better=False)


def holm(values):
    p=np.asarray(values); order=np.argsort(p); result=np.empty(len(p)); last=0
    for rank,i in enumerate(order):
        last=max(last,min(1,(len(p)-rank)*p[i])); result[i]=last
    return result


def statistics(d):
    out=ROOT/'artifacts'
    d[['engagement','likes','num_comments','caption_length','hashtag_count']].describe().to_csv(out/'descriptive_statistics.csv')
    tests=[]
    for col in ['content_type','time_block','weekday']:
        groups=[v.engagement.to_numpy() for _,v in d.groupby(col) if len(v)>=5]
        h,p=stats.kruskal(*groups)
        n=sum(map(len,groups)); k=len(groups)
        tests.append(dict(comparison=col,test='Kruskal–Wallis',statistic=float(h),p_value=float(p),
                          epsilon_squared=float(max(0,(h-k+1)/(n-k))),groups=k,n=n))
    adjusted=holm([r['p_value'] for r in tests])
    for r,p in zip(tests,adjusted):r['p_holm']=float(p);r['significant_005']=bool(p<.05)
    pd.DataFrame(tests).to_csv(out/'hypothesis_tests.csv',index=False)
    correlations=[]
    for col in ['caption_length','word_count','hashtag_count','mention_count','exclamation_count','question_count']:
        rho,p=stats.spearmanr(d[col],d.engagement)
        correlations.append(dict(feature=col,spearman_rho=float(rho),p_value=float(p)))
    for r,p in zip(correlations,holm([r['p_value'] for r in correlations])):r['p_holm']=float(p)
    pd.DataFrame(correlations).to_csv(out/'correlations.csv',index=False)
    rng=np.random.default_rng(42)
    medians=[np.median(rng.choice(d.engagement,len(d),replace=True)) for _ in range(2000)]
    return {'median_95_bootstrap_ci':np.quantile(medians,[.025,.975]).tolist(),'tests':tests}


def pipeline(estimator):
    pre=ColumnTransformer([
        ('numbers',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUMERIC),
        ('type',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['content_type'])])
    return Pipeline([('prepare',pre),('model',estimator)])


def run():
    out=ROOT/'artifacts';out.mkdir(exist_ok=True)
    d,audit=clean_data(ROOT/'data/instagram_posts.csv')
    d.to_csv(out/'cleaned_posts.csv',index=False)
    stat=statistics(d)
    groups=d.user_posted_id
    traincal,test=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(d,groups=groups))
    tr,ca=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=43).split(d.iloc[traincal],groups=groups.iloc[traincal]))
    train,cal=traincal[tr],traincal[ca]
    assert not (set(groups.iloc[train]) & set(groups.iloc[test]))
    assert not (set(groups.iloc[cal]) & (set(groups.iloc[train]) | set(groups.iloc[test])))
    X=d[FEATURES];y=np.log1p(d.engagement)
    candidates={
        'Median baseline':(DummyRegressor(strategy='median'),{}),
        'Linear Regression':(LinearRegression(),{}),
        'Random Forest':(RandomForestRegressor(n_estimators=300,random_state=42,n_jobs=1),
                         {'model__min_samples_leaf':[3,10,20],'model__max_features':[.7,1.0]}),
        'Gradient Boosting':(HistGradientBoostingRegressor(random_state=42,max_iter=180,early_stopping=False),
                             {'model__max_leaf_nodes':[7,15],'model__l2_regularization':[1.,10.]})}
    models={};cvrows=[]
    for name,(estimator,grid) in candidates.items():
        search=GridSearchCV(pipeline(estimator),grid,cv=GroupKFold(5),scoring=LOG_SCORER,n_jobs=1)
        search.fit(X.iloc[train],y.iloc[train],groups=groups.iloc[train])
        models[name]=search.best_estimator_
        cvrows.append({'model':name,'cv_rmsle':float(-search.best_score_),
                       'cv_sd':float(search.cv_results_['std_test_score'][search.best_index_]),'parameters':str(search.best_params_)})
        print(name,cvrows[-1]['cv_rmsle'],flush=True)
    cv=pd.DataFrame(cvrows).sort_values('cv_rmsle');cv.to_csv(out/'cross_validation.csv',index=False)
    # Include the simple baseline in selection rather than force a weaker ML model.
    selected=cv.iloc[0]['model'];chosen=models[selected]
    residual=np.abs(y.iloc[cal].to_numpy()-np.clip(chosen.predict(X.iloc[cal]),0,30))
    rank=min(len(residual),int(np.ceil((len(residual)+1)*.8)))
    radius=float(np.sort(residual)[rank-1])
    metrics=[];predframe=pd.DataFrame({'post_id':d.post_id.iloc[test].to_numpy(),'actual':d.engagement.iloc[test].to_numpy()})
    for name,m in models.items():
        p=predict(m,X.iloc[test]);actual=d.engagement.iloc[test]
        metrics.append({'model':name,'MAE':mean_absolute_error(actual,p),'RMSE':np.sqrt(mean_squared_error(actual,p)),
                        'R2':r2_score(actual,p),'RMSLE':np.sqrt(mean_squared_error(np.log1p(actual),np.log1p(p))),
                        'log_R2':r2_score(np.log1p(actual),np.log1p(p))})
        predframe[name]=p
    pd.DataFrame(metrics).to_csv(out/'test_metrics.csv',index=False)
    lo,hi=intervals(chosen,X.iloc[test],radius)
    predframe['lower_80']=lo;predframe['upper_80']=hi;predframe.to_csv(out/'test_predictions.csv',index=False)
    imp=permutation_importance(chosen,X.iloc[test],y.iloc[test],scoring=LOG_SCORER,n_repeats=10,random_state=42)
    pd.DataFrame({'feature':FEATURES,'importance':imp.importances_mean,'std':imp.importances_std}).sort_values('importance',ascending=False).to_csv(out/'feature_importance.csv',index=False)
    splits=pd.DataFrame({'post_id':d.post_id,'account_id':groups,'split':'train'})
    splits.loc[cal,'split']='calibration';splits.loc[test,'split']='test';splits.to_csv(out/'splits.csv',index=False)
    bundle={'model':chosen,'models':models,'selected':selected,'radius':radius,'features':FEATURES,
            'types':sorted(d.content_type.unique().tolist()),'numeric_ranges':{c:[float(d.iloc[train][c].min()),float(d.iloc[train][c].max())] for c in NUMERIC[:6]}}
    joblib.dump(bundle,out/'model.joblib',compress=3)
    report={**audit,'statistics':stat,'selected_model':selected,'selection_metric':'Lowest five-fold training CV RMSLE',
            'split_counts':{'train':len(train),'calibration':len(cal),'test':len(test)},'test_metrics':metrics,
            'nominal_interval_coverage':.8,'observed_test_coverage':float(np.mean((d.engagement.iloc[test].to_numpy()>=lo)&(d.engagement.iloc[test].to_numpy()<=hi))),
            'interval_log_radius':radius,'raw_sha256':hashlib.sha256((ROOT/'data/instagram_posts.csv').read_bytes()).hexdigest(),
            'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,'pandas':pd.__version__,'numpy':np.__version__},
            'limitations':['Only 888 labeled posts in the supplied sample; measured metrics are not guaranteed future accuracy.',
            'Followers, account post counts, views, likes, comments and engagement scores are excluded from predictors.',
            'Follower counts and account flags are collection-time snapshots, not verified pre-publication values.',
            'No engagement observation window or collection timestamp is supplied: this estimates observed historical engagement, not seven-day engagement.',
            'Missing captions are treated as empty text; the source cannot distinguish absence from collection failure.',
            'Posting times use UTC. Associations are observational, unadjusted for audience size and cannot establish causation.',
            'Caption text is represented by length and punctuation counts; semantic meaning and images are not modeled.',
            'Prediction intervals are split-conformal intervals under exchangeability; distribution shift can invalidate coverage.']}
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('SELECTED',selected,'TEST',metrics,'COVERAGE',report['observed_test_coverage'],flush=True)
    return report

if __name__=='__main__':run()
