import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from art.ink_budget import capacity_report, deficit, pair_capacity, summarize


class InkBudget(unittest.TestCase):
    def test_partial_cells_do_not_pair_ink_across_their_boundaries(self):
        missed = np.array([[1, 0, 0, 1, 0], [0, 0, 0, 0, 0]], dtype=bool)
        extra = np.array([[0, 1, 0, 0, 1], [0, 0, 0, 0, 0]], dtype=bool)
        self.assertEqual([pair_capacity(missed, extra, size) for size in (1, 2, 4, 8)], [0, 1, 1, 2])
        levels = summarize(3, 2, 2, {2: 1})['byCellSize']['2']
        self.assertEqual(levels['upperIouAtUnchangedCellTotals'], 4 / 6)
        self.assertEqual(levels['remainingDeficitTwentieths'], deficit(3, 7) - 37)

    def test_cells_never_borrow_from_another_region_or_excluded_ink(self):
        target = np.array([[1, 0, 1, 0, 1]], bool)
        drawing = np.array([[0, 0, 0, 1, 0]], bool)
        valid = np.array([[1, 1, 0, 1, 0]], bool)
        report = capacity_report([908, 300, 913, 301], target, drawing, valid)
        self.assertEqual(report['wholePark']['byCellSize']['64']['pairable'], 0)
        self.assertEqual(report['wholePark']['deficitTwentieths'], 34)
        self.assertIsNone(report['regions']['sw']['byCellSize']['1']['upperIouAtUnchangedCellTotals'])

    def test_goal_threshold_is_checked_without_rounding(self):
        self.assertEqual(deficit(17, 20), 0)
        self.assertGreater(deficit(849999, 1000000), 0)
        self.assertLess(deficit(850001, 1000000), 0)
