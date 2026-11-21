<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import type { Place } from '../data/catalog'
import { clampCamera, zoomAt, zoomRange, ZOOM_STEP, SCENE, type Camera } from '../lib/map-camera'
import ReferenceTiles from './ReferenceTiles.vue'
import referenceMap from '../data/reference-map.json'
import ReferenceLabels from './ReferenceLabels.vue'
import AppIcon from './AppIcon.vue'
import { gameSites, roamingAreas } from '../data/offsite'
import { useParkGeography, isGeographicView, type MapView } from '../lib/park-geography'
import { classifyFix, type GeographicFix, type GeoFeature } from '../lib/geography'
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
  allPlaces: Place[]
  motion: boolean
  view: MapView
  fix: GeographicFix | null
  now: number
  focusLocation: number
}>()
const emit = defineEmits<{
  select: [place: Place]
  locate: []
  zoom: [value: number]
  geoselect: [feature: GeoFeature]
  outside: []
  game: [id: string]
}>()
const geography = useParkGeography()
const geographic = computed(() => isGeographicView(props.view))
const cameraWorld = computed(() =>
  geographic.value ? ('geographic' as const) : ('illustration' as const),
)
const positions = geography.points
const userPosition = computed(() =>
  props.fix && geography.frame.value
    ? geography.frame.value.project([props.fix.longitude, props.fix.latitude])
    : null,
)
const userVisible = computed(
  () =>
    userPosition.value &&
    userPosition.value[0] >= 0 &&
    userPosition.value[0] <= SCENE.width &&
    userPosition.value[1] >= 0 &&
    userPosition.value[1] <= SCENE.height,
)
const roamingName = computed(() =>
  props.focusRequest?.id.startsWith('area:') ? props.focusRequest.id.slice(5) : '',
)
const roamingPoint = computed(() => roamingAreas[roamingName.value])
const userStatus = computed(() =>
  props.fix && geography.ring.value.length
    ? classifyFix(props.fix, geography.ring.value, props.now)
    : null,
)
const accuracyRadius = computed(() =>
  props.fix && geography.frame.value
    ? (Math.max(0, props.fix.accuracy) * geography.frame.value.scale) /
      Math.cos((props.fix.latitude * Math.PI) / 180)
    : 0,
)
const savedCameras = new Map<MapView, Camera>()
const viewport = ref<HTMLElement>()
const camera = reactive<Camera>({ x: 0, y: 0, scale: 0.6 })
const dimensions = reactive({ width: 0, height: 0 })
const limits = computed(() => zoomRange(dimensions.width, dimensions.height))
const atMaxZoom = computed(() => camera.scale >= limits.value.max - 1e-9)
const atMinZoom = computed(() => camera.scale <= limits.value.min + 1e-9)
const dragging = ref(false)
const ready = ref(false)
const pointers = new Map<number, { x: number; y: number }>()
let observer: ResizeObserver | undefined
let suppressClick = false
let dragDistance = 0
const style = computed(() => ({
  transform: `translate3d(${camera.x}px, ${camera.y}px, 0) scale(${camera.scale})`,
  '--inverse-scale': 1 / camera.scale,
}))
const meadowStyle = computed(() => ({
  backgroundSize: `${384 * camera.scale}px ${384 * camera.scale}px`,
  backgroundPosition: `${camera.x}px ${camera.y}px`,
}))
const townOutOfView = computed(
  () =>
    !geographic.value &&
    (camera.x + SCENE.width * camera.scale < 35 ||
      camera.x > dimensions.width - 35 ||
      camera.y + SCENE.height * camera.scale < 145 ||
      camera.y > dimensions.height - 135),
)
function setCamera(value: Camera) {
  Object.assign(camera, clampCamera(value, dimensions.width, dimensions.height, cameraWorld.value))
  emit('zoom', camera.scale)
}
function reset() {
  const { width, height } = dimensions
  const scale = limits.value.initial
  setCamera({ scale, x: width / 2 - 850 * scale, y: (height + 5) / 2 - 605 * scale })
}
watch(
  () => props.view,
  (next, previous) => {
    savedCameras.set(previous, { ...camera })
    const saved = savedCameras.get(next)
    if (saved) setCamera(saved)
    else reset()
  },
)
watch(
  () => props.focusLocation,
  () => {
    if (!userVisible.value || !userPosition.value) {
      emit('outside')
      return
    }
    const scale = Math.max(camera.scale, 0.72)
    setCamera({
      scale,
      x: dimensions.width / 2 - userPosition.value[0] * scale,
      y: dimensions.height * 0.45 - userPosition.value[1] * scale,
    })
  },
)

