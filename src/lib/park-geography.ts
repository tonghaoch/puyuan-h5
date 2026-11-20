import { computed, onMounted, ref } from 'vue'
import { createGeoFrame, type GeoCollection, type GeoFeature, type LngLat } from './geography'
import { SCENE } from './map-camera'

export type MapView = 'illustration' | 'reference' | 'geographic'
let geometryRequest: Promise<GeoCollection> | undefined
async function getGeometry(): Promise<GeoCollection> {
  const response = await fetch('/geodata/puyuan.geojson')
  if (!response.ok) throw new Error('暂时无法加载地理资料')
  const result = (await response.json()) as GeoCollection
  if (result.type !== 'FeatureCollection' || !Array.isArray(result.features))
    throw new Error('地理资料格式异常')
  return result
}
export function useParkGeography() {
  const data = ref<GeoCollection | null>(null)
  const error = ref('')
  const ring = computed(() => {
    const boundary = data.value?.features.find((f) => f.properties.layer === 'boundary')
    return boundary?.geometry.type === 'Polygon' ? (boundary.geometry.coordinates[0] ?? []) : []
  })
  const frame = computed(() =>
    ring.value.length >= 3 ? createGeoFrame(ring.value, SCENE.width, SCENE.height, 100) : null,
  )
  function path(coordinates: LngLat[]) {
    return coordinates
      .map((coordinate, i) => {
        const [x, y] = frame.value!.project(coordinate)
        return `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ')
  }
  const shapes = computed(() =>
    !frame.value
      ? []
      : data.value!.features.flatMap((feature) => {
          if (feature.geometry.type === 'Point') return []
          const d =
            feature.geometry.type === 'Polygon'
              ? feature.geometry.coordinates.map((r) => path(r) + 'Z').join(' ')
              : path(feature.geometry.coordinates)
          return [
            {
              d,
              layer: String(feature.properties.layer),
              bridge: feature.properties.bridge === 'yes',
              name: String(feature.properties.name || ''),
            },
          ]
        }),
  )
  const points = computed(() =>
    !frame.value
      ? []
      : data.value!.features.flatMap((feature) => {
          if (feature.geometry.type !== 'Point') return []
          const [x, y] = frame.value!.project(feature.geometry.coordinates)
          return [{ feature, point: { x, y }, name: String(feature.properties.name || '地图地点') }]
        }),
  )
  async function load() {
    error.value = ''
    try {
      geometryRequest ??= getGeometry()
      data.value = await geometryRequest
      if (!frame.value) throw new Error('缺少园区边界')
    } catch (reason) {
      geometryRequest = undefined
      error.value = reason instanceof Error ? reason.message : '地理地图暂时不可用'
    }
  }
  onMounted(load)
  return { ring, frame, shapes, points, error, reload: load }
}
export function isGeographicView(view: MapView) {
  return view === 'geographic'
}
export function geoName(feature: GeoFeature) {
  return String(feature.properties.name || '地图地点')
}
