import base64,io,sys,unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pipeline import Pipeline
from assess import Assessor
class FakeDetector:
    def __init__(self,classes=(1,5)):self.classes=classes
    def predict(self,image,threshold):
        n=len(self.classes)
        return SimpleNamespace(xyxy=np.array([[10,10,100,100]]*n),confidence=np.array([.8]*n),class_id=np.array(self.classes))
def photo(view='left'):
    b=io.BytesIO();Image.new('RGB',(200,200),'gray').save(b,format='JPEG')
    return {'image':'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode(),'view':view}
def run(classes=(1,5),**data):
    request={'mode':'sell','photos':[photo('left'),photo('rear')],'vehicle':'Chevrolet Cobalt','query':''}
    request.update(data)
    return Assessor(Pipeline(detector=FakeDetector(classes),retriever=None)).assess(request)
class Tests(unittest.TestCase):
    def setUp(self):
        import assess
        self.lookup=assess.Assessor.lookup
        assess.Assessor.lookup=lambda self,q,**p:(__import__('retrieve').retrieve(q,**p),'keyword')
    def tearDown(self):
        import assess;assess.Assessor.lookup=self.lookup
    def test_multi_photo_findings_and_report(self):
        r=run()
        self.assertEqual(len(r['photos']),2)
        self.assertEqual({d['label'] for d in r['findings']},{'scratch','tire flat'})
        self.assertEqual(r['views_damaged'],['left','rear'])
        self.assertTrue(r['evidence']['evidence'])
        self.assertEqual(r['verdict']['level'],'red')  # flat tyre record is stop_and_assess
        self.assertIn('Vehicle condition report',r['report'])
    def test_workshops_follow_vehicle_brand(self):
        r=run()
        self.assertTrue(r['workshops'])
        self.assertTrue(all('Chevrolet' in w['brands'] for w in r['workshops']))
    def test_demo_technicians_have_coordinates_and_match_needs(self):
        r=run()
        self.assertTrue(r['technicians'])
        for t in r['technicians']:
            self.assertTrue(t['demo']);self.assertTrue(t['matched'])
            self.assertTrue(41<t['lat']<41.5 and 69<t['lon']<69.5)
        self.assertTrue(any('Tyre fitting' in t['matched'] for t in r['technicians']))
    def test_text_only_fleet_without_component(self):
        r=run(photos=[],mode='fleet',query='flat tyre, lost pressure on the highway')
        self.assertEqual(r['findings'],[])
        self.assertTrue(any(e['part']=='tire' for e in r['evidence']['evidence']))
        self.assertIn('Fleet incident report',r['report'])
    def test_no_damage_is_not_reported_as_safe(self):
        r=run(classes=())
        self.assertEqual(r['verdict']['level'],'none')
        self.assertTrue(any('does not prove' in w for w in r['warnings']))
    def test_invalid_input_rejected(self):
        for bad in [{'mode':'x'},{'photos':[{'image':'not base64!','view':'left'}]},{'photos':[photo('roof')]},
                    {'photos':[photo()]*11},{'photos':[],'query':''},{'threshold':True}]:
            with self.assertRaises(ValueError):run(**bad)
if __name__=='__main__':unittest.main()
