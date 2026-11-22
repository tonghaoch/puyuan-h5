import { shallowRef, watch } from 'vue'
import { publicAsset } from './public-asset'
import type { GeoCollection, LngLat } from './geography'

export function useParkBoundary(hasFix: () => boolean, overviewOpen: () => boolean) {
  const ring = shallowRef<LngLat[]>([])
  const error = shallowRef(false)
  watch(
    [hasFix, overviewOpen],
    async ([fix, open], _, cleanup) => {
      if ((!fix && !open) || ring.value.length) return
      const controller = new AbortController()
      cleanup(() => controller.abort())
      error.value = false
      try {
        const response = await fetch(publicAsset('/geodata/boundary.geojson'), {
          signal: controller.signal,
        })
        if (!response.ok) throw new Error('Map data unavailable')
        const geometry = ((await response.json()) as GeoCollection).features?.[0]?.geometry
        if (geometry?.type !== 'Polygon' || !(geometry.coordinates[0]?.length >= 3))
          throw new Error('Invalid park boundary')
        if (!controller.signal.aborted) ring.value = geometry.coordinates[0]
      } catch {
        if (!controller.signal.aborted) error.value = true
      }
    },
    { immediate: true },
  )
  return { ring, error }
}
