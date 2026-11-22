<script setup lang="ts">
import { t } from '../i18n'
import { computed } from 'vue'
import type { CompassPermission } from '../lib/compass'
import CompassFan from './CompassFan.vue'
import { createGeoFrame, type GeographicFix, type LngLat } from '../lib/geography'
const props = defineProps<{
  fix: GeographicFix | null
  ring: LngLat[]
  error: boolean
  status: 'inside' | 'outside' | 'uncertain' | 'stale' | null
  illustrated: boolean
  heading: number | null
  compassPermission: CompassPermission
  deviceMessage: string
  canRetry: boolean
}>()
defineEmits<{ retry: []; enableCompass: [] }>()
const frame = computed(() => (props.ring.length >= 3 ? createGeoFrame(props.ring) : null))
const boundaryPath = computed(() => {
  const projection = frame.value
  if (!projection) return ''
  return (
    props.ring
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
const message = computed(() => {
  if (!props.fix) return props.deviceMessage
  if (props.error) return '地理概览暂时无法加载，仍可浏览古镇示意图。'
  if (!props.status) return '正在加载园区位置…'
  if (props.status === 'stale') return '这次位置已过期，请重新获取。'
  if (props.status === 'uncertain') return '位置精度范围接近园区边界，暂无法确认是否在园内。'
  if (props.status === 'inside') return '你的位置在公开资料记录的园区范围内。'
  return '你的位置在公开资料记录的园区范围外。'
})
</script>
<template>
  <aside class="geo-overview" :aria-label="t('位置概览')">
    <strong>{{ t('位置概览') }}</strong>
    <p class="geo-message" role="status">{{ t(message) }}</p>
    <small v-if="fix">{{ t('精度约 {meters} 米', { meters: Math.round(fix.accuracy) }) }}</small>
    <button v-if="canRetry" type="button" @click="$emit('retry')">{{ t('手动请求定位') }}</button>
    <template v-if="status === 'inside' && position">
      <small>{{
        t(illustrated ? '手绘图圈出大致位置，不作导航。' : '此处手绘定位依据不足，仅显示园区小图。')
      }}</small>
      <button
        v-if="compassPermission === 'prompt' || compassPermission === 'requesting'"
        type="button"
        :disabled="compassPermission === 'requesting'"
        @click="$emit('enableCompass')"
      >
        {{ t('开启手机朝向') }}
      </button>
      <small v-else-if="heading !== null">{{ t('扇尖指向手机屏幕上沿的方向。') }}</small>
      <small v-else-if="compassPermission === 'denied'">{{
        t('未获朝向权限，仍可查看位置。')
      }}</small>
      <small v-else-if="compassPermission === 'unsupported'">{{
        t('当前环境不支持指南针。')
      }}</small>
      <small v-else>{{ t('暂无可靠朝向，可将手机放平再转动。') }}</small>
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
          <g v-if="heading !== null" transform="scale(1.45)"><CompassFan :bearing="heading" /></g>
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
