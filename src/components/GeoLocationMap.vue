<script setup lang="ts">
import { t } from '../i18n'
import { publicAsset } from '../lib/public-asset'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  classifyFix,
  createGeoFrame,
  type GeographicFix,
  type GeoCollection,
  type LngLat,
} from '../lib/geography'
const props = defineProps<{
  fix: GeographicFix | null
  now: number
  deviceMessage: string
  canRetry: boolean
}>()
defineEmits<{ retry: [] }>()
const ring = ref<LngLat[]>([])
const error = ref(false)
const controller = new AbortController()
const frame = computed(() => (ring.value.length >= 3 ? createGeoFrame(ring.value) : null))
const boundaryPath = computed(() => {
  const projection = frame.value
  if (!projection) return ''
  return (
    ring.value
      .map((coordinate, index) => {
        const [x, y] = projection.project(coordinate)
        return `${index ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ') + 'Z'
  )
})
const position = computed(() =>
  props.fix && frame.value ? frame.value.project([props.fix.longitude, props.fix.latitude]) : null,
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
  if (!props.fix) return props.deviceMessage
  if (error.value) return '地理概览暂时无法加载，仍可浏览古镇示意图。'
  if (!status.value) return '正在加载园区位置…'
  if (status.value === 'stale') return '这次位置已过期，请重新获取。'
  if (status.value === 'uncertain') return '位置精度范围接近园区边界，暂无法确认是否在园内。'
  if (status.value === 'inside') return '你的位置在公开资料记录的园区范围内。'
  return '你的位置在公开资料记录的园区范围外。'
})
onMounted(async () => {
  try {
    const response = await fetch(publicAsset('/geodata/boundary.geojson'), {
      signal: controller.signal,
    })
    if (!response.ok) throw new Error('Map data unavailable')
    const result = (await response.json()) as GeoCollection
    if (result.type !== 'FeatureCollection' || !Array.isArray(result.features))
      throw new Error('Invalid map data')
    const geometry = result.features[0]?.geometry
    if (
      geometry?.type !== 'Polygon' ||
      !geometry.coordinates[0] ||
      geometry.coordinates[0].length < 3
    )
      throw new Error('Invalid park boundary')
    ring.value = geometry.coordinates[0]
  } catch {
    if (!controller.signal.aborted) error.value = true
  }
})
onBeforeUnmount(() => controller.abort())
</script>
<template>
  <aside class="geo-overview" :aria-label="t('位置概览')">
    <strong>{{ t('位置概览') }}</strong>
    <p class="geo-message" role="status">{{ t(message) }}</p>
    <small v-if="fix">{{ t('精度约 {meters} 米', { meters: Math.round(fix.accuracy) }) }}</small>
    <button v-if="canRetry" type="button" @click="$emit('retry')">{{ t('手动请求定位') }}</button>
    <template v-if="status === 'inside' && position">
      <svg
        class="geo-map"
        viewBox="0 0 400 260"
        role="img"
        :aria-label="t('濮院时尚古镇园区边界。{message}', { message })"
      >
        <rect width="400" height="260" fill="#eeeedf" />
        <path :d="boundaryPath" class="geo-boundary" />
        <text x="378" y="22" class="geo-north" text-anchor="middle">{{ t('北 ↑') }}</text>
        <g class="geo-user" :transform="`translate(${position[0]},${position[1]})`">
          <circle :r="accuracyRadius" class="geo-accuracy" />
          <circle r="11" class="geo-position" />
        </g>
      </svg>
      <p class="geo-source">
        <a
          href="https://www.openstreetmap.org/copyright"
          target="_blank"
          rel="noopener noreferrer"
          >{{ t('© OpenStreetMap contributors') }}</a
        >
      </p>
    </template>
  </aside>
</template>
