<script setup lang="ts">
import FieldHeading from './FieldHeading.vue'
import AppIcon from './AppIcon.vue'
import { days, experiences } from '../data/offsite'
defineProps<{ section: string }>()
const sections = [
  ['', '两天安排'],
  ['walk', '游览'],
  ['studio', '体验'],
  ['shows', '演出'],
] as const
function jumpToSecondDay() {
  document.getElementById('trip-day-02')?.scrollIntoView({ block: 'start' })
}
</script>
<template>
  <section class="field-page" aria-label="两天行程">
    <FieldHeading
      theme="journey"
      edition="TRAVEL JOURNAL"
      title="濮院两日记"
      note="苏州出发，循水入镇。两日的相聚与去处。"
      seal="同行"
    />
    <nav class="field-tabs" aria-label="行程内容">
      <a
        v-for="[key, label] in sections"
        :key="key"
        :href="`#itinerary${key ? '/' + key : ''}`"
        :aria-current="section === key ? 'page' : undefined"
        >{{ label }}</a
      >
    </nav>
    <div v-if="!section" class="field-inner">
      <section
        v-for="day in days"
        :id="`trip-day-${day.number}`"
        :key="day.number"
        class="trip-day"
      >
        <header class="day-heading">
          <span
            >DAY <b>{{ day.number }}</b></span
          >
          <h2>{{ day.title }}</h2>
          <button v-if="day.number === '01'" class="day-jump" @click="jumpToSecondDay">
            看第二天 ↓
          </button>
        </header>
        <ol class="timeline">
          <li v-for="row in day.rows" :key="row[0]">
            <div class="timeline-time">{{ row[0] }}</div>
            <h3>{{ row[1] }}</h3>
            <p>{{ row[2] }}</p>
            <a v-if="row.length === 5" class="ink-link" :href="`#${row[3]}`"
              >{{ row[4] }} <AppIcon name="arrow" :size="14"
            /></a>
            <a v-if="row[3] === 'itinerary/walk'" class="ink-link" href="#itinerary/studio"
              >查看体验 <AppIcon name="arrow" :size="14"
            /></a>
          </li>
        </ol>
      </section>
    </div>
    <div v-else-if="section === 'walk'" class="field-inner">
      <p class="section-kicker">DAY 02 · GUIDED WALK</p>
      <h2 class="field-title">跟讲解，走水巷</h2>
      <p class="field-copy">
        10:00–12:00，约 45 人一组。已报名体验的同事按自己的安排出发，无需同时参加讲解。
      </p>
      <div class="journal-panel">
        <small>沿途风景</small>
        <h3>漱芳禅园 · 濮川诗社 · 梅泾剧场</h3>
        <p>这是行程资料推荐的看点；集合处和当天游览顺序请听从讲解员安排。</p>
      </div>
      <a class="field-action" href="#map"><AppIcon name="map" :size="18" /> 打开古镇导览</a>
    </div>
    <div v-else-if="section === 'studio'" class="field-inner">
      <p class="section-kicker">DAY 02 · WORKSHOPS</p>
      <h2 class="field-title">给自己留一件手作</h2>
      <p class="field-copy">按已报名项目参加。以下为方案团队价，不代表实时库存或报名成功。</p>
      <article v-for="item in experiences" :key="item[0]" class="directory-row">
        <div>
          <small>{{ item[1] }}</small>
          <h3>{{ item[0] }}</h3>
          <p v-if="item[4]">{{ item[4] }}</p>
        </div>
        <div class="directory-meta">
          <strong>¥{{ item[3] }}</strong
          ><small>约 {{ item[2] }} 分钟</small>
        </div>
      </article>
    </div>
    <div v-else class="field-inner">
      <p class="section-kicker">ON STAGE · 今日演艺</p>
      <h2 class="field-title">看戏，先看当天场次</h2>
      <p class="field-copy">
        园内节目随日调整，不把示例时间当作实际排期。微信中长按识别下方小程序码；也可在微信搜索「濮院时尚古镇」查看演艺时间表。
      </p>
      <figure class="show-code">
        <img
          src="/art/offsite-shows.png"
          width="216"
          height="216"
          alt="濮院时尚古镇演艺时间表微信小程序码"
        />
        <figcaption>景区演艺时间表 · 以当天公告为准</figcaption>
      </figure>
    </div>
  </section>
</template>
