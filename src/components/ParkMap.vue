<script setup lang="ts">
import { t } from '../i18n'
import { publicAsset } from '../lib/public-asset'
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import type { MapLayer, Place } from '../data/catalog'
import { clampCamera, zoomAt, zoomRange, SCENE, type Camera } from '../lib/map-camera'
import ReferenceTiles from './ReferenceTiles.vue'
import referenceMap from '../data/reference-map.json'
import ReferenceLabels from './ReferenceLabels.vue'
import QuestToken from './QuestToken.vue'
import EncounterToken from './EncounterToken.vue'
import AppIcon from './AppIcon.vue'
import { quests, wanderers } from '../data/offsite'
// Start point and bearing in the original painting's coordinate system.
const boatRoutes = [
  [1040, 895, -12],
  [1094, 356, 30],
  [1190, 1100, 80],
  [662, 476, 0],
  [982, 440, 160],
  [1302, 836, 130],
  [790, 752, 80],
  [1398, 464, 70],
] as const
const props = defineProps<{
  places: Place[]
  focusRequest: { id: string; nonce: number } | null
  layers: Record<MapLayer, boolean>
  motion: boolean
  activeQuestId?: string
  activeNpcId?: string
}>()
const emit = defineEmits<{
  select: [place: Place]
  locate: []
  zoom: [value: number]
  game: [id: string, opener: HTMLElement]
  npc: [id: string, opener: HTMLElement]
}>()
const pins = [
  ...quests.map(({ id, place, name, point }) => ({
    kind: 'quest' as const,
    key: `quest:${id}`,
    id,
    place,
    name,
    point,
  })),
  ...wanderers.flatMap((npc) =>
    npc.point
      ? [
          {
            kind: 'npc' as const,
            key: `npc:${npc.id}`,
            id: npc.id,
            name: npc.name,
            point: npc.point,
            area: npc.area,
          },
        ]
      : [],
  ),
]
const fieldMarkers = computed(() => pins.filter((pin) => props.layers[pin.kind]))
function openPin(pin: (typeof pins)[number], event: MouseEvent) {
  const opener = event.currentTarget as HTMLElement
  if (pin.kind === 'quest') emit('game', pin.id, opener)
  else emit('npc', pin.id, opener)
}
const viewport = ref<HTMLElement>()
const camera = reactive<Camera>({ x: 0, y: 0, scale: 0.6 })
const dimensions = reactive({ width: 0, height: 0 })
const limits = computed(() => zoomRange(dimensions.width, dimensions.height))
const atMaxZoom = computed(() => camera.scale >= limits.value.max - 1e-9)
const dragging = ref(false)
const ready = ref(false)
const pointers = new Map<number, { x: number; y: number }>()
let observer: ResizeObserver | undefined
let suppressClick = false
let dragDistance = 0
const style = computed(() => ({
  transform: `translate3d(${camera.x}px, ${camera.y}px, 0) scale(${camera.scale})`,
  '--inverse-scale': 1 / camera.scale,
  '--field-scale': 1 / limits.value.initial,
}))
const meadowStyle = computed(() => ({
  backgroundSize: `${384 * camera.scale}px ${384 * camera.scale}px`,
  backgroundPosition: `${camera.x}px ${camera.y}px`,
}))
function setCamera(value: Camera) {
  Object.assign(camera, clampCamera(value, dimensions.width, dimensions.height))
  emit('zoom', camera.scale)
}
function reset() {
  const { width, height } = dimensions
  const scale = limits.value.initial
  setCamera({ scale, x: width / 2 - 850 * scale, y: (height + 5) / 2 - 605 * scale })
}
function changeZoom(factor: number) {
  setCamera(
    zoomAt(
      camera,
      factor,
      dimensions.width / 2,
      dimensions.height / 2,
      dimensions.width,
      dimensions.height,
    ),
  )
}
function guardClick(event: MouseEvent) {
  if (suppressClick) {
    event.preventDefault()
    event.stopPropagation()
    suppressClick = false
  }
}
function focus(point: Place['point']) {
  const scale = Math.max(camera.scale, 0.83)
  setCamera({
    scale,
    x: dimensions.width / 2 - point.x * scale,
    y: dimensions.height * 0.45 - point.y * scale,
  })
}
function applyFocus(request: typeof props.focusRequest) {
  if (!request || !ready.value) return
  const place = props.places.find((p) => p.id === request?.id)
  if (place) focus(place.point)
  const pin = pins.find((item) => item.key === request.id)
  if (pin) focus({ x: pin.point[0], y: pin.point[1] })
}
watch(() => props.focusRequest, applyFocus, { flush: 'post' })
function down(event: PointerEvent) {
  if (pointers.size === 0) {
    suppressClick = false
    dragDistance = 0
  }
  const button = (event.target as Element).closest('button')
  if ((button && !button.classList.contains('field-pin')) || event.button > 0) return
  // Keep taps on the flag, but allow a drag starting on it to pan the map.
  const captureTarget = button ?? viewport.value
  captureTarget?.setPointerCapture(event.pointerId)
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })
  dragging.value = true
}
function move(event: PointerEvent) {
  const old = pointers.get(event.pointerId)
  if (!old) return
  dragDistance += Math.hypot(event.clientX - old.x, event.clientY - old.y)
  if (dragDistance > 6 || pointers.size > 1) suppressClick = true
  const previous = [...pointers.values()]
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })
  if (pointers.size === 1)
    setCamera({
      ...camera,
      x: camera.x + event.clientX - old.x,
      y: camera.y + event.clientY - old.y,
    })
  else {
    const next = [...pointers.values()]
    const a = previous[0]!,
      b = previous[1]!,
      c = next[0]!,
      d = next[1]!
    const oldDistance = Math.hypot(a.x - b.x, a.y - b.y)
    if (oldDistance < 2) return
    const bounds = viewport.value!.getBoundingClientRect()
    const midX = (a.x + b.x) / 2 - bounds.left,
      midY = (a.y + b.y) / 2 - bounds.top
    const result = zoomAt(
      camera,
      Math.hypot(c.x - d.x, c.y - d.y) / oldDistance,
      midX,
      midY,
      dimensions.width,
      dimensions.height,
    )
    result.x += (c.x + d.x - a.x - b.x) / 2
    result.y += (c.y + d.y - a.y - b.y) / 2
    setCamera(result)
  }
}
function up(event: PointerEvent) {
  pointers.delete(event.pointerId)
  dragging.value = pointers.size > 0
  if (viewport.value?.hasPointerCapture(event.pointerId))
    viewport.value.releasePointerCapture(event.pointerId)
}
function wheel(event: WheelEvent) {
  const bounds = viewport.value!.getBoundingClientRect()
  setCamera(
    zoomAt(
      camera,
      Math.exp(-event.deltaY * 0.0015),
      event.clientX - bounds.left,
      event.clientY - bounds.top,
      dimensions.width,
      dimensions.height,
    ),
  )
}
function keyboard(event: KeyboardEvent) {
  if (event.target !== viewport.value) return
  const actions: Record<string, () => void> = {
    ArrowLeft: () => setCamera({ ...camera, x: camera.x + 70 }),
    ArrowRight: () => setCamera({ ...camera, x: camera.x - 70 }),
    ArrowUp: () => setCamera({ ...camera, y: camera.y + 70 }),
    ArrowDown: () => setCamera({ ...camera, y: camera.y - 70 }),
    '+': () => changeZoom(1.2),
    '=': () => changeZoom(1.2),
    '-': () => changeZoom(1 / 1.2),
    Home: reset,
  }
  if (actions[event.key]) {
    event.preventDefault()
    actions[event.key]!()
  }
}
onMounted(() => {
  observer = new ResizeObserver((entries) => {
    const rect = entries[0]!.contentRect
    if (rect.width <= 0 || rect.height <= 0) return
    const dx = rect.width - dimensions.width,
      dy = rect.height - dimensions.height
    dimensions.width = rect.width
    dimensions.height = rect.height
    if (!ready.value) {
      reset()
      ready.value = true
      applyFocus(props.focusRequest)
    } else setCamera({ ...camera, x: camera.x + dx / 2, y: camera.y + dy / 2 })
  })
  observer.observe(viewport.value!)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div
    ref="viewport"
    class="map-viewport has-meadow"
    :class="{
      dragging,
      'motion-paused': !motion,
      'compact-pins': camera.scale < 0.58,
    }"
    role="region"
    :aria-label="t('古镇导览，可拖动缩放')"
    tabindex="0"
    @click.capture="guardClick"
    @pointerdown="down"
    @pointermove="move"
    @pointerup="up"
    @pointercancel="up"
    @lostpointercapture="up"
    @wheel.prevent="wheel"
    @keydown="keyboard"
    @dblclick="changeZoom(1.3)"
  >
    <div class="meadow-backdrop" :style="meadowStyle" aria-hidden="true"></div>
    <div class="map-scene" :style="style">
      <img
        class="map-art"
        :src="publicAsset('/art/puyuan-original-scope.webp')"
        :alt="t('原始参考地图')"
        :width="SCENE.width"
        :height="SCENE.height"
        draggable="false"
        fetchpriority="high"
      />
      <ReferenceTiles
        :at-max-zoom="atMaxZoom"
        :camera="camera"
        :width="dimensions.width"
        :height="dimensions.height"
      />
      <div class="map-water-mask" aria-hidden="true">
        <svg class="map-effects" :width="SCENE.width" :height="SCENE.height">
          <defs>
            <pattern id="guide-ripples" width="70" height="43" patternUnits="userSpaceOnUse">
              <path class="canal-ripple" d="M-5 12q14 -5 30 -1t28 -2 M28 33q12 -4 29 -1t19 -1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#guide-ripples)" />
          <g
            :transform="`translate(${referenceMap.sourceOffset.x} ${referenceMap.sourceOffset.y})`"
          >
            <path
              v-for="d in referenceMap.waterAnimations"
              :key="d"
              :d="d"
              class="water-highlight"
            />
            <path d="M1028 897 Q1090 886 1165 870" class="water-highlight" />
            <g
              v-for="([x, y, bearing], i) in boatRoutes"
              :key="x"
              :transform="`translate(${x} ${y}) rotate(${bearing})`"
            >
              <g
                class="guide-boat"
                :style="{ animationDuration: `${11 + (i % 4)}s`, animationDelay: `${-2 - i}s` }"
              >
                <g :transform="`scale(${Math.max(1, Math.min(2.5, 0.85 / camera.scale))})`">
                  <path
                    d="M-12 -2q-5 -3 -12 -3m12 7q-6 3 -12 3"
                    fill="none"
                    stroke="#fff4d9"
                    stroke-width="1.4"
                  />
                  <image
                    :href="publicAsset(i % 2 ? '/art/boat-covered.webp' : '/art/boat-bamboo.webp')"
                    x="-15"
                    y="-13"
                    width="30"
                    height="21"
                    :transform="`rotate(${-bearing}) scale(${bearing > 90 ? -1 : 1} 1)`"
                  />
                </g>
              </g>
            </g>
          </g>
        </svg>
      </div>
      <ReferenceLabels v-if="layers.places" :places="places" @select="emit('select', $event)" />
      <div class="field-markers">
        <div
          v-for="pin in fieldMarkers"
          :key="pin.key"
          class="field-marker"
          :data-marker="pin.key"
          :class="{
            'npc-marker': pin.kind === 'npc',
            'pin-selected': pin.kind === 'npc' ? activeNpcId === pin.id : activeQuestId === pin.id,
          }"
          :style="{ left: `${pin.point[0]}px`, top: `${pin.point[1]}px` }"
        >
          <svg class="marker-leader" width="1" height="1" aria-hidden="true">
            <line y2="-4" />
            <circle r="2.3" />
          </svg>
          <button
            class="field-pin"
            :class="pin.kind === 'npc' ? 'npc-pin' : 'quest-pin'"
            :aria-label="
              pin.kind === 'quest'
                ? t('游戏：{place} · {name}', { place: pin.place, name: pin.name })
                : t('游走 NPC：{name} · {area}', { name: pin.name, area: pin.area })
            "
            :title="t(pin.name)"
            aria-haspopup="dialog"
            @click.stop="openPin(pin, $event)"
            @dblclick.stop
          >
            <QuestToken v-if="pin.kind === 'quest'" /><EncounterToken v-else />
            <span v-if="camera.scale >= 0.8" class="marker-name">{{ t(pin.name) }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
  <button
    type="button"
    class="locate-tool"
    :aria-label="t('获取我的位置')"
    :title="t('获取我的位置')"
    aria-haspopup="dialog"
    @click="emit('locate')"
  >
    <AppIcon name="locate" :size="22" />
  </button>
</template>
