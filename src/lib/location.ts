import { onBeforeUnmount, onMounted, readonly, ref, watch } from 'vue'
import { FIX_LIFETIME_MS, type GeographicFix } from './geography'

type LocationState =
  'idle' | 'loading' | 'available' | 'denied' | 'unavailable' | 'timeout' | 'error' | 'stale'

export function useLocation(active: () => boolean) {
  const state = ref<LocationState>('idle')
  const fix = ref<GeographicFix | null>(null)
  let watchId: number | undefined
  let generation = 0
  let expiry: number | undefined

  function clearFix() {
    window.clearTimeout(expiry)
    fix.value = null
  }

  function stop() {
    generation++
    if (watchId !== undefined) navigator.geolocation.clearWatch(watchId)
    watchId = undefined
    clearFix()
    if (state.value !== 'denied') state.value = 'idle'
  }

  function start() {
    if (!active()) return
    stop()
    const token = generation
    let newest = -Infinity
    state.value = 'loading'
    try {
      if (!window.isSecureContext || !navigator.geolocation?.watchPosition) {
        state.value = 'unavailable'
        return
      }
      const id = navigator.geolocation.watchPosition(
        ({ coords, timestamp }) => {
          if (token !== generation || timestamp < newest) return
          const { longitude, latitude, accuracy } = coords
          if (
            ![longitude, latitude, accuracy, timestamp].every(Number.isFinite) ||
            Math.abs(longitude) > 180 ||
            Math.abs(latitude) > 90 ||
            accuracy < 0
          ) {
            clearFix()
            state.value = 'error'
            return
          }
          clearFix()
          newest = timestamp
          const remaining = Math.min(FIX_LIFETIME_MS, timestamp + FIX_LIFETIME_MS - Date.now())
          if (remaining <= 0) {
            state.value = 'stale'
            return
          }
          fix.value = { longitude, latitude, accuracy, timestamp }
          state.value = 'available'
          expiry = window.setTimeout(() => {
            fix.value = null
            state.value = 'stale'
          }, remaining)
        },
        ({ code }) => {
          if (token !== generation) return
          if (code === 1) {
            stop()
            state.value = 'denied'
          } else {
            clearFix()
            state.value = code === 3 ? 'timeout' : 'error'
          }
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 },
      )
      if (token === generation) watchId = id
      else navigator.geolocation.clearWatch(id)
    } catch (error) {
      stop()
      state.value =
        error instanceof DOMException && error.name === 'SecurityError' ? 'denied' : 'error'
    }
  }

  onMounted(() =>
    watch(
      active,
      (enabled) => {
        if (!enabled) stop()
        else if (state.value !== 'denied') start()
      },
      { immediate: true, flush: 'sync' },
    ),
  )
  onBeforeUnmount(stop)
  return { state: readonly(state), fix: readonly(fix), retry: start }
}
