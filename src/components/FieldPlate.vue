<script setup lang="ts">
import { t } from '../i18n'
import { computed, ref } from 'vue'
import { encounterImage, type FieldEntry } from '../data/offsite'
const props = defineProps<{ entry: FieldEntry }>()
const selected = ref(0)
const photo = computed(() => props.entry.photos[selected.value]!)
const folioMarks = ['壹', '贰', '叁']
let touchOrigin: { x: number; y: number } | null = null
function startLeaf(event: TouchEvent) {
  const touch = event.touches[0]
  touchOrigin = touch && event.touches.length === 1 ? { x: touch.clientX, y: touch.clientY } : null
}
function finishLeaf(event: TouchEvent) {
  const origin = touchOrigin
  touchOrigin = null
  const touch = event.changedTouches[0]
  if (!origin || !touch || event.touches.length) return
  const delta = touch.clientX - origin.x
  if (Math.abs(delta) < 44 || Math.abs(delta) < 1.5 * Math.abs(touch.clientY - origin.y)) return
  selected.value = Math.max(
    0,
    Math.min(props.entry.photos.length - 1, selected.value - Math.sign(delta)),
  )
}
</script>
<template>
  <div class="field-plate">
    <figure :aria-label="t('{name}图录', { name: entry.name })">
      <div
        class="plate-mount"
        @touchstart.passive="startLeaf"
        @touchend.passive="finishLeaf"
        @touchcancel="touchOrigin = null"
      >
        <div :key="selected" class="plate-leaf" :class="photo[2]">
          <div v-if="photo[2] === 'portrait'" class="plate-inscription" aria-hidden="true">
            <span>{{ t('人物小像') }}</span><i>{{ t('濮院') }}</i>
          </div>
          <img :src="encounterImage(entry.id, selected + 1)" :alt="t(photo[1])" draggable="false" />
        </div>
      </div>
      <figcaption aria-live="polite">
        <span class="plate-imprint">{{ t('图记') }}</span><span>{{ t(photo[1]) }}</span>
      </figcaption>
    </figure>
    <div
      v-if="entry.photos.length > 1"
      class="plate-choices"
      role="group"
      :aria-label="t('选择图版')"
    >
      <button
        v-for="([label], index) in entry.photos"
        :key="label"
        type="button"
        :aria-pressed="selected === index"
        @click="selected = index"
      >
        <span aria-hidden="true">{{ t(folioMarks[index] ?? index + 1) }}</span>{{ t(label) }}
      </button>
    </div>
  </div>
</template>
