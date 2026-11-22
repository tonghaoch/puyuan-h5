export type CompassSample = Pick<
  DeviceOrientationEvent,
  'type' | 'absolute' | 'alpha' | 'beta' | 'gamma'
> & {
  webkitCompassHeading?: number
  webkitCompassAccuracy?: number
}

const radians = Math.PI / 180
const degrees = (value: number) => ((value % 360) + 360) % 360
const finite = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value)

export function deviceBearing(
  sample: CompassSample,
  screenAngle: number,
): number | null | undefined {
  const native = sample.webkitCompassHeading
  const hasNative = native !== undefined
  if (!hasNative && !sample.absolute && sample.type !== 'deviceorientationabsolute')
    return undefined
  if (!Number.isFinite(screenAngle)) return null
  const accuracy = sample.webkitCompassAccuracy
  if (
    hasNative &&
    (!finite(native) ||
      native < 0 ||
      native >= 360 ||
      (accuracy !== undefined && (!finite(accuracy) || accuracy < 0 || accuracy > 45)))
  )
    return null
  if (!hasNative && (!finite(sample.alpha) || !finite(sample.beta) || !finite(sample.gamma)))
    return null

  const beta = (sample.beta ?? 0) * radians
  const gamma = (sample.gamma ?? 0) * radians
  const right = Math.sin(screenAngle * radians)
  const top = Math.cos(screenAngle * radians)
  const east = right * Math.cos(gamma)
  const north = top * Math.cos(beta) + right * Math.sin(beta) * Math.sin(gamma)
  if (!finite(east) || !finite(north) || Math.hypot(east, north) < 0.2) return null
  const offset = Math.atan2(east, north) / radians
  if (!hasNative) return degrees(offset - sample.alpha!)
  if (Math.abs(Math.cos(beta)) < 0.2) return null
  return degrees(native + offset - (Math.cos(beta) < 0 ? 180 : 0))
}
