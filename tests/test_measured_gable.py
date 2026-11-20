from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as XML

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from art.street_houses import colonnade


class TimberGableTest(unittest.TestCase):
    def test_existing_bays_share_beam_with_gable(self):
        frame={'beam':[[2,10],[14,9]],'columns':[0,.3,.7,1],'infill':'lattice-panels'}
        old=XML.fromstring(colonnade(frame,6));new=XML.fromstring(colonnade(frame|{'gableHead':[8,5]},6))
        self.assertEqual(old.attrib,new.attrib)
        self.assertEqual([XML.tostring(item) for item in old],[XML.tostring(item) for item in new[1:]])
        self.assertEqual(new[0].get('d'),'M2,10L8,5L14,9Z')
