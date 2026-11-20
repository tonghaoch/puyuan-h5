import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.ne_root_order import contact_order
from art.plantings import planting


class RootOrder(unittest.TestCase):
    def setUp(self):
        rows=json.loads((ROOT/'src/data/town-landscape.json').read_bytes())['trees'];self.by_id={row['id']:row for row in rows}

    def test_interleaves_real_feet_not_group_centres(self):
        trees=[self.by_id[k] for k in ('tree-51','flowering-1229-638')];draw=[]
        def capture(model,index,first):
            draw.append((model['id'],index,first));return ''
        contact_order(trees,capture);self.assertEqual(draw,[('tree-51',3,True),('tree-51',2,False),('tree-51',0,False),('flowering-1229-638',0,True),('tree-51',1,False)])
        for model in trees:
            full=planting(model)
            for idx,_ in enumerate(model['stems']):
                single=planting(model,idx);self.assertIn(single[single.index('>')+1:-4],full)

    def test_rejects_moved_foot_and_preserves_nonparticipants(self):
        trees=[deepcopy(self.by_id[k]) for k in ('tree-51','flowering-1229-638')];trees[0]['stems'][2]['root'][0]+=.5
        with self.assertRaisesRegex(ValueError,'grounding'):contact_order(trees,lambda *args:'')
        self.assertEqual(contact_order([self.by_id['tree-54'],self.by_id['tree-51']],lambda model:model['id']+';'),''.join(row['id']+';' for row in sorted([self.by_id['tree-54'],self.by_id['tree-51']],key=lambda m:m['y'])))
