<script setup lang="ts">
import { computed } from 'vue'
import landscape from '../data/native-landscape.json'
import { visibleScene, type Camera } from '../lib/map-camera'
const props = defineProps<{ camera: Camera; width: number; height: number }>()
const tiles = computed(() => {
  const view = visibleScene(props.camera, props.width, props.height, 80)
  return landscape.tiles.filter(
    (tile) =>
      tile.x + tile.width > view.left &&
      tile.x < view.right &&
      tile.y + tile.height > view.top &&
      tile.y < view.bottom,
  )
})
</script>
<template>
  <div class="native-landscape-layer" aria-hidden="true">
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
