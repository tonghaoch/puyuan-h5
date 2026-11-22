<script setup lang="ts">
defineProps<{ bearing: number }>()
</script>

<template>
  <g class="compass-fan" :transform="`rotate(${bearing})`" aria-hidden="true" pointer-events="none">
    <path
      d="M0 0 -17 -29 Q0 -41 17 -29 Z"
      fill="#386780"
      fill-opacity=".46"
      stroke="#fff3d2"
      stroke-width="1.5"
    />
    <path
      d="M0 -42 6 -31 0 -34 -6 -31 Z"
      fill="#28475e"
      stroke="#fff3d2"
      stroke-width="1.5"
      stroke-linejoin="round"
    />
  </g>
</template>
