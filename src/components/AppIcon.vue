<script setup lang="ts">
withDefaults(defineProps<{ name: string; size?: number }>(), { size: 20 })
const paths: Record<string, string> = {
  calendar: 'M4 5h16v16H4zM4 10h16M8 3v4m8-4v4M8 14h2m4 0h2m-8 3h2',
  flag: 'M5 22V3m0 1q3-3 8 0t8-1l-2 5 2 4q-3 3-8 0t-8 0',
  bowl: 'M3 11h18a9 9 0 0 1-18 0Zm5 10h8M9 10l9-8m-4 8 7-6',
  map: 'm3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2V5Zm6-2v16m6-14v16',
  pavilion:
    'M3 10c3.6 0 6.7-3.3 9-5.5 2.3 2.2 5.4 5.5 9 5.5-4 1.7-14 1.7-18 0ZM12 2v2.5M6 12v8m12-8v8M9 12v7m6-7v7M3 21c3 .5 6-1 9-1s6 1.5 9 1',
  pin: 'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0ZM15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  search: 'm21 21-4.5-4.5M19 10.5a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0Z',
  tea: 'M4 8h13v6a6.5 6.5 0 0 1-13 0V8Zm13 1h2a3 3 0 0 1 0 6h-2M3 22h16M8 2v3m5-3v3',
  fan: 'M12 20 2 8a15 15 0 0 1 20 0L12 20Zm0 0L8 4m4 16 4-16m-4 0v16m-2 2h4',
  flower:
    'M12 9C5 0 2 7 7 11c-8 0-5 9 2 6-2 8 7 8 6 0 7 3 10-6 2-6 5-4 2-11-5-2Zm2 4a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z',
  sparkles: 'm12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8L12 2Zm8-1v4m-2-2h4',
  bell: 'M4 17h16l-2-4V9a6 6 0 0 0-12 0v4l-2 4Zm6 4h4M12 1v2',
  heart:
    'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',
  arrow: 'M4 12h16m-6-6 6 6-6 6',
  chevron: 'm9 5 7 7-7 7',
  close: 'm6 6 12 12M6 18 18 6',
  plus: 'M12 5v14M5 12h14',
  minus: 'M5 12h14',
  locate:
    'M12 2v3m0 14v3M2 12h3m14 0h3M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  clock: 'M12 7v5l3 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
  book: 'M12 5v16M12 5C8 2 4 2 2 3v16c4-1 7 0 10 2 3-2 6-3 10-2V3c-3-1-7-1-10 2Z',
  leaf: 'M20 3C4 0 1 11 8 17s15-1 12-14ZM4 21l12-13',
  check: 'm5 12 4 4L19 6',
  info: 'M12 11v6m0-10h.01M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
  volume: 'M4 9h4l5-4v14l-5-4H4V9Zm13-1a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14',
  moon: 'M21 13A9 9 0 0 1 11 3a9 9 0 1 0 10 10Z',
  reset: 'M3 11a9 9 0 1 1 2.6 7.5M3 4v7h7',
  lantern: 'M8 3h8M12 0v3M6 6h12v10H6V6Zm2 13h8m-4-3v8M4 6c-3 3-3 7 0 10M20 6c3 3 3 7 0 10',
}
</script>
<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.55"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="paths[name] || paths.sparkles" />
  </svg>
</template>
