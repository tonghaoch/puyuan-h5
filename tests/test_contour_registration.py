from pathlib import Path
import sys
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from art.contour_registration import close_roof_gaps, matches_archived_contour, reviewed_eave


class RoofRegistration(unittest.TestCase):
    def test_review_restores_only_selected_openings_in_illustration_space(self):
        corners = [[4,4],[19,5],[19,15],[4,15]]
        native = dict(id='roof-1',kind='roof',bounds=[4,4,16,12],points=corners,holes=[])
        returns = [[4,4],[5,4],[6,5],*corners[1:]]
        windows = [[[7,7],[9,7],[9,10],[7,10]], [[13,8],[16,8],[16,13],[13,13]]]
        current = dict(native,points=returns,holes=windows)
        old = dict(current,bounds=[5,5,16,12],points=(np.int32(returns)+1).tolist(),
                   holes=[(np.int32(ring)+1).tolist() for ring in windows])
        result = reviewed_eave(native,old,True,[1])
        self.assertEqual(result,reviewed_eave(native,current,False,[1]))
        self.assertEqual(result['points'],[corners[0],[6,5],*corners[1:]])
        self.assertEqual(result['holes'],[windows[1]])
        self.assertEqual(native['holes'],[])
        with self.assertRaisesRegex(ValueError,'Edited silhouette'):
            reviewed_eave(result,old,True)
        with self.assertRaisesRegex(ValueError,'already retained'):
            reviewed_eave(dict(native,holes=[windows[1]]),old,True,[1])
        with self.assertRaisesRegex(ValueError,'Degenerate'):
            reviewed_eave(native,dict(current,holes=[[[7,7],[8,7],[9,7]]]),False,[0])

    def test_closing_a_joint_keeps_eaves_and_courtyard_in_place(self):
        expected = np.zeros((24, 28), np.uint8)
        expected[3:19, 5:23] = 255
        expected[7:14, 11:17] = 0
        roof = expected.copy()
        roof[5, 6:10] = 0
        closed = close_roof_gaps(roof)
        np.testing.assert_array_equal(closed, expected)
        np.testing.assert_array_equal(close_roof_gaps(closed), expected)
        legacy = cv2.morphologyEx(roof, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
        self.assertEqual(cv2.boundingRect(legacy), (6, 4, 18, 16))
        self.assertEqual(cv2.boundingRect(closed), (5, 3, 18, 16))

    def test_legacy_and_balanced_archives_do_not_claim_an_unrelated_face(self):
        native=dict(id='roof-1',kind='roof',bounds=[4,5,8,7],points=[[4,5],[11,5],[4,11]],holes=[])
        old=dict(native,bounds=[5,6,8,7],points=[[5,6],[9,6],[12,6],[5,12]])
        self.assertTrue(matches_archived_contour(native,old,True))
        self.assertTrue(matches_archived_contour(native,native,False))
        self.assertFalse(matches_archived_contour(native,old,False))
        self.assertFalse(matches_archived_contour(dict(native,holes=[[[5,7],[7,7],[6,9]]]),old,True))
