<script setup lang="ts">
defineProps<{
  edition: string
  title: string
  note: string
  seal: string
  theme: 'journey' | 'games' | 'food'
}>()
</script>
<template>
  <header class="field-heading" :class="[`field-${theme}`, { 'illustrated-heading': $slots.art }]">
    <div v-if="$slots.art" class="folio-art" aria-hidden="true"><slot name="art" /></div>
    <div class="folio-caption">
      <p class="folio-kicker">SOX OFFSITE <i></i> {{ edition }}</p>
      <h1>{{ title }}</h1>
      <p class="folio-note">{{ note }}</p>
    </div>
    <span class="folio-seal" aria-hidden="true">{{ seal }}</span>
  </header>
</template>
