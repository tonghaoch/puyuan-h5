export type LngLat = readonly [number, number]
export type XY = readonly [number, number]
export interface GeoFeature {
  type: 'Feature'
  id?: string
  properties: Record<string, unknown>
  geometry:
    | { type: 'Polygon'; coordinates: LngLat[][] }
    | { type: 'LineString'; coordinates: LngLat[] }
    | { type: 'Point'; coordinates: LngLat }
}
export interface GeoCollection {
  type: 'FeatureCollection'
  features: GeoFeature[]
}
export interface GeographicFix {
  longitude: number
  latitude: number
  accuracy: number
  timestamp: number
}
const RADIUS = 6378137
export const FIX_LIFETIME_MS = 60000
export function mercator([longitude, latitude]: LngLat): XY {
  const clamped = Math.max(-85.05112878, Math.min(85.05112878, latitude))
  return [
    (RADIUS * longitude * Math.PI) / 180,
    RADIUS * Math.log(Math.tan(Math.PI / 4 + (clamped * Math.PI) / 360)),
  ]
}
export function pointInRing(point: LngLat, ring: readonly LngLat[]): boolean {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i]!,
      b = ring[j]!
    if (
      a[1] > point[1] !== b[1] > point[1] &&
      point[0] < ((b[0] - a[0]) * (point[1] - a[1])) / (b[1] - a[1]) + a[0]
    )
      inside = !inside
  }
  return inside
}
function distanceToSegment(point: XY, a: XY, b: XY): number {
  const dx = b[0] - a[0],
    dy = b[1] - a[1]
  const length = dx * dx + dy * dy
  const t = length
    ? Math.max(0, Math.min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length))
    : 0
  return Math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)
}
/** Local Mercator distance corrected for latitude; suitable for this small park, not navigation. */
export function classifyFix(
  fix: GeographicFix,
  ring: readonly LngLat[],
  now = Date.now(),
): 'inside' | 'outside' | 'uncertain' | 'stale' {
  if (now - fix.timestamp >= FIX_LIFETIME_MS) return 'stale'
  if (!Number.isFinite(fix.accuracy) || fix.accuracy < 0 || ring.length < 3) return 'uncertain'
  const coordinate: LngLat = [fix.longitude, fix.latitude]
  const projected = mercator(coordinate)
  const latitudeCorrection = Math.cos((fix.latitude * Math.PI) / 180)
  let distance = Infinity
  for (let i = 0; i < ring.length; i++)
    distance = Math.min(
      distance,
      distanceToSegment(projected, mercator(ring[i]!), mercator(ring[(i + 1) % ring.length]!)) *
        latitudeCorrection,
    )
  if (distance <= fix.accuracy) return 'uncertain'
  return pointInRing(coordinate, ring) ? 'inside' : 'outside'
}
export function createGeoFrame(ring: readonly LngLat[], width = 400, height = 260, padding = 22) {
  const projected = ring.map(mercator)
  const xs = projected.map((p) => p[0]),
    ys = projected.map((p) => p[1])
  const minX = Math.min(...xs),
    maxX = Math.max(...xs),
    minY = Math.min(...ys),
    maxY = Math.max(...ys)
  const scale = Math.min(
    (width - padding * 2) / Math.max(1, maxX - minX),
    (height - padding * 2) / Math.max(1, maxY - minY),
  )
  const offsetX = (width - (maxX - minX) * scale) / 2,
    offsetY = (height - (maxY - minY) * scale) / 2
  const projectMeters = (point: XY): XY => [
    offsetX + (point[0] - minX) * scale,
    offsetY + (maxY - point[1]) * scale,
  ]
  const project = (point: LngLat): XY => projectMeters(mercator(point))
  return { project, projectMeters, scale, width, height }
}
