<script setup lang="ts">
import { computed } from 'vue'
import { SCENE, visibleScene, type Camera } from '../lib/map-camera'

const props = defineProps<{ camera: Camera; width: number; height: number }>()
const tiles = computed(() => {
  const density = props.camera.scale * window.devicePixelRatio
  const closeUp = props.camera.scale >= 2.7 || density > 4
  const level = closeUp ? 8 : density > 1.7 ? 4 : density > 1.1 ? 2 : 1
  if (level === 1 || !props.width || !props.height) return []
  const step = (closeUp ? 1024 : 512) / level
  const view = visibleScene(props.camera, props.width, props.height, 32 / props.camera.scale)
  const tiles = []
  for (
    let y = Math.max(0, Math.floor(view.top / step));
    y * step < Math.min(view.bottom, SCENE.height);
    y++
  ) {
    for (
      let x = Math.max(0, Math.floor(view.left / step));
      x * step < Math.min(view.right, SCENE.width);
      x++
    ) {
      tiles.push({
        src: `/art/reference-tiles/${level}/${x}-${y}.webp`,
        left: x * step,
        top: y * step,
        width: Math.min(step, SCENE.width - x * step),
        height: Math.min(step, SCENE.height - y * step),
      })
    }
  }
  return tiles
})
</script>
<template>
  <div class="reference-tiles" aria-hidden="true">
    <img
      v-for="tile in tiles"
      :key="tile.src"
      :src="tile.src"
      :width="tile.width"
      :height="tile.height"
      :style="{ left: `${tile.left}px`, top: `${tile.top}px` }"
      alt=""
      decoding="async"
      draggable="false"
      @load="($event.currentTarget as HTMLImageElement).classList.add('loaded')"
    />
  </div>
</template>
<style scoped>
.reference-tiles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.reference-tiles img {
  position: absolute;
  visibility: hidden;
  max-width: none;
}
.reference-tiles img.loaded {
  visibility: visible;
}
</style>
