import registration from '../data/illustration-registration.json' with { type: 'json' }
import { mercator, type GeographicFix } from './geography.ts'

type Point = readonly number[]
interface CoverageGuard {
  hull: readonly Point[]
  controls: readonly Point[]
}
export interface IllustrationRegistration extends CoverageGuard {
  kind: string
  world: Point
  targets: readonly Point[]
  triangles: readonly Point[]
  exclusionSites: readonly Point[]
  supportPx: number
  registrationAllowanceM: number
  imageryAllowanceM: number
  coverageGuard?: CoverageGuard
}
export interface IllustratedPosition {
  x: number
  y: number
  radius: number
  basis: readonly Point[]
}

export function illustratedBearing(position: IllustratedPosition, heading: number) {
  const radians = (heading * Math.PI) / 180
  const [dx, dy] = position.basis.map(
    ([east, south]) => east * Math.sin(radians) - south * Math.cos(radians),
  )
  return ((Math.atan2(dx, -dy) * 180) / Math.PI + 360) % 360
}

function cross(start: Point, end: Point, point: Point) {
  return (end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (point[0] - start[0])
}

export function createIllustrationProjector(registration: IllustrationRegistration) {
  if (registration.kind !== 'mesh')
    throw new Error('Illustrated positioning requires a triangle mesh')
  const triangles = registration.triangles.map((indices) => {
    const source = indices.map((index) => registration.controls[index])
    const target = indices.map((index) => registration.targets[index])
    const [first, second, third] = source
    const area = cross(first, second, third)
    const rows = [0, 1].map((axis) => {
      const firstDelta = target[1][axis] - target[0][axis]
      const secondDelta = target[2][axis] - target[0][axis]
      return [
        (firstDelta * (third[1] - first[1]) - secondDelta * (second[1] - first[1])) / area,
        (secondDelta * (second[0] - first[0]) - firstDelta * (third[0] - first[0])) / area,
      ]
    })
    const squared = rows.flat().reduce((total, value) => total + value * value, 0)
    const determinant = cross(target[0], target[1], target[2]) / area
    const stretch = Math.sqrt(
      (squared + Math.sqrt(Math.max(0, squared ** 2 - 4 * determinant ** 2))) / 2,
    )
    return { source, target, area, stretch, rows }
  })

  return function project(fix: GeographicFix): IllustratedPosition | null {
    if (!Number.isFinite(fix.accuracy) || fix.accuracy < 0 || fix.accuracy > 50) return null
    const [east, north] = mercator([fix.longitude, fix.latitude])
    const [eastStep, , , northStep, originEast, originNorth] = registration.world
    const pixel = [(east - originEast) / eastStep, (north - originNorth) / northStep]
    const metersPerPixel = eastStep * Math.cos((fix.latitude * Math.PI) / 180)
    const margin = (fix.accuracy + registration.imageryAllowanceM) / metersPerPixel
    const distance = (site: Point) => Math.hypot(pixel[0] - site[0], pixel[1] - site[1])
    const coverage = registration.coverageGuard
      ? [registration, registration.coverageGuard]
      : [registration]
    if (
      coverage.some(
        (area) =>
          area.hull.some((start, index, hull) => {
            const end = hull[(index + 1) % hull.length]
            return (
              cross(start, end, pixel) < margin * Math.hypot(end[0] - start[0], end[1] - start[1])
            )
          }) || !area.controls.some((site) => distance(site) + margin <= registration.supportPx),
      ) ||
      registration.exclusionSites.some((site) => distance(site) <= registration.supportPx + margin)
    )
      return null

    const radius = margin + registration.registrationAllowanceM / metersPerPixel
    let center: Omit<IllustratedPosition, 'radius'> | undefined
    let maxStretch = 0
    for (const { source, target, area, stretch, rows } of triangles) {
      if (
        [0, 1].some(
          (axis) =>
            source.every((site) => site[axis] < pixel[axis] - radius) ||
            source.every((site) => site[axis] > pixel[axis] + radius),
        )
      )
        continue
      maxStretch = Math.max(maxStretch, stretch)
      const weights = source.map(
        (_, index) => cross(source[(index + 1) % 3], source[(index + 2) % 3], pixel) / area,
      )
      if (!center && weights.every((weight) => weight >= -1e-9)) {
        const sum = (axis: number) =>
          weights.reduce((total, weight, index) => total + weight * target[index][axis], 0)
        center = { x: sum(0), y: sum(1), basis: rows }
      }
    }
    return center ? { ...center, radius: radius * maxStretch } : null
  }
}

export const projectIllustratedFix = createIllustrationProjector(registration)
