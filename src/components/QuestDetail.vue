<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { gameSites, type GameSite } from '../data/offsite'
const props = defineProps<{ site: GameSite; index: number; fromMap: boolean }>()
defineEmits<{ back: []; map: []; choose: [index: number] }>()
const current = computed(() => props.site.challenges[props.index]!)
const number = computed(() =>
  String(gameSites.findIndex((s) => s.id === props.site.id) + 1).padStart(2, '0'),
)
</script>
<template>
  <section class="field-page quest-detail" aria-label="游戏详情">
    <div class="field-inner">
      <button class="back-link" @click="$emit('back')">
        <AppIcon name="chevron" :size="16" />{{ fromMap ? '返回地图' : '返回游戏手册' }}
      </button>
      <header class="quest-banner">
        <p class="folio-kicker">PUYUAN QUEST <i></i> {{ number }}</p>
        <h1>{{ site.place }}</h1>
        <p>濮院诗简 · 固定挑战</p>
        <AppIcon name="flag" :size="64" />
      </header>
      <div v-if="site.challenges.length > 1" class="field-tabs detail-tabs" aria-label="选择挑战">
        <button
          v-for="(c, i) in site.challenges"
          :key="c.name"
          :aria-pressed="index === i"
          @click="$emit('choose', i)"
        >
          {{ c.name }}
        </button>
      </div>
      <p class="section-kicker">MISSION BRIEF</p>
      <h2 class="field-title">{{ current.name }}</h2>
      <div class="rule-block">
        <span>壹</span>
        <div>
          <h3>怎么玩</h3>
          <p>{{ current.setup }}</p>
        </div>
      </div>
      <div class="rule-block">
        <span>贰</span>
        <div>
          <h3>怎样过关</h3>
          <p>{{ current.goal }}</p>
        </div>
      </div>
      <button class="field-action" @click="$emit('map')">
        <AppIcon name="flag" :size="18" />{{ fromMap ? '返回地图' : '在导览中查看' }}
      </button>
      <p class="field-fine">朱旗标示活动参考区域，具体集合点以现场守关人为准。</p>
    </div>
  </section>
</template>
