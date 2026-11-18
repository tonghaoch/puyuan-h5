<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  classifyFix,
  createGeoFrame,
  type GeographicFix,
  type GeoCollection,
  type LngLat,
} from '../lib/geography'
const props = defineProps<{ fix: GeographicFix | null; now: number }>()
const data = ref<GeoCollection | null>(null)
const error = ref(false)
const controller = new AbortController()
const boundary = computed(() => data.value?.features.find((f) => f.properties.layer === 'boundary'))
const ring = computed(() =>
  boundary.value?.geometry.type === 'Polygon' ? (boundary.value.geometry.coordinates[0] ?? []) : [],
)
const frame = computed(() => (ring.value.length >= 3 ? createGeoFrame(ring.value) : null))
function linePath(coordinates: LngLat[]) {
  return coordinates
    .map((coordinate, index) => {
      const [x, y] = frame.value!.project(coordinate)
      return `${index ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`
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
            ? feature.geometry.coordinates.map((r) => linePath(r) + 'Z').join(' ')
            : linePath(feature.geometry.coordinates)
        return [{ d, layer: String(feature.properties.layer) }]
      }),
)
const position = computed(() =>
  props.fix && frame.value ? frame.value.project([props.fix.longitude, props.fix.latitude]) : null,
)
const positionVisible = computed(
  () =>
    position.value &&
    position.value[0] >= 8 &&
    position.value[0] <= 392 &&
    position.value[1] >= 8 &&
    position.value[1] <= 252,
)
const accuracyRadius = computed(() =>
  props.fix && frame.value
    ? (Math.max(0, props.fix.accuracy) * frame.value.scale) /
      Math.cos((props.fix.latitude * Math.PI) / 180)
    : 0,
)
const status = computed(() =>
  props.fix && ring.value.length ? classifyFix(props.fix, ring.value, props.now) : null,
)
const message = computed(() => {
  if (!status.value) return '濮院时尚古镇 · 地理位置概览'
  if (status.value === 'stale') return '这次位置已过期，请重新获取。'
  if (status.value === 'uncertain') return '位置精度范围接近园区边界，暂无法确认是否在园内。'
  if (status.value === 'inside') return '你的位置在公开资料记录的园区范围内。'
  return positionVisible.value
    ? '你的位置在公开资料记录的园区范围外。'
    : '你的位置在园区附近视野之外，图中仅展示园区。'
})
onMounted(async () => {
  try {
    const response = await fetch('/geodata/puyuan.geojson', { signal: controller.signal })
    if (!response.ok) throw new Error('Map data unavailable')
    const result = (await response.json()) as GeoCollection
    if (result.type !== 'FeatureCollection' || !Array.isArray(result.features))
      throw new Error('Invalid map data')
    data.value = result
    if (ring.value.length < 3) error.value = true
  } catch {
    if (!controller.signal.aborted) error.value = true
  }
})
onBeforeUnmount(() => controller.abort())
</script>
<template>
  <div class="geo-overview">
    <div class="geo-overview-title"><span>位置概览</span><small>真实地理坐标</small></div>
    <p v-if="error" class="geo-loading">地理概览暂时无法加载，仍可浏览古镇示意图。</p>
    <p v-else-if="!frame" class="geo-loading" role="status">正在加载园区位置…</p>
    <template v-else>
      <svg
        class="geo-map"
        viewBox="0 0 400 260"
        role="img"
        :aria-label="`濮院时尚古镇公开地理地图。${message}`"
      >
        <rect width="400" height="260" fill="#eeeedf" />
        <path
          v-for="(shape, index) in shapes.filter((s) => s.layer === 'boundary')"
          :key="`b-${index}`"
          :d="shape.d"
          class="geo-boundary"
        />
        <path
          v-for="(shape, index) in shapes.filter((s) => s.layer !== 'boundary')"
          :key="index"
          :d="shape.d"
          :class="`geo-${shape.layer}`"
          fill-rule="evenodd"
        />
        <text x="378" y="22" class="geo-north" text-anchor="middle">北 ↑</text>
        <g
          v-if="positionVisible && position"
          class="geo-user"
          :class="{ stale: status === 'stale' }"
          :transform="`translate(${position[0]},${position[1]})`"
        >
          <circle :r="accuracyRadius" class="geo-accuracy" />
          <circle r="7" class="geo-position" />
          <rect x="-28" y="12" width="56" height="20" rx="4" fill="#fbf9ed" />
          <text y="26" text-anchor="middle" class="geo-user-label">我的位置</text>
        </g>
      </svg>
      <p class="geo-message" role="status">{{ message }}</p>
      <p class="geo-source">
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer"
          >© OpenStreetMap contributors</a
        ><span>公开边界供位置参考</span>
      </p>
    </template>
  </div>
</template>
