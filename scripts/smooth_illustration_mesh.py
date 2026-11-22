"""Choose smoothing on observed controls, then sample a conforming offline triangle mesh."""
import math

from calibrate_illustration import Mesh, cross, predict, rms, supported, train


def select_on_controls(points, anchor_limit):
    folds = [(point, points[:index]+points[index+1:]) for index, point in enumerate(points)]
    folds = [(point, rest) for point, rest in folds if supported(point['satellitePx'], rest)]
    if len(folds) < 5:
        raise ValueError('Too few supported control-only leave-one-out predictions')
    scores = []
    for smoothing in (None, 0, 0.01, 0.1, 0.5, 2, 'mesh'):
        errors = [math.dist(predict(train(rest, smoothing), point['satellitePx']), point['scenePx'])
                  for point, rest in folds]
        fitted = train(points, smoothing)
        anchor_error = max(math.dist(predict(fitted, point['satellitePx']), point['scenePx']) for point in points)
        scores.append(dict(smoothing=smoothing, looRmsScenePx=rms(errors), maxAnchorPx=anchor_error))
    eligible = [score for score in scores if score['maxAnchorPx'] <= anchor_limit]
    if not eligible:
        raise ValueError('No model meets the fixed observed-control displacement limit')
    chosen = min(eligible, key=lambda score: score['looRmsScenePx'])
    return train(points, chosen['smoothing']), dict(chosen=chosen['smoothing'], looCount=len(folds),
                                                  maxAnchorPx=anchor_limit, scores=scores)


def boundary_crossings(source, target, triangles):
    counts = {}
    for tri in triangles:
        for a, b in zip(tri, tri[1:]+tri[:1]):
            edge = tuple(sorted((a, b)))
            counts[edge] = counts.get(edge, 0)+1
    if any(count > 2 for count in counts.values()):
        raise ValueError('Mesh has a nonmanifold edge')
    edges = [edge for edge, count in counts.items() if count == 1]
    def on_segment(a, b, p):
        return (abs(cross(a, b, p)) <= 1e-9 and
                all(min(a[axis], b[axis])-1e-9 <= p[axis] <= max(a[axis], b[axis])+1e-9 for axis in (0, 1)))
    crossings = 0
    for index, (a, b) in enumerate(edges):
        first, second = target[a], target[b]
        for c, d in edges[index+1:]:
            if len({a, b, c, d}) < 4:
                continue
            third, fourth = target[c], target[d]
            if ((cross(first, second, third)*cross(first, second, fourth) < 0 and
                 cross(third, fourth, first)*cross(third, fourth, second) < 0) or
                    on_segment(first, second, third) or on_segment(first, second, fourth) or
                    on_segment(third, fourth, first) or on_segment(third, fourth, second)):
                crossings += 1
    return crossings


def sample_mesh(points, fitted, levels):
    if not isinstance(levels, int) or not 0 <= levels <= 5:
        raise ValueError('Mesh subdivision level must be an integer from zero through five')
    base = Mesh(points)
    source = list(base.sites)
    target = [predict(fitted, point) for point in source]
    triangles = list(base.triangles)
    audit = []
    for level in range(levels+1):
        ratios = [cross(*[target[index] for index in tri]) / cross(*[source[index] for index in tri]) for tri in triangles]
        folds = sum(ratio <= 0 for ratio in ratios)
        audit.append(dict(level=level, meshNodes=len(source), triangles=len(triangles),
                          foldedTriangles=folds, minimumAreaRatio=min(ratios)))
        if level == levels:
            break
        edges = sorted({tuple(sorted((start, end))) for tri in triangles for start, end in zip(tri, tri[1:]+tri[:1])})
        midpoints = {}
        departures = []
        for start, end in edges:
            site = [(source[start][axis]+source[end][axis])/2 for axis in (0, 1)]
            position = predict(fitted, site)
            departures.append(math.dist(position, [(target[start][axis]+target[end][axis])/2 for axis in (0, 1)]))
            midpoints[(start, end)] = len(source)
            source.append(site)
            target.append(position)
        audit[-1]['nextMidpointMaxDeparturePx'] = max(departures)
        def middle(a, b):
            return midpoints[tuple(sorted((a, b)))]
        refined = []
        for a, b, c in triangles:
            ab, bc, ca = middle(a, b), middle(b, c), middle(c, a)
            refined.extend([(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)])
        triangles = refined
    if audit[-1]['foldedTriangles']:
        raise ValueError('Selected smooth candidate folds; it cannot be represented as an invertible triangle mesh')
    crossings = boundary_crossings(source, target, triangles)
    audit[-1]['boundaryCrossings'] = crossings
    if crossings:
        raise ValueError('Selected smooth candidate has a self-intersecting boundary')
    return dict(controls=source, targets=target, triangles=triangles,
                supportSites=[point['satellitePx'] for point in points]), audit


def build_smooth_candidate(points, policy):
    if policy.get('kind') != 'control-loo-spline-mesh':
        raise ValueError('Unknown offline model selection policy')
    # Preserve the earlier calibration protocol: the limit is not tuned against held-out checks.
    if policy.get('maxAnchorPx') != 4:
        raise ValueError('Smooth candidate must preserve the established four-pixel anchor limit')
    fitted, selection = select_on_controls(points, policy['maxAnchorPx'])
    mesh, refinement = sample_mesh(points, fitted, policy['subdivisionLevels'])
    selection.update(kind=policy['kind'], observedControlCount=len(points), refinement=refinement,
                     note='Synthetic mesh nodes approximate the selected model; they are not observed controls or extra location support.')
    return mesh, selection