function changeZoom(factor: number) {
  setCamera(
    zoomAt(
      camera,
      factor,
      dimensions.width / 2,
      dimensions.height / 2,
      dimensions.width,
      dimensions.height,
      cameraWorld.value,
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
  const place = props.allPlaces.find((p) => p.id === request?.id)
  if (place) focus(place.point)
  const site = gameSites.find((s) => `quest:${s.id}` === request?.id)
  if (site) focus({ x: site.point[0], y: site.point[1] })
  if (roamingPoint.value) focus({ x: roamingPoint.value[0], y: roamingPoint.value[1] })
}
watch(() => props.focusRequest, applyFocus, { flush: 'post' })
function down(event: PointerEvent) {
  if (pointers.size === 0) {
    suppressClick = false
    dragDistance = 0
  }
  const button = (event.target as Element).closest('button')
  if ((button && !button.classList.contains('quest-pin')) || event.button > 0) return
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
      cameraWorld.value,
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
      cameraWorld.value,
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
    class="map-viewport"
    :class="{
      dragging,
      'motion-paused': !motion,
      'compact-pins': camera.scale < 0.58,
      'is-geographic': geographic,
      'has-meadow': !geographic,
    }"
    role="region"
    :aria-label="geographic ? '古镇真实地理地图，可拖动缩放' : '古镇导览，可拖动缩放'"
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
    <div v-if="!geographic" class="meadow-backdrop" :style="meadowStyle" aria-hidden="true"></div>
    <div class="map-scene" :style="style">
      <template v-if="!geographic">
        <img
          class="map-art"
          src="/art/puyuan-original-scope.webp"
          alt="原始参考地图"
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
                      :href="i % 2 ? '/art/boat-covered.webp' : '/art/boat-bamboo.webp'"
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
      </template>
      <template v-else>
        <svg
          class="real-map-scene"
          :width="SCENE.width"
          :height="SCENE.height"
          :viewBox="`0 0 ${SCENE.width} ${SCENE.height}`"
          aria-label="公开地图道路、水道、桥梁和园区范围"
        >
          <rect :width="SCENE.width" :height="SCENE.height" fill="#eeeedf" />
          <g>
            <path
              v-for="(shape, index) in geography.shapes.value.filter((s) => s.layer === 'boundary')"
              :key="`boundary-${index}`"
              :d="shape.d"
              class="real-boundary"
            />
            <path
              v-for="(shape, index) in geography.shapes.value.filter((s) => s.layer === 'road')"
              :key="`road-${index}`"
              :d="shape.d"
              class="real-road-casing"
            />
            <path
              v-for="(shape, index) in geography.shapes.value.filter((s) => s.layer !== 'boundary')"
              :key="index"
              :d="shape.d"
              :class="[`real-${shape.layer}`, { 'real-bridge': shape.bridge }]"
              fill-rule="evenodd"
            />
          </g>
          <g
            v-if="userVisible && userPosition"
            class="main-user-position"
            :class="{ stale: userStatus === 'stale' }"
            :transform="`translate(${userPosition[0]},${userPosition[1]})`"
          >
            <circle :r="accuracyRadius" class="geo-accuracy" />
            <circle :r="7 / camera.scale" class="geo-position" :stroke-width="2 / camera.scale" />
          </g>
        </svg>
        <button
          v-for="position in positions"
          :key="position.feature.id"
          class="map-pin geo-landmark scenic"
          :style="{ left: `${position.point.x}px`, top: `${position.point.y}px` }"
          :aria-label="`查看地图资料：${position.name}`"
          @click.stop="emit('geoselect', position.feature)"
          @dblclick.stop
        >
          <span class="pin-symbol"><AppIcon name="pin" :size="18" /></span
          ><span class="pin-caption">{{ position.name }}</span>
        </button>
      </template>
      <ReferenceLabels
        v-if="view === 'reference'"
        :places="places"
        @select="emit('select', $event)"
      />
      <template v-if="view === 'reference'">
        <div
          v-if="roamingPoint"
          class="roaming-area"
          :style="{ left: `${roamingPoint[0]}px`, top: `${roamingPoint[1]}px` }"
        >
          <span>{{ roamingName }} · 活动范围示意</span>
        </div>
        <button
          v-for="site in gameSites"
          :key="site.id"
          class="quest-pin"
          :class="{ 'pin-west': site.id === 'treasure', 'pin-east': site.id === 'relay' }"
          :style="{ left: `${site.point[0]}px`, top: `${site.point[1]}px` }"
          :aria-label="`游戏：${site.place} · ${site.challenges.map((c) => c.name).join('、')}`"
          :title="`${site.place} · ${site.challenges.map((c) => c.name).join('、')}`"
          @click.stop="emit('game', site.id)"
          @dblclick.stop
        >
          <span
            ><AppIcon name="flag" :size="16" /><b v-if="site.challenges.length > 1">{{
              site.challenges.length
            }}</b></span
          >
        </button>
      </template>
    </div>
  </div>
  <div v-if="geographic && geography.error.value" class="geo-map-error" role="status">
    {{ geography.error.value }}<button @click="geography.reload()">重新加载</button>
  </div>
  <div
    v-if="geographic && !geography.frame.value && !geography.error.value"
    class="geo-map-error"
    role="status"
  >
    正在加载路网…
  </div>
  <button v-if="townOutOfView" class="return-to-town" @click="reset">
    <AppIcon name="map" :size="16" />回到古镇
  </button>
  <div class="map-tools" aria-label="地图工具">
    <button
      class="map-tool locate-tool"
      aria-label="获取我的位置"
      title="获取我的位置"
      @click="emit('locate')"
    >
      <AppIcon name="locate" :size="22" />
    </button>
    <div class="zoom-tools">
      <button
        class="map-tool"
        aria-label="放大地图"
        :disabled="atMaxZoom"
        @click="changeZoom(ZOOM_STEP)"
      >
        <AppIcon name="plus" /></button
      ><span></span
      ><button
        class="map-tool"
        aria-label="缩小地图"
        :disabled="atMinZoom"
        @click="changeZoom(1 / ZOOM_STEP)"
      >
        <AppIcon name="minus" />
      </button>
    </div>
    <button class="map-tool" aria-label="重置地图视野" title="重置地图视野" @click="reset">
      <AppIcon name="reset" />
    </button>
  </div>
  <div v-if="geographic" class="compass" aria-hidden="true">
    <span>{{ geographic ? '北' : '览' }}</span><svg width="32" height="40" viewBox="0 0 32 40">
      <path d="M16 3 26 34 16 28 6 34Z" fill="#a49a7b" />
      <path d="M16 3 16 28 6 34Z" fill="#476456" />
    </svg>
  </div>
</template>
