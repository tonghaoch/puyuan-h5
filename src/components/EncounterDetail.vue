<script setup lang="ts">
import { t } from '../i18n'
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import QuestToken from './QuestToken.vue'
import EncounterToken from './EncounterToken.vue'
import FieldPlate from './FieldPlate.vue'
import { quests, tools, type Quest, type Wanderer } from '../data/offsite'
const props = defineProps<{ entry: Quest | Wanderer; sheet?: boolean }>()
defineEmits<{ back: []; map: [id: string] }>()
const isQuest = computed(() => 'place' in props.entry)
const location = computed(() => ('place' in props.entry ? props.entry.place : props.entry.area))
const number = computed(() =>
  String(quests.findIndex((quest) => quest.id === props.entry.id) + 1).padStart(2, '0'),
)
</script>
<template>
  <section
    class="quest-detail"
    :class="[sheet ? 'quest-brief' : 'field-page', { 'npc-dossier': !isQuest }]"
    :aria-label="t(isQuest ? '游戏详情' : '人物手札')"
  >
    <div class="field-inner">
      <button v-if="!sheet" class="back-link" @click="$emit('back')">
        <AppIcon name="chevron" :size="16" />{{ t('返回游戏手册') }}
      </button>
      <header class="warrant-heading">
        <QuestToken v-if="isQuest" /><EncounterToken v-else />
        <div>
          <p class="section-kicker">
            {{ isQuest ? t('江湖令 {number}', { number }) : t('游走 NPC') }} <i></i>
            <span>{{ t(location) }}</span>
          </p>
          <h2 v-if="sheet">{{ t(entry.name) }}</h2>
          <h1 v-else>{{ t(entry.name) }}</h1>
        </div>
      </header>
      <FieldPlate :entry="entry" />
      <p class="dossier-intro">{{ t(entry.description) }}</p>
      <div class="rule-block">
        <span>{{ t('壹') }}</span>
        <div>
          <h3>{{ t(isQuest ? '怎么玩' : '相遇任务') }}</h3>
          <p>{{ t(entry.setup) }}</p>
        </div>
      </div>
      <div class="rule-block">
        <span>{{ t('贰') }}</span>
        <div>
          <h3>{{ t(isQuest ? '怎样过关' : '相遇结果') }}</h3>
          <p>{{ t(entry.goal) }}</p>
        </div>
      </div>
      <aside v-if="entry.note" class="dossier-note">
        <strong>{{ t('额外机缘') }}</strong>
        <p>{{ t(entry.note) }}</p>
      </aside>
      <details v-if="entry.id === 'trader'" class="dossier-shop">
        <summary>{{ t('商人的五张特殊卡 · 查看价目') }}</summary>
        <dl>
          <div v-for="[name, price, rule] in tools" :key="name">
            <dt>{{ t(name) }} · {{ price }} {{ t('交子') }}</dt>
            <dd>{{ t(rule) }}</dd>
          </div>
        </dl>
      </details>
      <button
        v-if="!sheet && entry.point"
        class="field-action"
        @click="$emit('map', `${isQuest ? 'quest' : 'npc'}:${entry.id}`)"
      >
        <AppIcon name="map" :size="18" />{{ t(isQuest ? '在导览中查看' : '查看活动范围') }}
      </button>
      <p class="field-fine">
        {{
          t(
            isQuest
              ? '令牌标示挑战区域，集合点以现场守关人为准。'
              : entry.point
                ? '活动范围仅作示意，不是实时位置；请在现场留意角色装扮。'
                : '巡捕游走全古镇，不设固定点位。',
          )
        }}
      </p>
    </div>
  </section>
</template>
