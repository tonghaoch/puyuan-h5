<script setup lang="ts">
import { publicAsset } from '../lib/public-asset'
import { t } from '../i18n'
import FieldHeading from './FieldHeading.vue'
import ChapterTabs from './ChapterTabs.vue'
import AppIcon from './AppIcon.vue'
import { days, experiences } from '../data/offsite'
defineProps<{ section: string }>()
const sections = [
  ['', '两天安排'],
  ['walk', '游览'],
  ['studio', '体验'],
  ['shows', '演出'],
] as const
function jumpToDay(number: '01' | '02') {
  const day = document.getElementById(`trip-day-${number}`)
  if (!day) return
  day.scrollIntoView({ block: 'start' })
  day.focus({ preventScroll: true })
}
</script>
<template>
  <section class="field-page trip-book" :aria-label="t('两天行程')">
    <FieldHeading
      theme="journey"
      edition="TRAVEL JOURNAL"
      title="濮院两日记"
      note="苏州出发，循水入镇。两日的相聚与去处。"
      seal="同行"
    >
      <template #art>
        <img
          class="journey-print"
          :src="publicAsset('/art/journal-journey.svg')"
          width="320"
          height="236"
          alt=""
        />
      </template>
    </FieldHeading>
    <ChapterTabs label="行程内容" base="#itinerary" :items="sections" :current="section" />
    <div v-if="!section" class="field-inner">
      <section
        v-for="day in days"
        :id="`trip-day-${day.number}`"
        :key="day.number"
        class="trip-day"
        :aria-labelledby="`day-title-${day.number}`"
        tabindex="-1"
      >
        <header class="trip-chapter">
          <span class="day-number" :aria-label="t(day.number === '01' ? '第一天' : '第二天')">
            {{ t('DAY') }} <b>{{ day.number }}</b>
          </span>
          <div>
            <p class="day-route">{{ t(day.number === '01' ? '苏州 → 濮院' : '濮院 → 苏州') }}</p>
            <h2 :id="`day-title-${day.number}`">{{ t(day.title) }}</h2>
          </div>
          <button
            class="chapter-turn"
            type="button"
            :aria-controls="day.number === '01' ? 'trip-day-02' : 'trip-day-01'"
            @click="jumpToDay(day.number === '01' ? '02' : '01')"
          >
            {{ t(day.number === '01' ? '看第二天' : '回第一天') }}
            <span aria-hidden="true">{{ day.number === '01' ? '↓' : '↑' }}</span>
          </button>
        </header>
        <ol class="trip-entries" role="list">
          <li v-for="row in day.rows" :key="row[0]" class="trip-entry">
            <div class="entry-time">{{ t(row[0]) }}</div>
            <div class="entry-body">
              <h3>{{ t(row[1]) }}</h3>
              <p>{{ t(row[2]) }}</p>
              <div v-if="row.length === 5" class="entry-links">
                <a class="ink-link" :href="`#${row[3]}`">
                  {{ t(row[4]) }} <AppIcon name="arrow" :size="14" />
                </a>
                <a v-if="row[3] === 'itinerary/walk'" class="ink-link" href="#itinerary/studio">
                  {{ t('查看体验') }} <AppIcon name="arrow" :size="14" />
                </a>
              </div>
            </div>
          </li>
        </ol>
      </section>
    </div>
    <div v-else-if="section === 'walk'" class="field-inner">
      <p class="section-kicker">{{ t('DAY 02 · GUIDED WALK') }}</p>
      <h2 class="field-title">{{ t('跟讲解，走水巷') }}</h2>
      <p class="field-copy">
        {{ t('10:00–12:00，约 45 人一组。已报名体验的同事按自己的安排出发，无需同时参加讲解。') }}
      </p>
      <div class="journal-panel">
        <small>{{ t('沿途风景') }}</small>
        <h3>{{ t('漱芳禅园 · 濮川诗社 · 梅泾剧场') }}</h3>
        <p>{{ t('这是行程资料推荐的看点；集合处和当天游览顺序请听从讲解员安排。') }}</p>
      </div>
      <a class="field-action" href="#map"
        ><AppIcon name="map" :size="18" /> {{ t('打开古镇导览') }}</a
      >
    </div>
    <div v-else-if="section === 'studio'" class="field-inner">
      <p class="section-kicker">{{ t('DAY 02 · WORKSHOPS') }}</p>
      <h2 class="field-title">{{ t('给自己留一件手作') }}</h2>
      <p class="field-copy">
        {{ t('按已报名项目参加。以下为方案团队价，不代表实时库存或报名成功。') }}
      </p>
      <article v-for="item in experiences" :key="item[0]" class="directory-row">
        <div>
          <small>{{ t(item[1]) }}</small>
          <h3>{{ t(item[0]) }}</h3>
          <p v-if="item[4]">{{ t(item[4]) }}</p>
        </div>
        <div class="directory-meta">
          <strong>¥{{ item[3] }}</strong
          ><small>{{ t('约 {count} 分钟', { count: item[2] }) }}</small>
        </div>
      </article>
    </div>
    <div v-else class="field-inner">
      <p class="section-kicker">{{ t('ON STAGE · 今日演艺') }}</p>
      <h2 class="field-title">{{ t('看戏，先看当天场次') }}</h2>
      <p class="field-copy">
        {{
          t(
            '园内节目随日调整，不把示例时间当作实际排期。微信中长按识别下方小程序码；也可在微信搜索「濮院时尚古镇」查看演艺时间表。',
          )
        }}
      </p>
      <figure class="show-code">
        <img
          :src="publicAsset('/art/offsite-shows.png')"
          width="216"
          height="216"
          :alt="t('濮院时尚古镇演艺时间表微信小程序码')"
        />
        <figcaption>{{ t('景区演艺时间表 · 以当天公告为准') }}</figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.trip-book {
  --trip-ink: #304e41;
  --tab-ink: var(--trip-ink);
  --trip-rule: #d7ceba;
  container-type: inline-size;
}
.journey-print {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: right center;
}
.trip-book .field-inner {
  max-width: 46rem;
  margin-inline: auto;
  padding: 22px clamp(16px, 4%, 32px) 36px;
}
.trip-day {
  --chapter-ink: var(--trip-ink);
  scroll-margin-block-start: 4rem;
}
.trip-day + .trip-day {
  --chapter-ink: #825034;
  margin-top: 28px;
}
.trip-day:focus-visible {
  outline: 2px solid var(--chapter-ink);
  outline-offset: 4px;
}
.trip-chapter {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: clamp(8px, 2.5%, 16px);
  border-block: 2px solid var(--chapter-ink);
  border-bottom: 1px solid var(--trip-rule);
  padding: 12px 0;
}
.day-number {
  display: grid;
  place-items: center;
  align-content: center;
  width: 46px;
  min-height: 52px;
  background: var(--chapter-ink);
  color: #fff3d8;
  font: 650 10px/1.25 sans-serif;
  letter-spacing: 0.14em;
}
.day-number b {
  font:
    500 28px/1 Georgia,
    serif;
  letter-spacing: 0;
}
.day-route {
  color: var(--chapter-ink);
  font-size: 11px;
  letter-spacing: 0.12em;
}
.trip-chapter h2 {
  margin-top: 3px;
  color: #293d32;
  font: 650 22px/1.35 var(--serif);
  text-wrap: balance;
}
.chapter-turn {
  padding: 0 4px;
  min-height: 44px;
  color: var(--chapter-ink);
  font-size: 13px;
  white-space: nowrap;
}
.chapter-turn span {
  display: inline-grid;
  place-items: center;
  width: 19px;
  height: 19px;
  border: 1px solid var(--trip-rule);
  border-radius: 50%;
}
.chapter-turn:hover,
.entry-links a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}
.trip-entries {
  margin: 20px 0 0 5px;
  padding: 0;
  list-style: none;
}
.trip-entry {
  position: relative;
  display: grid;
  gap: 3px 20px;
  border-inline-start: 1px solid var(--trip-rule);
  padding: 0 0 19px 19px;
}
.trip-entry:last-child {
  border-color: transparent;
  padding-bottom: 0;
}
.trip-entry::before {
  position: absolute;
  content: '';
  inset: 5px auto auto -5px;
  width: 7px;
  height: 7px;
  border: 1px solid var(--chapter-ink);
  border-radius: 50%;
  background: #faf7ee;
}
.trip-entry:is(:first-child, :last-child)::before {
  background: var(--chapter-ink);
}
.entry-time {
  color: var(--chapter-ink);
  font:
    650 13px/1.5 ui-monospace,
    monospace;
  font-variant-numeric: tabular-nums;
}
.entry-body h3 {
  color: #2e3b32;
  font: 650 18px/1.45 var(--serif);
}
.entry-body p {
  margin-top: 3px;
  color: #596154;
  font-size: 14px;
  line-height: 1.65;
}
.entry-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0 16px;
}
.entry-links .ink-link {
  margin: 0;
  min-height: 44px;
  color: var(--trip-ink);
}
@container (min-width: 32rem) {
  .trip-entry {
    grid-template-columns: 6.5rem minmax(0, 1fr);
  }
  .entry-time {
    padding-top: 3px;
  }
  .trip-entry::before {
    top: 8px;
  }
}
@container (max-width: 22rem) {
  .trip-chapter h2 {
    font-size: 19px;
  }
  .chapter-turn span {
    width: auto;
    border: 0;
  }
}
</style>
