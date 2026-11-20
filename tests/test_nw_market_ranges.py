import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.nw_market_ranges import MARKETS, market_layer


class MarketFronts(unittest.TestCase):
    def test_only_named_timber_is_replaced_not_roofs_gaps_or_trees(self):
        features = json.loads((ROOT/'src/data/town-architecture.json').read_bytes())['features']
        removed, drawing = market_layer(features)
        self.assertEqual(removed, {key for _, group, _ in MARKETS.values() for key in group})
        self.assertEqual({feature['kind'] for feature in features if feature['id'] in removed}, {'wood'})
        self.assertEqual(market_layer([feature for feature in features if feature['id'] not in removed]), (set(),''))
        self.assertNotIn('mask=', drawing)

    def test_members_and_floors_are_distinct(self):
        for name,(_,timber,members) in MARKETS.items():
            removed,drawing=market_layer([{'id':key} for key in timber])
            self.assertEqual(set(timber),removed)
            block=ET.fromstring(drawing)
            self.assertEqual(block.get('id'),'nw-market-'+name)
            self.assertEqual([bay.get('id') for bay in block], ['nw-market-'+member[0] for member in members])
            self.assertEqual([bay.get('data-storeys') for bay in block], ['1']*5 if name=='islet' else ['1','2'])
            with self.assertRaises(ValueError):
                market_layer([{'id':timber[0]}])
