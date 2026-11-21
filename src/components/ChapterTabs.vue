<script setup lang="ts">
import { t } from '../i18n'
defineProps<{
  label: string
  items: readonly (readonly [string, string])[]
  current: string
  base?: '#games' | '#itinerary'
}>()
defineEmits<{ select: [key: string] }>()
</script>
<template>
  <component
    :is="base ? 'nav' : 'div'"
    :role="base ? undefined : 'group'"
    :aria-label="t(label)"
    class="chapter-tabs"
    :class="{ 'chapter-index': base }"
  >
    <template v-for="[key, name] in items" :key="key">
      <a
        v-if="base"
        :href="`${base}${key ? '/' + key : ''}`"
        :aria-current="current === key ? 'page' : undefined"
        >{{ t(name) }}</a
      >
      <button v-else type="button" :aria-pressed="current === key" @click="$emit('select', key)">
        {{ t(name) }}
      </button>
    </template>
  </component>
</template>

<style scoped>
.chapter-tabs {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(0, 1fr);
  gap: 4px;
  color: #5e5646;
}
.chapter-index {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 4px clamp(8px, 3vw, 16px);
  background: #f6f0e1;
  border-bottom: 1px solid #cbbea3;
}
.chapter-tabs :is(a, button) {
  position: relative;
  isolation: isolate;
  display: grid;
  place-items: center;
  min-width: 0;
  min-height: 44px;
  padding: 2px;
  color: inherit;
  font: 600 14px/1.25 var(--serif);
  text-align: center;
  text-decoration: none;
}
.chapter-tabs :is(a, button),
.chapter-tabs :is(a, button)::before {
  transition-property: none;
}
.chapter-tabs :is(a, button)::before {
  content: '';
  position: absolute;
  z-index: -1;
  inset: 5px 0;
  border: 1px solid #d6c9af;
  border-radius: 2px;
  background: linear-gradient(#fcf8ed, #f2ead8);
}
.chapter-tabs :is([aria-current='page'], [aria-pressed='true']) {
  color: #fff4d7;
}
.chapter-tabs :is([aria-current='page'], [aria-pressed='true'])::before {
  inset-block: 2px;
  border-color: var(--tab-ink, #793e30);
  background: var(--tab-ink, #793e30);
  box-shadow:
    inset 0 0 0 2px var(--tab-ink, #793e30),
    inset 0 0 0 3px #d9bd827a;
}
.chapter-tabs :is([aria-current='page'], [aria-pressed='true'])::after {
  content: '';
  position: absolute;
  bottom: 1px;
  width: 6px;
  height: 6px;
  transform: rotate(45deg);
  background: var(--tab-ink, #793e30);
}
.chapter-tabs :is(a, button):focus-visible {
  outline: 2px solid #854631;
  outline-offset: 0;
}
@media (hover: hover) {
  .chapter-tabs :is(a, button):hover::before {
    border-color: #95805a;
  }
}
</style>
