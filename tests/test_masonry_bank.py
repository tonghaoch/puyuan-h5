import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from art.landscape import quay_face
from art.masonry_bank import curb_sections, inset_face


class MasonryBankTests(unittest.TestCase):
    def test_registered_toe_and_dry_side_cap_turn_together(self):
        edge = [(10,4),(5,4),(2,7)]
        sections = curb_sections(edge,4,1.5)
        self.assertEqual([row[0] for row in sections],edge)
        self.assertEqual([row[1] for row in sections],[(10,0),(5,0),(2,3)])
        self.assertEqual(sections[0][2],(10,-1.5))
        self.assertLess(sections[1][2][0],5)
        self.assertLess(sections[1][2][1],0)
        self.assertLess(sections[2][2][0],2)

    def test_only_the_enabled_span_replaces_ordinary_stone(self):
        edge = [(12,5),(8,5),(3,7),(0,8)]
        style = dict(finish='dressed-quay',span=[1,2],base='#998877',rise=4,copingWidth=1.5)
        result = quay_face(edge,3,style)
        self.assertEqual(result,quay_face(edge[:2],3,style['base'])+inset_face(edge[1:3],4,1.5)+quay_face(edge[2:],3,style['base']))
        self.assertEqual(len(ElementTree.fromstring('<svg>'+result+'</svg>').findall("g[@data-finish='dressed-quay']")),1)
        self.assertNotIn('dressed-quay',quay_face(edge,3,style['base']))
        with self.assertRaises(ValueError):
            quay_face(edge,3,dict(style,span=[1,4]))
