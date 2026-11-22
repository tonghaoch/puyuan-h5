"""Recompute the local illustration fit and render its held-out bridge checks, offline."""
import base64
import io
import json
import math
from html import escape
from pathlib import Path
from statistics import mean
from string import Template

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'references/geodata/east-water-street-registration.json'
OUTPUT = ROOT / 'artifacts/location-calibration'
MERCATOR_RADIUS = 6378137.0


def solve(first, second, target):
    east_x, south_x = first
    east_y, south_y = second
    target_x, target_y = target
    determinant = east_x * south_y - south_x * east_y
    if abs(determinant) <= 1e-12 * math.hypot(*first) * math.hypot(*second):
        raise ValueError('Landmarks must span two dimensions')
    return ((target_x * south_y - south_x * target_y) / determinant,
            (east_x * target_y - target_x * east_y) / determinant)


def fit(controls):
    if len(controls) < 3:
        raise ValueError('At least three controls are needed for an affine fit')
    columns = list(zip(*[point['satellitePx'] + point['scenePx'] for point in controls]))
    centers = list(map(mean, columns))
    east, south, scene_x, scene_y = [[value - center for value in column]
                                    for column, center in zip(columns, centers)]

    def dot(first, second):
        return sum(left * right for left, right in zip(first, second))

    covariance_x = dot(east, east), dot(east, south)
    covariance_y = covariance_x[1], dot(south, south)
    rows = []
    for target, center in zip((scene_x, scene_y), centers[2:]):
        scale_x, scale_y = solve(covariance_x, covariance_y, (dot(east, target), dot(south, target)))
        rows.append((scale_x, scale_y, center - scale_x * centers[0] - scale_y * centers[1]))
    return rows


def audit(spec, world):
    controls, checks = spec['controls'], spec['checks']
    if not checks:
        raise ValueError('At least one independent check is needed')
    points = controls + checks
    for field in ('id', 'satellitePx', 'scenePx'):
        values = [point[field] for point in points]
        if any(value in values[:index] for index, value in enumerate(values)):
            raise ValueError(f'Repeated landmark {field}')
    rows = fit(controls)
    east_x, north_x, east_y, north_y, origin_east, origin_north = world

    def measure(point):
        source_x, source_y = point['satellitePx']
        east = origin_east + east_x * source_x + east_y * source_y
        north = origin_north + north_x * source_x + north_y * source_y
        latitude = math.atan(math.sinh(north / MERCATOR_RADIUS))
        predicted = [scale_x * source_x + scale_y * source_y + offset for scale_x, scale_y, offset in rows]
        delta = [value - observed for value, observed in zip(predicted, point['scenePx'])]
        pixel_x, pixel_y = solve(rows[0][:2], rows[1][:2], delta)
        meters = math.cos(latitude) * math.hypot(east_x * pixel_x + east_y * pixel_y,
                                                north_x * pixel_x + north_y * pixel_y)
        return {**point, 'referenceLonLat': [math.degrees(east / MERCATOR_RADIUS), math.degrees(latitude)],
                'predictedScenePx': predicted, 'deltaScenePx': delta, 'equivalentMeters': meters}

    checked = list(map(measure, checks))
    errors = [point['equivalentMeters'] for point in checked]
    return {'region': spec['region'], 'affineSatellitePxToScenePx': rows,
            'controls': list(map(measure, controls)), 'checks': checked,
            'checkRmsMeters': math.sqrt(mean(error ** 2 for error in errors)), 'checkMaxMeters': max(errors)}


def panel(image, bounds, points, coordinates, detail=False):
    left, top, right, bottom = bounds
    width, height = right - left, bottom - top
    buffer = io.BytesIO()
    image.crop(bounds).save(buffer, 'PNG')
    raster = base64.b64encode(buffer.getvalue()).decode('ascii')
    content = [f'<svg viewBox="0 0 {width} {height}" aria-hidden="true">',
               f'<image width="{width}" height="{height}" href="data:image/png;base64,{raster}"/>']
    radius = 1.45 if detail else 3.0
    for point in points:
        center_x, center_y = point[coordinates]
        center_x, center_y = center_x - left + 0.5, center_y - top + 0.5
        if coordinates == 'scenePx' and 'predictedScenePx' in point:
            end_x, end_y = point['predictedScenePx']
            end_x, end_y = end_x - left + 0.5, end_y - top + 0.5
            content.append(f'<g class="estimate"><path d="M{center_x} {center_y} L{end_x} {end_y}"/>'
                           f'<path d="M{end_x-radius} {end_y-radius} l{2*radius} {2*radius} '
                           f'M{end_x-radius} {end_y+radius} l{2*radius} {-2*radius}"/></g>')
        style = 'check' if 'predictedScenePx' in point else 'control'
        content.append(f'<circle class="{style}" cx="{center_x}" cy="{center_y}" r="{radius}"/>')
        if not detail:
            content.append(f'<text x="{center_x+5}" y="{center_y-5}">{escape(point["id"])}</text>')
    return ''.join(content) + '</svg>'


def render(spec, report, satellite, scene):
    points = spec['controls'] + report['checks']

    def overview(image, coordinates):
        horizontal, vertical = zip(*(point[coordinates] for point in points))
        bounds = min(horizontal)-28, min(vertical)-22, max(horizontal)+28, max(vertical)+22
        return panel(image, bounds, points, coordinates)

    cards = []
    for point in report['checks']:
        center_x, center_y = point['scenePx']
        zoom = panel(scene, (center_x-24, center_y-16, center_x+25, center_y+17), [point], 'scenePx', True)
        delta_x, delta_y = point['deltaScenePx']
        cards.append(f'<figure><figcaption>{escape(point["id"])} · {escape(point["label"])}</figcaption>{zoom}'
                     f'<p><b>{point["equivalentMeters"]:.1f} 米</b><br>图上偏移 Δx {delta_x:+.1f}、'
                     f'Δy {delta_y:+.1f} 像素</p></figure>')
    template = Template(Path(__file__).with_name('location-registration-review.html').read_text())
    return template.substitute(region=escape(report['region']), rms=f'{report["checkRmsMeters"]:.1f}',
                               maximum=f'{report["checkMaxMeters"]:.1f}', checks=''.join(cards),
                               satellite=overview(satellite, 'satellitePx'), scene=overview(scene, 'scenePx'))


def main():
    spec = json.loads(SPEC.read_text())
    world = [float(value) for value in (ROOT / spec['worldFile']).read_text().splitlines()]
    report = audit(spec, world)
    with Image.open(ROOT / spec['satellite']) as satellite, Image.open(ROOT / spec['scene']) as scene:
        if satellite.size != (1400, 1200) or scene.size != (1520, 1240):
            raise ValueError('Registration requires the original raster and final illustration dimensions')
        html = render(spec, report, satellite, scene)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'review.html').write_text(html, encoding='utf-8')
    (OUTPUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{OUTPUT / "review.html"}\nHeld-out checks: RMS {report["checkRmsMeters"]:.3f} m, '
          f'max {report["checkMaxMeters"]:.3f} m (image registration, not device accuracy)')


if __name__ == '__main__':
    main()
