<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import QuestToken from './QuestToken.vue'
import { quests, type Quest } from '../data/offsite'
const props = defineProps<{ quest: Quest; sheet?: boolean }>()
defineEmits<{ back: []; map: [] }>()
const number = computed(() =>
  String(quests.findIndex((quest) => quest.id === props.quest.id) + 1).padStart(2, '0'),
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
          <p class="section-kicker">江湖令 {{ number }} <i></i> {{ quest.place }}</p>
          <h2 v-if="sheet">{{ quest.name }}</h2>
          <h1 v-else>{{ quest.name }}</h1>
        </div>
      </header>
      <p v-if="!sheet" class="section-kicker mission-kicker">关卡手札 <i></i> MISSION BRIEF</p>
      <div class="rule-block">
        <span>壹</span>
        <div>
          <h3>怎么玩</h3>
          <p>{{ quest.setup }}</p>
        </div>
      </div>
      <div class="rule-block">
        <span>贰</span>
        <div>
          <h3>怎样过关</h3>
          <p>{{ quest.goal }}</p>
        </div>
      </div>
      <button v-if="!sheet" class="field-action" @click="$emit('map')">
        <AppIcon name="map" :size="18" />在导览中查看
      </button>
      <p class="field-fine">令牌标示挑战区域，集合点以现场守关人为准。</p>
    </div>
  </section>
</template>
