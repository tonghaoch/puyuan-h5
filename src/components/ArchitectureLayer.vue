<script setup lang="ts">
import { computed } from 'vue'
import atlas from '../data/architecture-tiles.json'
import { visibleScene, type Camera } from '../lib/map-camera'
const props = defineProps<{ camera: Camera; width: number; height: number }>()
const tiles = computed(() => {
  const view = visibleScene(props.camera, props.width, props.height, 80)
  return atlas.tiles.filter(
    (t) =>
      t.x + t.width > view.left &&
      t.x < view.right &&
      t.y + t.height > view.top &&
      t.y < view.bottom,
  )
})
</script>
<template>
  <div class="architecture-context-layer" aria-hidden="true">
    <img
      v-for="tile in tiles"
      :key="tile.id"
      :src="camera.scale >= 0.75 ? tile.asset : tile.overviewAsset"
      :style="{ left: `${tile.x}px`, top: `${tile.y}px` }"
      :width="tile.width"
      :height="tile.height"
      alt=""
      decoding="async"
      draggable="false"
    />
  </div>
</template>
