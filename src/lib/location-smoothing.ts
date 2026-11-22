import type { GeographicFix } from './geography.ts'

const RADIUS = 6378137
const radians = Math.PI / 180
const WINDOW_MS = 2500
const MAX_ADJUSTMENT_M = 3
const RESET_DISTANCE_M = 12

function longitudeDelta(a: number, b: number) {
  return ((a - b + 540) % 360) - 180
}

export function fixDistance(a: GeographicFix, b: GeographicFix) {
  const latitude = ((a.latitude - b.latitude) * radians) / 2
  const longitude = (longitudeDelta(a.longitude, b.longitude) * radians) / 2
  const half =
    Math.sin(latitude) ** 2 +
    Math.cos(a.latitude * radians) * Math.cos(b.latitude * radians) * Math.sin(longitude) ** 2
  return 2 * RADIUS * Math.asin(Math.sqrt(Math.min(1, half)))
}

/** Short-lived device samples only; reported uncertainty is never reduced. */
export function createLocationSmoother() {
  let samples: GeographicFix[] = []
  let estimate: GeographicFix | null = null

  function reset() {
    samples = []
    estimate = null
  }

  function update(fix: GeographicFix): GeographicFix {
    const previous = samples.at(-1)
    if (previous && fix.timestamp <= previous.timestamp) return estimate!
    if (
      previous &&
      (fix.timestamp - previous.timestamp > WINDOW_MS ||
        fixDistance(fix, previous) > RESET_DISTANCE_M)
    )
      reset()
    samples = [...samples.filter((sample) => fix.timestamp - sample.timestamp <= WINDOW_MS), fix]
      .slice(-5)
      .map((sample) => ({ ...sample }))
    const weighted = samples.map((sample) => ({
      sample,
      weight:
        Math.exp((sample.timestamp - fix.timestamp) / 1000) / Math.max(3, sample.accuracy) ** 2,
    }))
    const total = weighted.reduce((sum, item) => sum + item.weight, 0)
    const latitude =
      weighted.reduce((sum, { sample, weight }) => sum + sample.latitude * weight, 0) / total
    const delta =
      weighted.reduce(
        (sum, { sample, weight }) => sum + longitudeDelta(sample.longitude, fix.longitude) * weight,
        0,
      ) / total
    const candidate = {
      ...fix,
      longitude: longitudeDelta(fix.longitude + delta, 0),
      latitude,
    }
    const distance = fixDistance(candidate, fix)
    const fraction = distance > MAX_ADJUSTMENT_M ? MAX_ADJUSTMENT_M / distance : 1
    estimate = {
      ...fix,
      longitude: longitudeDelta(fix.longitude + delta * fraction, 0),
      latitude: fix.latitude + (latitude - fix.latitude) * fraction,
      // A displaced estimate must still contain the current device's reported confidence region.
      accuracy: fix.accuracy + Math.min(distance, MAX_ADJUSTMENT_M),
    }
    return { ...estimate }
  }

  return { update, reset }
}
