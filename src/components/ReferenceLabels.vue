<script setup lang="ts">
import { t } from '../i18n'
import type { Place } from '../data/catalog'
import layout from '../data/reference-map.json'

defineProps<{ places: Place[] }>()
defineEmits<{ select: [place: Place] }>()

// Centers of the printed nameplates in original image coordinates (not POI anchors).
const centers: Record<string, [number, number]> = {
  visitor: [733, 347],
  'water-stage': [1096, 319],
  'north-gate': [577, 491],
  fuma: [723, 611],
  temple: [948, 618],
  'art-gallery': [1116, 454],
  'zen-hotel': [1253, 496],
  'designer-house': [1384, 618],
  xiangyun: [1212, 756],
  guildhall: [627, 913],
  theater: [815, 895],
  teahouse: [856, 956],
  shuchang: [971, 936],
  dayou: [650, 1018],
  dining: [470, 1070],
  market: [1053, 1038],
  zhuanglou: [686, 1119],
  'food-center': [1370, 396],
}
function position(x: number, y: number) {
  return { left: `${x + layout.sourceOffset.x}px`, top: `${y + layout.sourceOffset.y}px` }
}
function printedName(place: Place) {
  // The original sign uses 径; the place directory uses 泾.
  return place.id === 'theater' ? '梅径剧场' : place.name
}
</script>
<template>
  <div class="reference-labels">
    <span class="town-title" :style="position(1055, 718)">{{ t('濮院古镇') }}</span>
    <button
      v-for="place in places"
      :key="place.id"
      :style="position(...centers[place.id]!)"
      :aria-label="t('查看{name}', { name: printedName(place) })"
      @click.stop="$emit('select', place)"
      @dblclick.stop
    >
      {{ t(printedName(place)) }}
    </button>
  </div>
</template>
<style scoped>
.reference-labels {
  position: absolute;
  inset: 0;
  pointer-events: none;
  font-family: KaiTi, STKaiti, 'Kaiti SC', serif;
  color: #766050;
}
.reference-labels button,
.town-title {
  position: absolute;
  transform: translate(-50%, -50%);
}
.reference-labels button {
  pointer-events: auto;
  font: inherit;
  color: inherit;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.25;
  white-space: nowrap;
  padding: 3px 11px;
  background: #fffdf6;
  border: 2px solid #aa998b;
  border-radius: 10px;
}
.reference-labels button::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 23%;
  width: 18px;
  height: 19px;
  background: #fffdf6;
  clip-path: polygon(20% 0, 100% 0, 0 100%);
}
.town-title {
  writing-mode: vertical-rl;
  white-space: nowrap;
  font-size: 57px;
  letter-spacing: 6px;
  font-weight: 700;
  -webkit-text-stroke: 9px #fffdf6;
  paint-order: stroke fill;
}
</style>
