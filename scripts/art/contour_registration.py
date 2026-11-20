"""Close small gaps without translating the contour of a roof in illustration space."""
import cv2
import numpy as np


def close_roof_gaps(mask):
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(mask, kernel, anchor=(1, 1))
    return cv2.erode(dilated, kernel, anchor=(0, 0))


def matches_archived_contour(feature, archived, legacy_closing):
    offset = int(legacy_closing and feature['kind'] in ('roof', 'gold'))
    left, top, width, height = feature['bounds']
    if (feature['kind'] != archived['kind'] or feature['id'] != archived['id'] or
            archived['bounds'] != [left+offset, top+offset, width, height]):
        return False
    def retained(ring, old):
        return {(horizontal+offset,vertical+offset) for horizontal,vertical in ring} <= set(map(tuple,old))
    return retained(feature['points'],archived['points']) and all(
        any(retained(hole,old) for old in archived['holes']) for hole in feature['holes'])


def reviewed_eave(feature, archived, legacy_closing, opening_indices=()):
    """Recover a reviewed building ring, never re-fit a hand-edited silhouette."""
    kind = feature['kind']
    if kind not in ('roof', 'gold', 'wood') or not matches_archived_contour(feature, archived, legacy_closing):
        raise ValueError(f'Unregistered building: {feature["id"]}')
    offset = int(legacy_closing and kind != 'wood')

    def simplify(ring, tolerance):
        points = np.asarray(ring, dtype=np.int32) - offset
        result = cv2.approxPolyDP(points, tolerance, True).reshape(-1, 2)
        if len(result) < 3 or cv2.contourArea(result) == 0:
            raise ValueError('Degenerate building ring')
        return result.tolist()

    if feature['points'] != simplify(archived['points'], .75 if kind == 'wood' else .95):
        raise ValueError(f'Edited silhouette: {feature["id"]}')
    outer = simplify(archived['points'], .65)
    if list(cv2.boundingRect(np.int32(outer))) != feature['bounds']:
        raise ValueError('Building extent changed')
    holes = list(feature['holes'])
    for index in opening_indices:
        ring = archived['holes'][index]
        samples = set(map(tuple, np.int32(ring) - offset))
        if any(set(map(tuple, hole)) <= samples for hole in holes):
            raise ValueError('Opening already retained')
        holes.append(simplify(ring, .6))
    return dict(feature, points=outer, holes=holes)
