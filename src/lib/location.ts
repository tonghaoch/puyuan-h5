import { readonly, ref } from 'vue'
export type LocationState =
  'idle' | 'loading' | 'available' | 'denied' | 'unavailable' | 'timeout' | 'error'
export function useLocation() {
  const state = ref<LocationState>('idle')
  const fix = ref<{
    longitude: number
    latitude: number
    accuracy: number
    timestamp: number
  } | null>(null)
  function locate() {
    if (state.value === 'loading') return
    if (!window.isSecureContext || !navigator.geolocation) {
      state.value = 'unavailable'
      return
    }
    state.value = 'loading'
    navigator.geolocation.getCurrentPosition(
      (position) => {
        fix.value = {
          longitude: position.coords.longitude,
          latitude: position.coords.latitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        }
        state.value = 'available'
      },
      (error) => {
        state.value = error.code === 1 ? 'denied' : error.code === 3 ? 'timeout' : 'error'
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 },
    )
  }
  return { state: readonly(state), fix: readonly(fix), locate }
}
