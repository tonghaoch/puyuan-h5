<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import QuestToken from './QuestToken.vue'
import { gameSites, type GameSite } from '../data/offsite'
const props = defineProps<{ site: GameSite; index: number; sheet?: boolean }>()
defineEmits<{ back: []; map: []; choose: [index: number] }>()
const current = computed(() => props.site.challenges[props.index]!)
const number = computed(() =>
  String(gameSites.findIndex((s) => s.id === props.site.id) + 1).padStart(2, '0'),
)
</script>
<template>
  <section class="quest-detail" :class="sheet ? 'quest-brief' : 'field-page'" aria-label="游戏详情">
    <div class="field-inner">
      <button v-if="!sheet" class="back-link" @click="$emit('back')">
        <AppIcon name="chevron" :size="16" />返回游戏手册
      </button>
      <header class="warrant-heading">
        <QuestToken />
        <div>
          <p class="section-kicker">
            江湖令 {{ number }} <i></i> {{ sheet ? site.place : '濮院诗简' }}
          </p>
          <h2 v-if="sheet">{{ current.name }}</h2>
          <h1 v-else>{{ site.place }}</h1>
        </div>
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
      <template v-if="!sheet">
        <p class="section-kicker mission-kicker">关卡手札 <i></i> MISSION BRIEF</p>
        <h2 class="field-title">{{ current.name }}</h2>
      </template>
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
      <button v-if="!sheet" class="field-action" @click="$emit('map')">
        <AppIcon name="map" :size="18" />在导览中查看
      </button>
      <p class="field-fine">令牌标示挑战区域，集合点以现场守关人为准。</p>
    </div>
  </section>
</template>
