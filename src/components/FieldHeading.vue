<script setup lang="ts">
import { t } from '../i18n'
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
      <p class="folio-kicker">{{ t('SOX OFFSITE') }} <i></i> {{ t(edition) }}</p>
      <h1>{{ t(title) }}</h1>
      <p class="folio-note">{{ t(note) }}</p>
    </div>
    <span class="folio-seal" aria-hidden="true">{{ t(seal) }}</span>
  </header>
</template>
