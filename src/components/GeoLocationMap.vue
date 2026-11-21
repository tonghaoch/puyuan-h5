<script setup lang="ts">
import { t } from '../i18n'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  classifyFix,
  createGeoFrame,
  type GeographicFix,
  type GeoCollection,
  type LngLat,
} from '../lib/geography'
const props = defineProps<{ fix: GeographicFix | null; now: number }>()
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
    const response = await fetch('/geodata/boundary.geojson', { signal: controller.signal })
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
  <div class="geo-overview">
    <div class="geo-overview-title">
      <span>{{ t('位置概览') }}</span
      ><small>{{ t('真实地理坐标') }}</small>
    </div>
    <p v-if="error" class="geo-loading">{{ t('地理概览暂时无法加载，仍可浏览古镇示意图。') }}</p>
    <p v-else-if="!frame" class="geo-loading" role="status">{{ t('正在加载园区位置…') }}</p>
    <template v-else>
      <svg
        class="geo-map"
        viewBox="0 0 400 260"
        role="img"
        :aria-label="t('濮院时尚古镇园区边界。{message}', { message })"
      >
        <rect width="400" height="260" fill="#eeeedf" />
        <path :d="boundaryPath" class="geo-boundary" />
        <text x="378" y="22" class="geo-north" text-anchor="middle">{{ t('北 ↑') }}</text>
        <g
          v-if="positionVisible && position"
          class="geo-user"
          :class="{ stale: status === 'stale' }"
          :transform="`translate(${position[0]},${position[1]})`"
        >
          <circle :r="accuracyRadius" class="geo-accuracy" />
          <circle r="7" class="geo-position" />
          <rect x="-28" y="12" width="56" height="20" rx="4" fill="#fbf9ed" />
          <text y="26" text-anchor="middle" class="geo-user-label">{{ t('我的位置') }}</text>
        </g>
      </svg>
      <p class="geo-message" role="status">{{ t(message) }}</p>
      <p class="geo-source">
        <a
          href="https://www.openstreetmap.org/copyright"
          target="_blank"
          rel="noopener noreferrer"
          >{{ t('© OpenStreetMap contributors') }}</a><span>{{ t('公开边界供位置参考') }}</span>
      </p>
    </template>
  </div>
</template>
