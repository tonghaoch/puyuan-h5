<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import type { Place } from '../data/catalog'
import { clampCamera, zoomAt, SCENE, type Camera } from '../lib/map-camera'
import AppIcon from './AppIcon.vue'
import referenceMap from '../data/reference-map.json'
import { useParkGeography, isGeographicView, type MapView } from '../lib/park-geography'
import { classifyFix, type GeographicFix, type GeoFeature } from '../lib/geography'
const props = defineProps<{
  places: Place[]
  selectedId?: string
  focusRequest: { id: string; nonce: number } | null
  allPlaces: Place[]
  motion: boolean
  view: MapView
  fix: GeographicFix | null
  now: number
  focusLocation: number
  query: string
}>()
const emit = defineEmits<{
  select: [place: Place]
  locate: []
  zoom: [value: number]
  geoselect: [feature: GeoFeature]
  outside: []
}>()
const geography = useParkGeography()
const geographic = computed(() => isGeographicView(props.view))
const positions = computed(() =>
  geography.points.value.filter((p) => p.name.includes(props.query.trim())),
)
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
const savedCameras = new Map<string, Camera>()
const viewport = ref<HTMLElement>()
const camera = reactive<Camera>({ x: 0, y: 0, scale: 0.6 })
const dimensions = reactive({ width: 0, height: 0 })
const dragging = ref(false)
const ready = ref(false)
const pointers = new Map<number, { x: number; y: number }>()
let observer: ResizeObserver | undefined
const style = computed(() => ({
  transform: `translate3d(${camera.x}px, ${camera.y}px, 0) scale(${camera.scale})`,
  '--inverse-scale': 1 / camera.scale,
}))
const icon: Record<string, string> = {
  performance: 'fan',
  craft: 'flower',
  food: 'tea',
  scenic: 'lantern',
  service: 'bell',
}
function setCamera(value: Camera) {
  Object.assign(camera, clampCamera(value, dimensions.width, dimensions.height))
  emit('zoom', camera.scale)
}
function reset() {
  const { width, height } = dimensions
  const scale = Math.min(width / 1120, (height - 160) / 1040)
  setCamera({ scale, x: width / 2 - 850 * scale, y: (height + 5) / 2 - 605 * scale })
}
watch(
  () => props.view,
  (next, previous) => {
    const previousKind = isGeographicView(previous) ? 'geographic' : 'art'
    const nextKind = isGeographicView(next) ? 'geographic' : 'art'
    if (previousKind === nextKind) return
    savedCameras.set(previousKind, { ...camera })
    const saved = savedCameras.get(nextKind)
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
    ),
  )
}
function focus(place: Place) {
  const scale = Math.max(camera.scale, 0.83)
  setCamera({
    scale,
    x: dimensions.width / 2 - place.point.x * scale,
    y: dimensions.height * 0.45 - place.point.y * scale,
  })
}
watch(
  () => props.focusRequest,
  (request) => {
    const place = props.allPlaces.find((p) => p.id === request?.id)
    if (place) focus(place)
  },
)
function down(event: PointerEvent) {
  if ((event.target as Element).closest('button') || event.button > 0) return
  viewport.value?.setPointerCapture(event.pointerId)
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })
  dragging.value = true
}
function move(event: PointerEvent) {
  const old = pointers.get(event.pointerId)
  if (!old) return
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
    }"
    role="region"
    :aria-label="
      geographic ? '古镇真实地理地图，可拖动缩放' : '古镇示意地图，按原图保留建筑与水系，可拖动缩放'
    "
    tabindex="0"
    @pointerdown="down"
    @pointermove="move"
    @pointerup="up"
    @pointercancel="up"
    @lostpointercapture="up"
    @wheel.prevent="wheel"
    @keydown="keyboard"
    @dblclick="changeZoom(1.3)"
  >
    <div class="map-scene" :style="style">
      <template v-if="!geographic">
        <img
          class="map-art"
          :src="
            view === 'reference'
              ? '/art/puyuan-original-scope.webp'
              : '/art/puyuan-reference-aligned.webp'
          "
          alt="按用户原图古镇范围保留的建筑、桥梁、水系与设施，周边住宅及产业区已排除"
          :width="SCENE.width"
          :height="SCENE.height"
          draggable="false"
          fetchpriority="high"
        />
        <div v-if="view === 'illustration'" class="map-water-mask">
          <svg
            :width="SCENE.width"
            :height="SCENE.height"
            :viewBox="`0 0 ${SCENE.width} ${SCENE.height}`"
            aria-hidden="true"
          >
            <g
              :transform="`translate(${referenceMap.sourceOffset.x} ${referenceMap.sourceOffset.y})`"
            >
              <path
                v-for="d in referenceMap.waterAnimations"
                :key="d"
                :d="d"
                class="water-highlight"
              />
            </g>
          </svg>
        </div>
        <svg
          v-if="view === 'illustration'"
          class="map-effects"
          :width="SCENE.width"
          :height="SCENE.height"
          :viewBox="`0 0 ${SCENE.width} ${SCENE.height}`"
          aria-hidden="true"
        >
          <g
            :transform="`translate(${referenceMap.sourceOffset.x} ${referenceMap.sourceOffset.y})`"
          >
            <g class="floating-boat" transform="translate(1218 911) rotate(25) scale(.5)">
              <path
                d="M0-30Q-18-8-12 25Q0 45 12 25Q18-8 0-30Z"
                fill="#8c7655"
                stroke="#e8d8ae"
                stroke-width="2"
              />
              <path d="M-10-10Q0-25 10-10V13H-10Z" fill="#617b67" />
            </g>
            <g class="lantern-glows" fill="#edc275">
              <circle cx="908" cy="669" r="3" />
              <circle cx="948" cy="677" r="3" />
              <circle cx="1061" cy="365" r="3" />
              <circle cx="1193" cy="561" r="3" />
            </g>
            <g class="falling-petals" fill="#d5a39a">
              <path
                d="M670 756q-4-7 4-7 8 4-4 7M1030 428q-4-8 4-7 7 3-4 7M945 900q-4-8 4-8 8 4-4 8"
              />
            </g>
            <g class="bird-flight" fill="none" stroke="#fcf7e5" stroke-width="2">
              <path d="M1020 390q10-10 20 0 10-8 20 0m-75 22q7-7 14 0 7-6 14 0" />
            </g>
          </g>
        </svg>
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
          <image
            v-if="view === 'imagery' && geography.image.value"
            href="/geodata/imagery-reference.jpg"
            v-bind="geography.image.value"
            preserveAspectRatio="none"
          />
          <g :class="{ 'imagery-overlay': view === 'imagery' }">
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
      <button
        v-for="place in geographic ? [] : places"
        :key="place.id"
        class="map-pin"
        :class="[place.category, { selected: place.id === selectedId, secondary: place.secondary }]"
        :style="{ left: `${place.point.x}px`, top: `${place.point.y}px` }"
        :aria-label="`查看${place.name}`"
        @click.stop="emit('select', place)"
        @dblclick.stop
      >
        <span class="pin-symbol"><AppIcon :name="icon[place.category]!" :size="21" /></span>
        <span class="pin-caption">{{ place.name }}</span>
      </button>
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
    正在加载真实路网…
  </div>
  <div
    v-if="view === 'imagery' && geography.imageryError.value"
    class="geo-map-error"
    role="status"
  >
    影像暂时不可用，请切换真实路网。
  </div>
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
      <button class="map-tool" aria-label="放大地图" @click="changeZoom(1.25)">
        <AppIcon name="plus" /></button
      ><span></span
      ><button class="map-tool" aria-label="缩小地图" @click="changeZoom(0.8)">
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
