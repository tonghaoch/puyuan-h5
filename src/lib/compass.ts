import { ref, watch } from 'vue'
import { deviceBearing, type CompassSample } from './device-bearing'

export type CompassPermission = 'prompt' | 'requesting' | 'denied' | 'unsupported' | 'ready'

export function useCompass(active: () => boolean) {
  const sensor = window.DeviceOrientationEvent as
    | (typeof DeviceOrientationEvent & {
        requestPermission?: (absolute?: boolean) => Promise<PermissionState>
      })
    | undefined
  const permission = ref<CompassPermission>(
    !window.isSecureContext || !sensor
      ? 'unsupported'
      : sensor.requestPermission
        ? 'prompt'
        : 'ready',
  )
  const heading = ref<number | null>(null)

  async function enable() {
    if (!active() || permission.value !== 'prompt' || !sensor?.requestPermission) return
    permission.value = 'requesting'
    try {
      permission.value = (await sensor.requestPermission(true)) === 'granted' ? 'ready' : 'denied'
    } catch {
      permission.value = 'denied'
    }
  }

  watch(
    () => active() && permission.value === 'ready',
    (enabled, _, cleanup) => {
      if (!enabled) return
      let latest: CompassSample | undefined
      let expiry: number | undefined
      const angle = () => window.screen.orientation?.angle ?? window.orientation ?? 0
      function update(next: number | null) {
        const previous = heading.value
        if (
          next === null ||
          previous === null ||
          Math.abs(((next - previous + 540) % 360) - 180) >= 2
        )
          heading.value = next
      }
      function reset() {
        latest = undefined
        heading.value = null
        window.clearTimeout(expiry)
      }
      function receive(event: Event) {
        const sample = event as DeviceOrientationEvent
        const next = deviceBearing(sample, angle())
        if (next === undefined) return
        window.clearTimeout(expiry)
        latest = sample
        update(next)
        expiry = window.setTimeout(reset, 20_000)
      }
      function rotate() {
        if (latest) update(deviceBearing(latest, angle()) ?? null)
      }
      window.addEventListener('deviceorientationabsolute', receive)
      window.addEventListener('deviceorientation', receive)
      window.screen.orientation?.addEventListener('change', rotate)
      window.addEventListener('orientationchange', rotate)
      cleanup(() => {
        window.removeEventListener('deviceorientationabsolute', receive)
        window.removeEventListener('deviceorientation', receive)
        window.screen.orientation?.removeEventListener('change', rotate)
        window.removeEventListener('orientationchange', rotate)
        reset()
      })
    },
    { immediate: true },
  )
  return { heading, permission, enable }
}
