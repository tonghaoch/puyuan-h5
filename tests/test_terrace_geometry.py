import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.completions import pale_block
from art.stage import fan
from art.street_houses import end_wall, house, plaster_loft, quay_apron, roof_frame, stone_platform
from art.waterfront import projected_span


class TerraceGeometry(unittest.TestCase):
    def test_wall_foot_can_be_reset_without_repainting_a_roof(self):
        groups=json.loads((ROOT/'src/data/street-houses.json').read_text())['sites']['zen-gallery']
        group=next(item for item in groups if item['id']=='museum-timber-courts');foot=group['wallFeet']['6']
        def draw():return house(group['houses'][6],form=group.get('roofForms',{}).get('6'),wall_feet=foot)
        before,roof=draw();foot['gable']['ends'][0][1]+=1.7;after,other_roof=draw()
        self.assertIn('data-wall-foot=',before);self.assertNotEqual(before,after);self.assertEqual(roof,other_roof)

    def test_gate_upper_window_moves_without_moving_the_shutters(self):
        group=json.loads((ROOT/'src/data/street-houses.json').read_text())['background']['south-garden-lane'][0]
        model=group['houses'][5];form=group['roofForms']['5'];detail=form['plasterLoft'];corners=end_wall(model,roof_frame(model,form),form)
        def draw():return ElementTree.fromstring(plaster_loft(*corners,model[7],detail))
        before=draw();detail['lights'][0][0]+=.016;after=draw()
        self.assertEqual(ElementTree.tostring(before[0]),ElementTree.tostring(after[0]))
        self.assertEqual(sum(ElementTree.tostring(first)!=ElementTree.tostring(second) for first,second in zip(before,after)),1)

    def test_one_quay_post_can_be_lengthened_without_moving_the_shore_or_other_posts(self):
        groups=json.loads((ROOT/'src/data/street-houses.json').read_text())['sites']['dressing-house']
        apron=next(item for item in groups if item['id']=='dressing-timber-loft')['quayAprons'][0]
        before=ElementTree.fromstring(quay_apron(apron));apron['supports'][1][3]+=1.4;after=ElementTree.fromstring(quay_apron(apron))
        changed=[index for index,(first,second) in enumerate(zip(before,after)) if first.attrib!=second.attrib]
        self.assertEqual(changed,[len(before)-6,len(before)-5])

    def test_a_curved_glazing_bar_can_be_repaired_without_moving_its_neighbours(self):
        canopy=json.loads((ROOT/'src/data/landmark-structures.json').read_text())['sites']['waterside-stage']['canopy']
        def draw():return ElementTree.fromstring(fan(canopy))
        before=draw();canopy['muntins'][0][3][5]+=.64;after=draw()
        for drawing in (before,after):
            bars=drawing.find('./g[@data-glazing-bay="0"]/g').findall('g[@data-glazing-bar]');self.assertEqual(len(bars),len(canopy['muntins'][0]))
        self.assertNotEqual(ElementTree.tostring(before),ElementTree.tostring(after))
        for drawing in (before,after):
            parent=drawing.find('./g[@data-glazing-bay="0"]/g');parent.remove(parent.findall('g[@data-glazing-bar]')[3])
        self.assertEqual(ElementTree.tostring(before),ElementTree.tostring(after))

    def test_extended_trestle_bent_leaves_the_deck_and_other_bents_unchanged(self):
        bridge=next(item for item in json.loads((ROOT/'src/data/town-landscape.json').read_text())['bridges'] if item['id']=='bridge-9')
        before=ElementTree.fromstring(projected_span(bridge));bridge['bents'][2][2]+=1.8;after=ElementTree.fromstring(projected_span(bridge))
        self.assertEqual(len(before.findall('./g[@data-trestle-bent]')),5)
        self.assertEqual([index for index,(first,second) in enumerate(zip(before,after)) if ElementTree.tostring(first)!=ElementTree.tostring(second)],[2])

    def test_river_gable_pan_spacing_only_changes_the_selected_pitch(self):
        groups=json.loads((ROOT/'src/data/street-houses.json').read_text())['sites']['temple-hall']
        group=next(item for item in groups if item['id']=='temple-river-gables')
        model=group['houses'][0];form=group['roofForms']['0']
        def draw():return ElementTree.fromstring('<g>'+''.join(house(model,form=form))+'</g>')
        before=draw();form['panPitch'][0]*=1.6;after=draw()
        panels=before.findall('.//g[@data-pan-rows]');other=after.findall('.//g[@data-pan-rows]')
        self.assertEqual(len(panels),2);self.assertGreater(int(panels[0].attrib['data-pan-rows']),int(other[0].attrib['data-pan-rows']))
        self.assertEqual(ElementTree.tostring(panels[1]),ElementTree.tostring(other[1]))
        for drawing in (before,after):
            for parent in drawing.iter():
                for child in list(parent):
                    if 'data-pan-rows' in child.attrib:parent.remove(child)
        self.assertEqual(ElementTree.tostring(before),ElementTree.tostring(after))

    def test_lowering_the_recess_wall_leaves_the_outer_stone_edges_intact(self):
        block=json.loads((ROOT/'src/data/town-completions.json').read_text())['paleBlocks'][0]
        original=ElementTree.fromstring(pale_block(block))
        opening=block['openings'][0];opening['wallFoot'][0][1]+=1.5
        edited=ElementTree.fromstring(pale_block(block))
        self.assertNotEqual(ElementTree.tostring(original),ElementTree.tostring(edited))
        for index in (0,-1):self.assertEqual(original[index].attrib,edited[index].attrib)
        self.assertEqual(len(original),len(edited))

    def test_near_gables_face_the_flight_and_its_cheek_can_be_repaired_separately(self):
        bank=json.loads((ROOT/'src/data/street-houses.json').read_text())['background']['east-west-bank']
        group=next(group for group in bank if group['id']=='west-bank-stepped-gables')
        for index,model in enumerate(group['houses']):
            form=group['roofForms'][str(index)];frame=roof_frame(model,form)
            self.assertEqual(end_wall(model,frame,form),(frame[1],form['ridge'][1],form['rear'][1]))
            self.assertGreater(frame[1][1],frame[0][1])
        flight=group['platforms'][0];before=ElementTree.fromstring(stone_platform(flight));flight['cheeks'][0][2][0]-=2
        after=ElementTree.fromstring(stone_platform(flight));self.assertEqual(before.attrib,after.attrib)
        self.assertEqual(before.attrib['data-stair-treads'],'2')
        self.assertEqual(sum(first.attrib!=second.attrib for first,second in zip(before,after)),1)
