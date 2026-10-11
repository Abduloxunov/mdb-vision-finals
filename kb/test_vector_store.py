"""Synthetic vectors test actual local DB behaviour; no relevance/accuracy claim."""
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import numpy as np
import retrieve
from runtime import configure, COLLECTION, DIMENSION
from vector_store import VectorKB, bm25, fuse, llm_context, point_id

class SyntheticVectorKB(VectorKB):
    def embed(self,texts,prefix):
        vectors=[]
        for text in texts:
            if prefix=='passage: ':
                index=next(i for i,r in enumerate(self.records) if text.startswith(r['title']+'\n'))
            elif any(term in text.casefold() for term in ['oil pressure','moy']): index=20
            elif 'brake' in text.casefold(): index=22
            elif 'crash' in text.casefold(): index=18
            elif 'bubble' in text.casefold(): index=11
            elif 'crack' in text.casefold(): index=6
            else:index=DIMENSION-1
            v=np.zeros(DIMENSION,dtype=np.float32);v[index]=1;vectors.append(v)
        return np.stack(vectors),100

class VectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=Path(tempfile.mkdtemp(prefix='vector-check-',dir=configure()/'tmp'))
        cls.base=cls.temp/'canonical';cls.base.mkdir()
        for name in ['knowledge.md','sources.md','workshops.md']:
            shutil.copyfile(retrieve.BASE/name,cls.base/name)
        cls.kb=SyntheticVectorKB(cls.temp/'store',base=cls.base)
        cls.first=cls.kb.ingest()

    @classmethod
    def tearDownClass(cls):
        cls.kb.close()
        # Keep tiny D: artifacts for inspection; no recursive deletion needed.

    def test_real_database_count(self):
        self.assertEqual(self.kb.client().count(COLLECTION,exact=True).count,28)
        self.assertEqual(self.first['inserted'],28)

    def test_reingestion_stable_ids(self):
        result=self.kb.ingest()
        self.assertEqual((result['inserted'],result['updated'],result['record_count']),(0,28,28))

    def test_scope_before_vector_selection(self):
        result=self.kb.query('bubble',part='tire',mode='semantic')
        self.assertEqual(result['status'],'candidates_found')
        self.assertEqual(result['evidence'][0]['id'],'K012')
        self.assertTrue(all(r['part']=='tire' for r in result['evidence']))

    def test_cross_component_closest_is_excluded(self):
        result=self.kb.query('bubble',part='body',mode='semantic')
        self.assertEqual(result['evidence'],[])

    def test_unknown_neighbour_does_not_become_evidence(self):
        result=self.kb.query('quantum banana spaceship',part='body')
        self.assertEqual(result['status'],'no_evidence')
        self.assertEqual(result['evidence'],[])
        self.assertEqual(result['sources'],[])

    def test_missing_component(self):
        self.assertEqual(self.kb.query('crack')['status'],'needs_context')

    def test_component_name_only(self):
        self.assertEqual(self.kb.query('my tyre',part='tire')['status'],'needs_context')

    def test_manual_confirmation_required(self):
        result=self.kb.query('oil pressure',part='dashboard',vehicle='Cobalt',context={'engine_running':True})
        self.assertEqual(result['status'],'needs_context')
        self.assertEqual(result['evidence'],[])

    def test_engine_state_required(self):
        for state in [{},{'engine_running':False}]:
            result=self.kb.query('oil pressure',part='dashboard',vehicle='Cobalt',confirmed_manual='S11',context=state)
            self.assertEqual(result['status'],'needs_context')
            self.assertEqual(result['evidence'],[])

    def test_confirmed_manual_and_state(self):
        result=self.kb.query('oil pressure',part='dashboard',vehicle='Cobalt',confirmed_manual='S11',context={'engine_running':True})
        self.assertEqual(result['evidence'][0]['id'],'K021')
        self.assertEqual({s['id'] for s in result['sources']},{'S11'})

    def test_wrong_model_is_excluded(self):
        result=self.kb.query('oil pressure',part='dashboard',vehicle='Spark',confirmed_manual='S11',context={'engine_running':True})
        self.assertEqual(result['evidence'],[])

    def test_brake_query_does_not_bypass_parking_context(self):
        result=self.kb.query('brake warning',part='dashboard',vehicle='Lacetti',confirmed_manual='S14',context={'engine_running':True})
        self.assertEqual(result['status'],'needs_context')
        self.assertEqual(result['evidence'],[])

    def test_ev_variant_guard(self):
        result=self.kb.query('crash',part='ev',vehicle='BYD Song')
        self.assertEqual(result['status'],'needs_context')
        self.assertEqual(result['evidence'],[])
        self.assertEqual(self.kb.query('crash',part='ev',propulsion='ice')['evidence'],[])

    def test_no_diagnostic_probability(self):
        result=self.kb.query('bubble',part='tire')
        self.assertIn('not diagnostic probabilities',result['method'])
        self.assertIsNone(result['cost_estimate'])

    def test_llm_context_does_not_invent_evidence(self):
        bundle=self.kb.query('crack')
        payload=llm_context(bundle)
        self.assertEqual(payload['status'],'needs_context')
        self.assertEqual(payload['evidence'],[])
        self.assertIsNone(payload['repair_cost'])

    def test_index_marker_missing(self):
        p=self.kb.root/'index-manifest.json';saved=p.read_text(encoding='utf-8')
        p.unlink()
        try:
            with self.assertRaises(RuntimeError): self.kb.query('bubble',part='tire')
        finally:p.write_text(saved,encoding='utf-8')

    def test_changed_markdown_rejected(self):
        p=self.base/'knowledge.md';saved=p.read_text(encoding='utf-8')
        p.write_text(saved.replace('Possible superficial clearcoat scratch','Changed record title'),encoding='utf-8')
        try:
            with self.assertRaises(RuntimeError):self.kb.query('bubble',part='tire')
        finally:p.write_text(saved,encoding='utf-8')

    def test_incompatible_manifest_rejected(self):
        p=self.kb.root/'index-manifest.json';saved=p.read_text(encoding='utf-8')
        data=json.loads(saved);data['revision']='another-model';p.write_text(json.dumps(data),encoding='utf-8')
        try:
            with self.assertRaises(RuntimeError):self.kb.query('bubble',part='tire')
        finally:p.write_text(saved,encoding='utf-8')

    @unittest.skipUnless(os.name=='nt','The D: storage rule applies to the Windows workstation only.')
    def test_c_disk_runtime_rejected(self):
        with self.assertRaises(ValueError):configure('C:/do-not-create')

    def test_invalid_threshold_rejected(self):
        for threshold in [float('nan'),True,1.5]:
            with self.assertRaises(ValueError):self.kb.query('x',part='body',min_cosine=threshold)

    def test_bm25_exact_term(self):
        rank=bm25(self.kb.records,'bulge')
        self.assertEqual(rank[0][0],'K012')

    def test_rrf_tie_preserves_semantic_order(self):
        ranked=fuse([('B-semantic-first',0.9),('A-keyword-first',0.8)],[('A-keyword-first',5),('B-semantic-first',4)])
        self.assertEqual(ranked[0][0],'B-semantic-first')

    def test_rrf_keeps_both_channels(self):
        merged=dict(fuse([('semantic-only',0.9),('shared',0.8)],[('keyword-only',5.0),('shared',1.0)]))
        self.assertEqual(set(merged),{'semantic-only','keyword-only','shared'})
        self.assertGreater(merged['shared'],merged['semantic-only'])

if __name__=='__main__':unittest.main()
