"""Bound the remaining strict IoU work without producing geometry or relaxed scores."""
import numpy as np

from .region_review import REGIONS, region_map


CELL_SIZES = (1, 2, 4, 8, 16, 32, 64)


def deficit(intersection, union):
    return 17 * int(union) - 20 * int(intersection)


def pair_capacity(missed, extra, cell_size):
    if cell_size <= 0 or missed.shape != extra.shape or missed.ndim != 2 or not missed.size:
        raise ValueError('Expected equally sized non-empty images and a positive cell size')
    height, width = missed.shape
    rows = np.arange(0, height, cell_size)
    columns = np.arange(0, width, cell_size)

    def totals(mask):
        bands = np.add.reduceat(mask, rows, axis=0, dtype=np.int64)
        return np.add.reduceat(bands, columns, axis=1)

    return int(np.minimum(totals(missed), totals(extra)).sum())


def summarize(intersection, missed, extra, pairs):
    union = intersection + missed + extra
    levels = {}
    for cell_size, count in pairs.items():
        best_union = union - count
        levels[str(cell_size)] = {
            'pairable': count,
            'unpairedMissed': missed - count,
            'unpairedExtra': extra - count,
            'upperIouAtUnchangedCellTotals': (intersection + count) / best_union if best_union else None,
            'remainingDeficitTwentieths': deficit(intersection + count, best_union),
        }
    return {'intersection': intersection, 'union': union, 'missed': missed, 'extra': extra,
            'deficitTwentieths': deficit(intersection, union), 'byCellSize': levels}


def capacity_report(bounds, target, drawing, valid):
    owners = region_map(bounds)
    if not (owners.shape == target.shape == drawing.shape == valid.shape):
        raise ValueError('Raster shapes differ from paper coordinates')
    regions = {}
    total_pairs = dict.fromkeys(CELL_SIZES, 0)
    for index, name in enumerate(REGIONS):
        scope = valid & (owners == index)
        missed = scope & target & ~drawing
        extra = scope & ~target & drawing
        pairs = {size: pair_capacity(missed, extra, size) for size in CELL_SIZES}
        regions[name] = summarize(int((scope & target & drawing).sum()), int(missed.sum()), int(extra.sum()), pairs)
        for size, number in pairs.items():
            total_pairs[size] += number
    intersection, missed, extra = [sum(row[key] for row in regions.values()) for key in ('intersection', 'missed', 'extra')]
    return {'note': 'Diagnostic only, not a tolerance metric. A deficit unit is 1/20 of a pixel: '
                    '0.85 is met iff 17*union - 20*intersection <= 0. Pairing relocates an existing '
                    'extra to a missing point in the same paper-aligned cell and region; this is '
                    'an optimistic bound, not a proposed edit. No error positions are exported.',
            'gridOrigin': bounds[:2], 'regions': regions, 'wholePark': summarize(intersection, missed, extra, total_pairs)}
