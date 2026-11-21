<script setup lang="ts">
import { t } from '../i18n'
import { publicAsset } from '../lib/public-asset'
import FieldHeading from './FieldHeading.vue'
import ChapterTabs from './ChapterTabs.vue'
import AppIcon from './AppIcon.vue'
import { encounterImage, quests, wanderers, tools } from '../data/offsite'
defineProps<{ section: string }>()
defineEmits<{
  open: [id: string, opener: HTMLElement]
  npc: [id: string, opener: HTMLElement]
  map: [id: string]
}>()
const sections = [
  ['', '点位挑战'],
  ['roaming', '游走 NPC'],
  ['tokens', '交子与道具'],
] as const
</script>
<template>
  <section class="field-page" :aria-label="t('游戏手册')">
    <FieldHeading
      theme="games"
      edition="FIELD QUESTS"
      title="濮院诗简"
      note="一首散落水乡的诗，等你们组队修复。"
      seal="寻诗"
    />
    <ChapterTabs label="游戏内容" base="#games" :items="sections" :current="section" />
    <div v-if="!section" class="field-inner">
      <div class="field-section-head">
        <div>
          <p class="section-kicker">{{ t('CHAPTER 01') }}</p>
          <h2 class="field-title">{{ t('循令寻关') }}</h2>
        </div>
        <span class="section-count">{{ t('7 处 · 8 项挑战') }}</span>
      </div>
      <p class="field-copy">
        {{
          t(
            '领取乱码诗碑拓片，按地图上的江湖令找到守关人。完成挑战收集词条，最后拼出诗篇，交裁判校验。',
          )
        }}
      </p>
      <a
        v-for="(quest, index) in quests"
        :key="quest.id"
        class="quest-row"
        :href="`#games/task/${quest.id}`"
        @click.exact.prevent="$emit('open', quest.id, $event.currentTarget as HTMLElement)"
      >
        <span class="dossier-thumb"
          ><img
            :src="publicAsset(encounterImage(quest.id, 'thumb'))"
            alt=""
            width="56"
            height="56"
            loading="lazy"
          /><span>{{ String(index + 1).padStart(2, '0') }}</span></span
        >
        <div>
          <small>{{ t(quest.place) }}</small>
          <h3>{{ t(quest.name) }}</h3>
        </div>
        <AppIcon name="chevron" :size="16" />
      </a>
    </div>
    <div v-else-if="section === 'roaming'" class="field-inner">
      <p class="section-kicker">{{ t('ENCOUNTERS') }}</p>
      <h2 class="field-title">{{ t('巷中遇见谁') }}</h2>
      <p class="field-copy">
        {{ t('以下是活动范围，不是实时位置。在附近留意角色装扮，遇见时再触发挑战。') }}
      </p>
      <article v-for="npc in wanderers" :key="npc.id" class="journal-panel">
        <a
          class="npc-entry"
          :href="`#games/npc/${npc.id}`"
          @click.exact.prevent="$emit('npc', npc.id, $event.currentTarget as HTMLElement)"
        >
          <img
            :src="publicAsset(encounterImage(npc.id, 'thumb'))"
            alt=""
            width="54"
            height="54"
            loading="lazy"
          />
          <div>
            <small>{{ t(npc.area) }}</small>
            <h3>{{ t(npc.name) }}</h3>
          </div>
          <span>{{ t('人物手札') }} <AppIcon name="chevron" :size="14" /></span>
        </a>
        <p>{{ t(npc.description) }}</p>
        <button v-if="npc.point" class="ink-link" @click="$emit('map', `npc:${npc.id}`)">
          {{ t('查看活动范围') }} <AppIcon name="arrow" :size="14" />
        </button>
      </article>
    </div>
    <div v-else class="field-inner">
      <p class="section-kicker">{{ t('FIELD NOTES') }}</p>
      <h2 class="field-title">{{ t('本队的交子怎么用') }}</h2>
      <p class="field-copy">
        {{
          t('与景区自营 NPC 互动可赚交子，仅限本队使用，不可转让或买卖。以下规则以现场裁判为准。')
        }}
      </p>
      <div class="journal-panel">
        <small>{{ t('情报处 · 隐藏任务') }}</small>
        <h3>{{ t('兑换藏宝线索') }}</h3>
        <p>{{ t('初、中、高级情报的方案示例为 20 / 50 / 100 交子。实际价格请向情报处确认。') }}</p>
      </div>
      <h3 class="field-subtitle">{{ t('北更楼附近 · 黑市商人的卡片') }}</h3>
      <article v-for="[name, price, rule] in tools" :key="name" class="directory-row">
        <div>
          <h3>{{ t(name) }}</h3>
          <p>{{ t(rule) }}</p>
        </div>
        <b class="directory-price">{{ price }} {{ t('交子') }}</b>
      </article>
    </div>
  </section>
</template>
