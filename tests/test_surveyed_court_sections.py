import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.street_houses import roof_frame


class SurveyedCourtSectionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        survey = json.loads((ROOT / 'src/data/street-houses.json').read_bytes())
        cls.streets = {group['id']: group for side in ('background', 'sites')
                       for rows in survey[side].values() for group in rows}

    def check_section(self, street, index, dimension, stations):
        group = self.streets[street]
        model = group['houses'][index]
        left, right, *_ = roof_frame(model, group.get('roofForms', {}).get(str(index)))
        for horizontal, expected, tolerance in stations:
            fraction = (horizontal - left[0]) / (right[0] - left[0])
            actual = left[1] + fraction * (right[1] - left[1])
            if dimension == 'foot':
                actual += model[7]
            with self.subTest(street=street, index=index, station=horizontal):
                self.assertLessEqual(abs(actual - expected), tolerance)

    def test_middle_grove_eave_opens_onto_first_yard(self):
        self.check_section('southwest-paired-courts', 3, 'eave', [(344, 1277.6, 1.2), (355, 1276.2, 1.3)])

    def test_south_grove_shop_meets_its_own_ground(self):
        self.check_section('southwest-paired-courts', 8, 'foot', [(350, 1297.9, 1), (366, 1295.5, 1.1)])

    def test_night_market_eave_respects_its_diagonal_front(self):
        self.check_section('night-shop-courts', 7, 'eave', [(848, 1037.6, 1.1), (870, 1034.3, 1.1)])
