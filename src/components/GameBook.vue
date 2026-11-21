<script setup lang="ts">
import FieldHeading from './FieldHeading.vue'
import AppIcon from './AppIcon.vue'
import { gameSites, wanderers, tools, roamingAreas } from '../data/offsite'
defineProps<{ section: string }>()
defineEmits<{ open: [id: string]; map: [id: string] }>()
const sections = [
  ['', '点位挑战'],
  ['roaming', '游走 NPC'],
  ['tokens', '交子与道具'],
] as const
</script>
<template>
  <section class="field-page" aria-label="游戏手册">
    <FieldHeading
      theme="games"
      edition="FIELD QUESTS"
      title="濮院诗简"
      note="一首散落水乡的诗，等你们组队修复。"
      seal="寻诗"
    />
    <nav class="field-tabs" aria-label="游戏内容">
      <a
        v-for="[key, label] in sections"
        :key="key"
        :href="`#games${key ? '/' + key : ''}`"
        :aria-current="section === key ? 'page' : undefined"
        >{{ label }}</a
      >
    </nav>
    <div v-if="!section" class="field-inner">
      <div class="field-section-head">
        <div>
          <p class="section-kicker">CHAPTER 01</p>
          <h2 class="field-title">沿旗寻关</h2>
        </div>
        <span class="section-count">7 处 · 8 项挑战</span>
      </div>
      <p class="field-copy">
        领取乱码诗碑拓片，按地图朱旗找到守关人。完成挑战收集词条，最后拼出诗篇，交裁判校验。
      </p>
      <a
        v-for="(site, i) in gameSites"
        :key="site.id"
        class="quest-row"
        :href="`#games/task/${site.id}`"
        @click.exact.prevent="$emit('open', site.id)"
      >
        <span class="quest-index">{{ String(i + 1).padStart(2, '0') }}</span>
        <div>
          <small>{{ site.place }}</small>
          <h3>{{ site.challenges.map((c) => c.name).join(' / ') }}</h3>
        </div>
        <AppIcon name="chevron" :size="16" />
      </a>
    </div>
    <div v-else-if="section === 'roaming'" class="field-inner">
      <p class="section-kicker">ENCOUNTERS</p>
      <h2 class="field-title">巷中遇见谁</h2>
      <p class="field-copy">以下是活动范围，不是实时位置。在附近留意角色装扮，遇见时再触发挑战。</p>
      <article v-for="[name, area, rule] in wanderers" :key="name" class="journal-panel">
        <small>{{ area }}</small>
        <h3>{{ name }}</h3>
        <p>{{ rule }}</p>
        <button v-if="roamingAreas[area]" class="ink-link" @click="$emit('map', `area:${area}`)">
          查看活动范围 <AppIcon name="arrow" :size="14" />
        </button>
      </article>
    </div>
    <div v-else class="field-inner">
      <p class="section-kicker">FIELD NOTES</p>
      <h2 class="field-title">本队的交子怎么用</h2>
      <p class="field-copy">
        与景区自营 NPC 互动可赚交子，仅限本队使用，不可转让或买卖。以下规则以现场裁判为准。
      </p>
      <div class="journal-panel">
        <small>情报处 · 隐藏任务</small>
        <h3>兑换藏宝线索</h3>
        <p>初、中、高级情报的方案示例为 20 / 50 / 100 交子。实际价格请向情报处确认。</p>
      </div>
      <h3 class="field-subtitle">北更楼附近 · 黑市商人的卡片</h3>
      <article v-for="[name, price, rule] in tools" :key="name" class="directory-row">
        <div>
          <h3>{{ name }}</h3>
          <p>{{ rule }}</p>
        </div>
        <b class="directory-price">{{ price }} 交子</b>
      </article>
    </div>
  </section>
</template>
