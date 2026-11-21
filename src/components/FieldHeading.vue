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
  <header class="field-heading" :class="`field-${theme}`">
    <div>
      <p class="folio-kicker">SOX OFFSITE <i></i> {{ edition }}</p>
      <h1>{{ title }}</h1>
      <p class="folio-note">{{ note }}</p>
    </div>
    <span class="folio-seal" aria-hidden="true">{{ seal }}</span>
  </header>
</template>
