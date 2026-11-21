<script setup lang="ts">
import { t } from '../i18n'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from './AppIcon.vue'
defineProps<{ label: string; wide?: boolean }>()
const emit = defineEmits<{ close: [] }>()
const panel = ref<HTMLElement>()
const dragOffset = ref(0)
const dragging = ref(false)
let dragStart = 0
let pointer: number | null = null
let suppressClick = false
function startDrag(event: PointerEvent) {
  if (event.button > 0) return
  pointer = event.pointerId
  dragStart = event.clientY
  dragging.value = true
  ;(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId)
}
function moveDrag(event: PointerEvent) {
  if (pointer === event.pointerId) dragOffset.value = Math.max(0, event.clientY - dragStart)
}
function endDrag(event: PointerEvent) {
  if (pointer !== event.pointerId) return
  suppressClick = dragOffset.value > 5
  const shouldClose = event.type !== 'pointercancel' && dragOffset.value >= 80
  pointer = null
  dragging.value = false
  dragOffset.value = 0
  if (shouldClose) emit('close')
}
function handleGripClick() {
  if (suppressClick) {
    suppressClick = false
    return
  }
  emit('close')
}
const previous = document.activeElement as HTMLElement | null
function keydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    emit('close')
  }
  if (event.key !== 'Tab') return
  const elements = [
    ...(panel.value?.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a[href], input, select, summary, [tabindex="0"]',
    ) ?? []),
  ].filter((el) => el.getClientRects().length > 0)
  if (!elements.length) {
    event.preventDefault()
    panel.value?.focus()
    return
  }
  const first = elements[0]!,
    last = elements[elements.length - 1]!
  if (
    event.shiftKey &&
    (document.activeElement === first || document.activeElement === panel.value)
  ) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}
onMounted(async () => {
  await nextTick()
  panel.value?.focus()
  document.addEventListener('keydown', keydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', keydown)
  if (previous?.isConnected) previous.focus()
})
</script>
<template>
  <div class="dialog-backdrop" @click.self="emit('close')">
    <section
      ref="panel"
      class="dialog-panel"
      :class="{ wide, dragging }"
      :style="dragOffset ? { transform: `translateY(${dragOffset}px)` } : undefined"
      role="dialog"
      aria-modal="true"
      :aria-label="t(label)"
      tabindex="-1"
    >
      <button
        class="sheet-grip"
        :aria-label="t('收起弹层')"
        @pointerdown="startDrag"
        @pointermove="moveDrag"
        @pointerup="endDrag"
        @pointercancel="endDrag"
        @click="handleGripClick"
      >
        <span></span>
      </button>
      <button class="dialog-close icon-button" :aria-label="t('关闭弹窗')" @click="emit('close')">
        <AppIcon name="close" />
      </button>
      <div class="dialog-content"><slot /></div>
    </section>
  </div>
</template>
