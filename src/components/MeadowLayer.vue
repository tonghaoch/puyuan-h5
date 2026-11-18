<script setup lang="ts">
import { computed } from 'vue'
import meadow from '../data/meadow-tiles.json'
import { visibleScene, type Camera } from '../lib/map-camera'
const props = defineProps<{ camera: Camera; width: number; height: number }>()
const tiles = computed(() => {
  const view = visibleScene(props.camera, props.width, props.height, 180)
  return meadow.tiles.filter(
    (t) =>
      t.x + t.width > view.left &&
      t.x < view.right &&
      t.y + t.height > view.top &&
      t.y < view.bottom,
  )
})
</script>
<template>
  <div class="meadow-layer" aria-hidden="true">
    <img
      v-for="tile in tiles"
      :key="tile.id"
      :src="tile.src"
      :style="{ left: `${tile.x}px`, top: `${tile.y}px` }"
      :width="tile.width"
      :height="tile.height"
      alt=""
      draggable="false"
      decoding="async"
    />
  </div>
</template>
