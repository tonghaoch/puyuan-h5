<script setup lang="ts">
import models from '../data/landmark-models.json'
import { computed } from 'vue'
import { visibleScene, type Camera } from '../lib/map-camera'
import reference from '../data/reference-map.json'
const props = defineProps<{
  selectedId?: string
  highlightedId?: string
  camera: Camera
  width: number
  height: number
}>()
const emit = defineEmits<{ select: [placeId: string, modelId: string] }>()
const buildings = computed(() => {
  const view = visibleScene(props.camera, props.width, props.height, 100)
  return models.models
    .filter((model) => {
      const [x, y, w, h] = model.sourceBounds
      return (
        x! + reference.sourceOffset.x + w! > view.left &&
        x! + reference.sourceOffset.x < view.right &&
        y! + reference.sourceOffset.y + h! > view.top &&
        y! + reference.sourceOffset.y < view.bottom
      )
    })
    .sort(
      (a, b) => a.sourceBounds[1]! + a.sourceBounds[3]! - b.sourceBounds[1]! - b.sourceBounds[3]!,
    )
})

function bounds(source: number[]) {
  return {
    left: `${source[0]! + reference.sourceOffset.x}px`,
    top: `${source[1]! + reference.sourceOffset.y}px`,
    width: `${source[2]}px`,
    height: `${source[3]}px`,
  }
}
</script>
<template>
  <div class="landmark-layer" aria-label="古建细节图层">
    <button
      v-for="model in buildings"
      :key="model.id"
      class="landmark-model"
      :class="{
        selected: props.selectedId === model.placeId,
        highlighted: props.highlightedId === model.id,
      }"
      :style="bounds(model.sourceBounds)"
      :data-model-id="model.id"
      :aria-label="`查看${model.name}建筑详情`"
      @click.stop="emit('select', model.placeId, model.id)"
      @dblclick.stop
    >
      <img
        :src="
          camera.scale >= 0.75 || props.highlightedId === model.id
            ? model.asset
            : model.overviewAsset
        "
        :alt="`${model.name}独立建筑插画`"
        draggable="false"
        decoding="async"
      />
      <svg
        class="landmark-light-layer"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <circle
          v-for="(light, index) in model.lights"
          :key="index"
          :cx="light[0]! * 100"
          :cy="light[1]! * 100"
          r=".65"
          class="landmark-lamp"
          :style="{ animationDelay: `${index * -0.7}s` }"
        />
      </svg>
    </button>
  </div>
</template>
