<script setup lang="ts">
import { t } from '../i18n'
import type { Tab } from '../data/catalog'
defineProps<{ current: Tab }>()
defineEmits<{ navigate: [tab: Tab] }>()
const destinations = [
  ['map', '地图'],
  ['itinerary', '行程'],
  ['games', '游戏'],
  ['food', '餐厅'],
] as const
</script>

<template>
  <nav class="main-nav" :aria-label="t('主要导航')">
    <button
      v-for="[id, label] in destinations"
      :key="id"
      type="button"
      :aria-current="current === id ? 'page' : undefined"
      @click="$emit('navigate', id)"
    >
      <svg
        viewBox="0 0 32 28"
        width="30"
        height="26"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
        focusable="false"
      >
        <g v-if="id === 'map'">
          <path d="M4 22c5 .7 7.5-1.5 12-1.5s7 2.2 12 1.5M7 25c4 .6 6-1 9-1s5 1.6 9 1" />
          <path
            d="M7 21v-8m18 8v-8M11 20.3v-6.5m10 6.5v-6.5M5 12c4.5 0 8-4.4 11-7.3 3 2.9 6.5 7.3 11 7.3-5 2.1-17 2.1-22 0Z"
          />
          <path d="M16 2.5v2.3M12 9.5h8" />
        </g>
        <g v-else-if="id === 'itinerary'">
          <path
            d="M6 4.5h18.5a2.7 2.7 0 0 1 2.7 2.7v2.3h-5V7.2a2.7 2.7 0 0 1 2.3-2.7M6 4.5A2.5 2.5 0 0 1 8.5 7v13.5H3.8v1.2A3.3 3.3 0 0 0 7.1 25h13a3 3 0 0 0 3-3v-1.5H8.5"
          />
          <path d="M22.2 9.5v11M12 10h7m-7 4h5m-5 3h3" />
        </g>
        <g v-else-if="id === 'games'">
          <path d="m16 2.5 3.5 2.4 6 1.8-1.3 12L16 24l-8.2-5.3-1.3-12 6-1.8Z" />
          <path
            d="m10 12.2 6-4.8 6 4.8m-8.2.3h4.4m-6.2 2.8h7l-3 3-1.7-1M16 24l-2 2.5m2-2.5 2 2.5"
          />
        </g>
        <g v-else>
          <path
            d="M4 14.5h24M6 15.3c.8 5.1 3.7 7.3 10 7.3s9.2-2.2 10-7.3M11.5 25h9M5.5 11.8c3.5-.3 5.2-5.1 10.5-5.1s7 4.8 10.5 5.1Z"
          />
          <path d="M14.2 6.8V5a1.8 1.8 0 0 1 3.6 0v1.8M10 17.5q1 1.7 3.5 2" />
        </g>
      </svg>
      <span>{{ t(label) }}</span>
    </button>
  </nav>
</template>

<style scoped>
.main-nav {
  position: absolute;
  z-index: 30;
  inset: auto 0 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 4px;
  height: calc(var(--main-nav-height) + env(safe-area-inset-bottom));
  padding: 5px 9px calc(4px + env(safe-area-inset-bottom));
  border-top: 1px solid #cec8bc;
  background: #faf9f5;
}
button {
  position: relative;
  isolation: isolate;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 2px;
  padding: 0;
  color: #605543;
  font: 600 14px/1.2 var(--serif);
}
button span {
  letter-spacing: 0.12em;
  text-indent: 0.12em;
}
button svg {
  color: #856a40;
}
button[aria-current='page'] {
  color: #fff0cc;
}
button[aria-current='page'] svg {
  color: #ffe2a4;
}
button[aria-current='page']::before,
button[aria-current='page']::after {
  content: '';
  position: absolute;
  z-index: -1;
  clip-path: polygon(
    7px 0,
    calc(100% - 7px) 0,
    100% 7px,
    100% calc(100% - 7px),
    calc(100% - 7px) 100%,
    7px 100%,
    0 calc(100% - 7px),
    0 7px
  );
}
button[aria-current='page']::before {
  inset: 2px 4px;
  background: linear-gradient(135deg, #e0bf82, #9c7546 55%, #d9b77c);
}
button[aria-current='page']::after {
  inset: 3px 5px;
  background: linear-gradient(120deg, #834a35, #683728);
}
button:focus-visible {
  outline: 2px solid #994230;
  outline-offset: -2px;
}
</style>
