from pathlib import Path
import json
import runpy
import sys
import unittest
from xml.etree import ElementTree

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.landscape import crown_extent, tree

observe = runpy.run_path(str(ROOT/'scripts/observe-crowns.py'))['crown_volume']


class CrownGeometry(unittest.TestCase):
    def test_pine_shelves_share_a_stem_but_the_low_tree_can_turn_independently(self):
        plants=json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']
        pair=next(plant for plant in plants if plant['id']=='tree-72')
        original=ElementTree.fromstring(tree(pair));pine,low=original
        pads=pine.findall('.//g[@data-foliage-pad]')
        self.assertEqual([pad.attrib['data-foliage-pad'].rsplit('-',1)[1] for pad in pads],['west','east','leader'])
        self.assertNotEqual(pine.attrib['transform'],low.attrib['transform'])
        pair['stems'][1]['mirror']=True
        edited=ElementTree.fromstring(tree(pair))
        self.assertEqual(ElementTree.tostring(pine),ElementTree.tostring(edited[0]))
        self.assertNotEqual(low.attrib['transform'],edited[1].attrib['transform'])

    def test_moving_a_willow_spray_does_not_move_its_neighbours(self):
        plants=json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']
        plant=next(plant for plant in plants if plant['id']=='watch-willow-tip')
        def sprays():return [ElementTree.tostring(node) for node in ElementTree.fromstring(tree(plant)).findall('.//g[@data-spray]')]
        before=sprays();plant['stems'][0]['sprays'][0][2]+=3;after=sprays()
        self.assertGreater(len(before),2);self.assertNotEqual(before[0],after[0]);self.assertEqual(before[1:],after[1:])

    def test_volume_is_a_relative_editable_profile_not_a_texture(self):
        points = np.float64([(x,y) for y in range(12,36) for x in range(8,41)
                             if ((x-24)/15)**2+((y-24)/12)**2<1])
        model = dict(id='test-plant',x=24,y=38,scale=1,kind='willow')
        brightness = np.where(points[:,0]<24,98,181)
        volume = observe(points,model,brightness)
        shifted = dict(model,x=55,y=85)
        self.assertEqual(observe(points[::-1]+[31,47],shifted,brightness[::-1]),volume)
        self.assertEqual(set(volume),{'stations','wash','grain'})
        rows = volume['stations']
        self.assertEqual(len(rows),6)
        self.assertLess(rows[0][2],rows[2][2])
        self.assertLess(rows[-1][2],rows[3][2])
        model['crown'] = dict(volume=volume,tone='leaf',lobes=[[0,-15,9,10,1,1,3]])
        original = tree(model)
        self.assertEqual(original,tree(model))
        rows[2][1] += 18
        self.assertGreaterEqual(crown_extent(model)[2],rows[2][1]+rows[2][2])
        self.assertNotEqual(tree(model),original)

    def test_tiny_fragment_is_not_promoted_to_a_crown(self):
        fragment = np.array([[x,y] for x in range(4) for y in range(6)])
        self.assertIsNone(observe(fragment,{'x':2,'y':6},np.full(len(fragment),112)))

    def test_group_is_ordered_by_foot_and_crosses_the_canopy_tile_with_its_stems(self):
        front = dict(species='willow',root=[11,2],size=[19,30],paint='lime')
        back = dict(species='spire',root=[-9,-3],size=[9,16],paint='leaf')
        plant = dict(id='near-tile-line',x=380,y=100,stems=[front,back])
        svg = tree(plant)
        group = ElementTree.fromstring(svg)
        self.assertEqual([child.attrib['data-species'] for child in group],['spire','willow'])
        self.assertEqual(svg,tree(plant))
        self.assertLess(plant['x']+crown_extent(plant)[0],384)
        self.assertGreater(plant['x']+crown_extent(plant)[2],384)
        front['root'][0] += 22
        self.assertGreaterEqual(crown_extent(plant)[2],front['root'][0]+front['size'][0]/2)
        self.assertNotEqual(svg,tree(plant))

    def test_authored_stems_render_without_a_fallback_crown(self):
        plants=json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']
        families=set()
        for plant in plants:
            if 'stems' not in plant:continue
            self.assertNotIn('crown',plant)
            group=ElementTree.fromstring(tree(plant))
            for stem in plant['stems']:
                self.assertTrue(all(length>0 for length in stem['size']))
                families.add(stem['species'])
            self.assertEqual(len(group),len(plant['stems']))
        self.assertEqual(families,{'bamboo','blooming-bough','flower-spray','umbrella','cloud-pine','shrub','spire','willow','clipped-oval','orchard-oval','pear-crown','tiered-pine','low-pollard','fern-bank'})

    def test_orchard_pair_has_independent_feet_and_colours(self):
        plants=json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']
        pair=next(plant for plant in plants if plant['id']=='tree-75')
        back,front=sorted(pair['stems'],key=lambda stem:stem['root'][1])
        self.assertEqual([back['species'],front['species']],['pear-crown']*2)
        self.assertGreater(front['root'][0]-back['root'][0],6)
        self.assertNotEqual(back['paint'],front['paint'])
        before=ElementTree.fromstring(tree(pair))
        front['root'][0]+=2
        after=ElementTree.fromstring(tree(pair))
        self.assertEqual(ElementTree.tostring(before[0]),ElementTree.tostring(after[0]))
        self.assertNotEqual(before[1].attrib['transform'],after[1].attrib['transform'])

    def test_open_spires_and_the_bridgehead_pollard_keep_separate_feet(self):
        plants={plant['id']:plant for plant in json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']}
        bridgehead=plants['tree-196'];pine,pollard=bridgehead['stems']
        self.assertEqual((pine['species'],pollard['species']),('tiered-pine','low-pollard'))
        self.assertGreater(pollard['root'][0]-pine['root'][0],pollard['size'][0]*.5)
        bounds=crown_extent(bridgehead)
        self.assertGreaterEqual(bounds[2],pollard['root'][0]+pollard['size'][0]*.5)
        saplings=plants['tree-36'];first,second,middle,shrub=saplings['stems']
        self.assertTrue(all(stem['habit']=='open-spire' for stem in (first,second,middle)))
        self.assertNotEqual(first['paint'],second['paint'])
        self.assertTrue(first['root'][0]<middle['root'][0]<second['root'][0])
        self.assertGreater(shrub['root'][1],middle['root'][1])
        self.assertEqual(shrub['habit'],'bank-dome')
        original=ElementTree.fromstring(tree(saplings));first.pop('habit')
        edited=ElementTree.fromstring(tree(saplings))
        self.assertEqual([node.attrib['transform'] for node in original],[node.attrib['transform'] for node in edited])
        self.assertNotEqual(ElementTree.tostring(original),ElementTree.tostring(edited))

    def test_blossom_has_open_ground_below_petals_and_editable_flower_colour(self):
        stem=dict(species='blooming-bough',root=[5,2],size=[32,40],paint='leaf',bloom='ivory')
        model=dict(id='garden-tree',x=380,y=100,stems=[stem])
        drawing=tree(model);group=ElementTree.fromstring(drawing)[0]
        self.assertEqual(group.attrib['transform'],'translate(5 2) scale(1 1)')
        petals=group.findall('ellipse')[1:]
        self.assertTrue(petals)
        self.assertLess(max(float(p.attrib['cy'])+float(p.attrib['ry']) for p in petals),-5)
        self.assertTrue(all(node.attrib.get('fill')=='none' for node in group.findall('path')[1:]))
        self.assertEqual(drawing,tree(model))
        stem['bloom']='pink'
        self.assertNotEqual(drawing,tree(model))
        self.assertEqual([p.attrib['d'] for p in group.findall('path')],
                         [p.attrib['d'] for p in ElementTree.fromstring(tree(model))[0].findall('path')])

    def test_river_bend_has_three_flowering_feet_with_independent_leaders(self):
        plants=json.loads((ROOT/'src/data/town-landscape.json').read_text())['trees']
        bend=next(plant for plant in plants if plant['id']=='flowering-770-991')
        stems=[stem for stem in bend['stems'] if stem['species']=='blooming-bough']
        self.assertEqual(len({tuple(stem['root']) for stem in stems}),3)
        def stems_by_foot():return {stem.attrib['transform']:stem for stem in ElementTree.fromstring(tree(bend))}
        before=stems_by_foot();stems[0]['leaders'][1][0]+=3
        after=stems_by_foot();changed=[foot for foot in before if ElementTree.tostring(before[foot])!=ElementTree.tostring(after[foot])]
        self.assertEqual(len(changed),1)
        foot=changed[0];prior=before[foot].findall('g');edited=after[foot].findall('g')
        self.assertEqual(len(prior),len(stems[0]['leaders']))
        self.assertEqual([index for index in range(len(prior)) if ElementTree.tostring(prior[index])!=ElementTree.tostring(edited[index])],[1])
