import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
review = runpy.run_path(str(ROOT/'scripts/review-park-alignment.py'))
from art.alignment_diagnostics import assign_layer
from art.region_review import change_counts, region_map
from art.underpainting import foreground_counts


class WholeParkMetric(unittest.TestCase):
    def test_pre_encoding_pixel_assignment_uses_the_same_stepped_boundaries(self):
        raw_counts = runpy.run_path(str(ROOT/'scripts/review-region-spill.py'))['raw_counts']
        before = np.zeros((4,4,4),np.uint8); after = before.copy()
        after[:2,:2,3] = 255; after[2,0,1] = 9; after[3,2,2] = 31
        self.assertEqual(raw_counts(before,after,[909,849,2,2]),(2,{'nw':4,'ne':0,'sw':1,'se':1}))

    def test_foreground_transitions_distinguish_covered_ink_from_errors_already_underneath(self):
        target = np.array([1,0,0,1,1,0,1],bool); under = np.array([0,0,1,1,0,1,1],bool)
        final = np.array([1,1,0,0,0,1,0],bool); scope = np.array([1,1,1,1,1,1,0],bool)
        counts = foreground_counts(target,under,final,scope)
        classes = ['correctDarkening','extraDarkening','correctLightening','missedAfterLightening','missedInBoth','extraInBoth']
        for index,name in enumerate(classes):
            only = scope & (np.arange(scope.size)==index)
            self.assertEqual(foreground_counts(target,under,final,only),{key:int(key==name) for key in classes})
        strict = review['counts'](target,final,scope)
        self.assertEqual(strict['missed'],counts['missedAfterLightening']+counts['missedInBoth'])
        self.assertEqual(strict['extra'],counts['extraDarkening']+counts['extraInBoth'])

    def test_equal_totals_do_not_hide_a_cross_border_repaint(self):
        target = np.array([1,1,1,0,0],bool); before = np.array([1,0,0,1,0],bool)
        after = np.array([0,1,1,0,1],bool); valid = np.array([1,1,0,1,1],bool)
        self.assertEqual(review['counts'](target,before,valid),review['counts'](target,after,valid))
        self.assertEqual(change_counts(target,before,after,valid),{'corrected':2,'regressed':2})

    def test_regions_use_paper_coordinates_and_assign_each_seam_pixel_once(self):
        bounds = [907,418,1021,853]; owners = region_map(bounds)
        def at(easting,northing):return int(owners[northing-bounds[1],easting-bounds[0]])
        for northing,split,west,east in [(419,910,0,1),(420,1018,0,1),(849,1018,0,1),(850,910,2,3)]:
            self.assertEqual((at(split-1,northing),at(split,northing)),(west,east))
        self.assertEqual(np.bincount(owners.ravel()).sum(),114*435)
        spec = json.loads((ROOT/'docs/visual-acceptance-v1.json').read_bytes())
        valid = review['evaluation_mask'](spec).astype(bool); labels = region_map(spec['sourceBox'])
        self.assertEqual(sum(int(np.count_nonzero(valid & (labels==index))) for index in range(4)),833439)

    def test_distance_context_reports_all_errors_without_credit_or_excluded_ink(self):
        from art.alignment_diagnostics import diagnose
        rgb = np.full((9,18,3),[111,160,91],np.uint8); valid = np.ones((9,18),bool)
        valid[:,9] = False; reference = np.zeros_like(valid); drawing = np.zeros_like(valid)
        reference[4,[1,5,10,16]] = True; drawing[4,[2,7,9,16]] = True
        detail = diagnose(rgb,reference,drawing,valid,[30,180,48,189])
        self.assertEqual(detail['missed']['bands'],{'upTo1.5':1,'over1.5To3':2,'over3':0})
        self.assertEqual(detail['extra']['total'],2)
        for side in ('missed','extra'):
            self.assertEqual(detail[side]['byReferenceContext']['green'],detail[side]['bands'])
            self.assertEqual(sum(detail[side]['bands'].values()),detail[side]['total'])
        far = diagnose(rgb,reference,np.zeros_like(drawing),valid,[30,180,48,189])['missed']
        self.assertEqual(far['bands']['over3'],4)
        self.assertEqual(far['largestDistantCells'][0]['sourceBox'],[30,180,48,189])

    def test_published_frame_and_comparison_area_are_fixed(self):
        spec = (ROOT/'docs/visual-acceptance-v1.json').read_bytes()
        self.assertEqual(hashlib.sha256(spec).hexdigest(),'93e6b2cae375f25a45559c116c601360973f5a3bfb9e82bfa788f61e90038661')
        config = json.loads(spec); mask = review['evaluation_mask'](config)
        self.assertEqual(mask.shape,(1240,1520))
        self.assertEqual(mask.sum(),833439)
        self.assertEqual(hashlib.sha256(mask.tobytes()).hexdigest(),'53cdb737f210cfaf4dbe5375758f5a44ea524de63602ab79fa2f20da310c512a')
        self.assertEqual(len(config['landmarkWindows']),19)
        self.assertEqual({key for key in config['landmarkWindows']},{item['id'] for item in json.loads((ROOT/'src/data/landmark-models.json').read_text())['models']})

    def test_foreground_attribution_clips_offscreen_and_preserves_transparency(self):
        owners=np.zeros((2,3),np.uint8)
        assign_layer(owners,np.uint8([[255,127,128],[0,255,255]]),-1,0,3)
        assign_layer(owners,np.uint8([[0,128,255],[255,0,0]]),1,1,5)
        self.assertEqual(owners.tolist(),[[0,3,0],[3,3,5]])

    def test_rgb_luminance_and_strict_threshold(self):
        colors = np.uint8([[[144,144,144],[145,145,145],[247,115,0],[0,255,0]]])
        self.assertEqual(review['dark'](colors,145).tolist(),[[True,False,True,False]])

    def test_no_tolerance_no_background_credit(self):
        reference = np.array([[1,1,0,0],[0,0,1,1]],bool)
        drawing = np.array([[1,0,1,0],[0,0,1,0]],bool)
        valid = np.array([[1,1,1,1],[1,1,0,0]],bool)
        self.assertEqual(review['counts'](reference,drawing,valid),{'pixels':6,'intersection':1,'union':3,'missed':1,'extra':1,'iou':1/3})
        self.assertIsNone(review['counts'](reference,drawing,~np.ones_like(valid))['iou'])


if __name__ == '__main__':
    unittest.main()
