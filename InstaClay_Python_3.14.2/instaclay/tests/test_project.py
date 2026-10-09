import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import numpy as np
import pandas as pd
import joblib
from core import ROOT, FEATURES, extract_tags, post_features, predict, intervals, clean_data
from streamlit.testing.v1 import AppTest

class ProjectTests(unittest.TestCase):
    def test_hashtags_and_timezone(self):
        self.assertEqual(extract_tags('#Hello #hello', '["Hello","world"]'),['hello','world'])
        a=post_features('caption','#tag','Image','2025-01-01T18:00:00+05:30')
        b=post_features('caption','#tag','Image','2025-01-01T12:30:00Z')
        self.assertEqual(a,b)

    def test_target_and_leakage(self):
        d,a=clean_data(ROOT/'data/instagram_posts.csv')
        self.assertEqual(len(d),888)
        np.testing.assert_array_equal(d.engagement,d.likes+d.num_comments)
        self.assertTrue(set(FEATURES).isdisjoint({'likes','num_comments','followers','video_view_count','engagement_score_view','post_id','user_posted_id'}))
        s=pd.read_csv(ROOT/'artifacts/splits.csv')
        self.assertEqual(s.groupby('account_id')['split'].nunique().max(),1)
        self.assertTrue(d.post_id.is_unique)

    def test_predictions(self):
        b=joblib.load(ROOT/'artifacts/model.joblib')
        f=pd.DataFrame([post_features('A new idea! #art','#design','Image','2025-01-01T12:00:00Z')])
        p=predict(b['model'],f);lo,hi=intervals(b['model'],f,b['radius'])
        self.assertTrue(np.isfinite(p).all() and (p>=0).all())
        self.assertTrue((lo<=p).all() and (p<=hi).all())
        np.testing.assert_array_equal(p,predict(b['model'],f))

    def test_interface_pages_and_forms(self):
        at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        self.assertFalse(at.exception,list(at.exception))
        for page in ['Statistics','Model performance','Data & methods','Predict a post','Compare two posts']:
            at.sidebar.radio[0].set_value(page).run()
            self.assertFalse(at.exception,list(at.exception))
            if page in ['Predict a post','Compare two posts']:
                at.button[0].click().run()
                self.assertFalse(at.exception,list(at.exception))
        at.sidebar.radio[0].set_value('Statistics').run()
        at.multiselect[0].set_value([]).run()
        self.assertFalse(at.exception,list(at.exception))

if __name__=='__main__':unittest.main()
