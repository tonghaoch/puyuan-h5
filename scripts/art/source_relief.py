"""Recover tonal planes and long ink marks from the reference, within an existing surface."""
import math
import cv2
import numpy as np


def source_relief(gray, region, origin, kind):
    x, y = origin
    samples = gray[region > 0]
    if samples.size < 12:
        return {'tones': [], 'seams': []}
    # Suppress JPEG grain while retaining the source's folds, beams and masonry shading.
    if kind in ['roof', 'gold']:
        weight = (region > 0).astype(float)
        smooth = cv2.GaussianBlur(gray.astype(float) * weight, (0, 0), 1.15)
        smooth /= np.maximum(cv2.GaussianBlur(weight, (0, 0), 1.15), .001)
    else:
        smooth = cv2.bilateralFilter(gray, 5, 14, 2).astype(float)
    middle = float(np.median(samples))
    delta = smooth - middle
    bands = [(-2, delta < -18), (-1, (delta >= -18) & (delta < -7)),
             (1, (delta > 8) & (delta <= 21)), (2, delta > 21)]
    if kind in ['roof', 'gold', 'wood']:
        # Preserve the source's fine dark tile/joinery strokes separately from broad shading.
        fine = cv2.GaussianBlur(gray, (0, 0), .35) < max(24, middle - 25)
        inset = cv2.erode(region, np.ones((3, 3), np.uint8)) > 0
        bands.append((-3, fine & inset))
    tones = []
    for level, band in bands:
        mask = ((region > 0) & band).astype(np.uint8) * 255
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            continue
        limit, minimum = (96, .7) if level == -3 else (32, 2)
        for i in sorted(range(len(contours)), key=lambda i: cv2.contourArea(contours[i]), reverse=True)[:limit]:
            if hierarchy[0, i, 3] >= 0 or cv2.contourArea(contours[i]) < minimum:
                continue
            outer = cv2.approxPolyDP(contours[i], .3, True).reshape(-1, 2)
            if len(outer) < 3:
                continue
            holes = []
            child = hierarchy[0, i, 2]
            while child >= 0:
                if cv2.contourArea(contours[child]) >= 2:
                    hole = cv2.approxPolyDP(contours[child], .3, True).reshape(-1, 2)
                    if len(hole) >= 3:
                        holes.append((hole + [x, y]).tolist())
                child = hierarchy[0, child, 0]
            tones.append({'level': level, 'points': (outer + [x, y]).tolist(), 'holes': holes})

    seams = []
    if kind in ['roof', 'gold', 'wood'] and len(samples) >= 100:
        ink = ((gray < middle - 20) & (region > 0)).astype(np.uint8) * 255
        segments = cv2.HoughLinesP(ink, 1, np.pi / 180, threshold=7, minLineLength=8, maxLineGap=1)
        if segments is not None:
            ranked = sorted(segments.reshape(-1, 4), key=lambda a: math.hypot(int(a[2])-int(a[0]), int(a[3])-int(a[1])), reverse=True)
            for a, b, c, d in ranked:
                a, b, c, d = map(int, (a, b, c, d))
                # The longest source strokes survive; neighbouring Hough detections collapse.
                midpoint = ((a+c)/2, (b+d)/2)
                angle = math.atan2(d-b, c-a)
                if any(math.dist(midpoint, old[0]) < 3 and abs(math.sin(angle-old[1])) < .15 for old in seams):
                    continue
                seams.append((midpoint, angle, [[a+x, b+y], [c+x, d+y]]))
                if len(seams) == 8:
                    break
    return {'tones': tones, 'seams': [item[2] for item in seams]}
