<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from './AppIcon.vue'
import FieldHeading from './FieldHeading.vue'
import ChapterTabs from './ChapterTabs.vue'
import { dinnerSpots } from '../data/offsite'
import { matchesSearch } from '../data/catalog'
const props = defineProps<{ favorites: string[] }>()
defineEmits<{ save: [id: string]; map: [id: string] }>()
const query = ref('')
const group = ref('全部')
const categories = ['全部', '水乡家常', '特色风味'].map((name) => [name, name] as const)
const searchInput = ref<HTMLInputElement | null>(null)
const entries = dinnerSpots.map((spot, index) => ({
  ...spot,
  number: String(index + 1).padStart(2, '0'),
}))

function isSaved(id: string) {
  return props.favorites.includes(`restaurant:${id}`)
}
function clearFilters() {
  query.value = ''
  group.value = '全部'
  searchInput.value?.focus()
}
const shown = computed(() =>
  entries.filter(
    (spot) =>
      (group.value === '全部' || spot.group === group.value) &&
      matchesSearch(query.value, spot.name, spot.style),
  ),
)
</script>
<template>
  <section class="field-page" aria-label="餐厅推荐">
    <FieldHeading
      theme="food"
      edition="DINING NOTES"
      title="寻味濮院"
      note="第一天的自由晚餐，从一桌水乡菜开始。"
      seal="食记"
    >
      <template #art>
        <img class="dining-art" src="/art/journal-dining.svg" width="300" height="220" alt="" />
      </template>
    </FieldHeading>
    <div class="field-inner dining-inner">
      <section class="supper-slip" aria-labelledby="supper-title">
        <h2 id="supper-title"><AppIcon name="bowl" :size="18" /> 第一天 · 自由晚餐</h2>
        <dl class="supper-facts">
          <div>
            <dt>晚餐时间</dt>
            <dd><time datetime="16:30">16:30</time> <small>起</small></dd>
          </div>
          <div>
            <dt>参考人均预算</dt>
            <dd><small>¥</small>80–100</dd>
          </div>
        </dl>
        <p>两天的团队午餐另见<a href="#itinerary">行程</a>。</p>
      </section>
      <div class="field-section-head directory-head">
        <h2 class="field-title">古镇餐桌</h2>
        <span class="section-count" role="status" aria-atomic="true"
          >{{ shown.length }} 家推荐</span
        >
      </div>
      <label class="book-search"
        ><AppIcon name="search" :size="18" /><input
          ref="searchInput"
          v-model="query"
          name="dining"
          type="search"
          aria-label="搜索餐厅"
          placeholder="搜索店名、菜系…"
      /></label>
      <ChapterTabs
        class="dining-filters"
        label="餐厅分类"
        :items="categories"
        :current="group"
        @select="group = $event"
      />
      <article v-for="spot in shown" :key="spot.id" class="directory-row dinner-row">
        <span class="entry-number" aria-hidden="true">{{ spot.number }}</span>
        <div class="entry-copy">
          <h3>{{ spot.name }}</h3>
          <p class="entry-detail">
            <span>{{ spot.style }}</span><span>约 {{ spot.seats }} 个餐位</span>
          </p>
          <button
            v-if="spot.placeId"
            type="button"
            class="ink-link"
            @click="$emit('map', spot.placeId)"
          >
            <AppIcon name="pin" :size="14" /> 在地图查看
          </button>
        </div>
        <button
          class="dining-save"
          type="button"
          :class="{ saved: isSaved(spot.id) }"
          :aria-pressed="isSaved(spot.id)"
          :aria-label="`${isSaved(spot.id) ? '取消收藏' : '收藏'}${spot.name}`"
          @click="$emit('save', spot.id)"
        >
          <AppIcon name="heart" :size="18" />
          <span>{{ isSaved(spot.id) ? '已收藏' : '收藏' }}</span>
        </button>
      </article>
      <div v-if="!shown.length" class="empty-table">
        <AppIcon name="search" :size="22" />
        <h3>没有找到这家餐厅</h3>
        <p>试试更短的店名、菜系，或切换餐厅分类。</p>
        <button type="button" class="ink-link" @click="clearFilters">查看全部餐厅 →</button>
      </div>
      <p v-else class="field-fine">餐位为总容量，不代表当晚余位；营业与价格以门店为准。</p>
    </div>
  </section>
</template>

<style scoped>
.dining-art {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: right bottom;
}
.dining-inner {
  --cinnabar: #883e2c;
  --rule: #d7cdb5;
  max-width: 720px;
  margin-inline: auto;
}
.supper-slip {
  padding: 14px clamp(14px, 4%, 24px) 10px;
  margin-bottom: 24px;
  background: #f3eddd;
  border-block: 1px solid var(--rule);
  border-top: 3px double #b29975;
}
.supper-slip h2 {
  display: flex;
  align-items: center;
  gap: 7px;
  font: 650 15px/1.5 var(--serif);
  color: var(--cinnabar);
}
.supper-facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 14px 0 8px;
}
.supper-facts > div + div {
  padding-left: 14%;
  border-left: 1px solid var(--rule);
}
.supper-facts dt,
.supper-slip p {
  font-size: 13px;
  line-height: 1.65;
  color: #605e50;
}
.supper-facts dd {
  margin: 2px 0 0;
  color: #533829;
  font:
    500 clamp(25px, 7vw, 32px)/1.15 Georgia,
    var(--serif);
  font-variant-numeric: lining-nums tabular-nums;
}
.supper-facts small {
  font-size: 0.6em;
}
.supper-slip p {
  border-top: 1px dashed var(--rule);
  padding-top: 8px;
}
.supper-slip a {
  text-decoration: underline;
  text-underline-offset: 3px;
  color: #38533c;
}
.directory-head::after {
  content: '';
  order: 1;
  flex: 1;
  border-top: 1px solid var(--rule);
}
.directory-head .section-count {
  order: 2;
  color: var(--cinnabar);
}
.book-search:focus-within {
  outline: 2px solid var(--cinnabar);
  outline-offset: 2px;
}
.book-search input {
  min-height: 44px;
  font-size: 16px;
  outline: none;
}
.dining-filters {
  --tab-ink: #694831;
  margin: 8px 0 14px;
}
.dinner-row {
  align-items: flex-start;
  gap: clamp(8px, 3%, 16px);
  padding: 14px 0;
}
.entry-number {
  margin-top: 5px;
  padding-bottom: 3px;
  border-bottom: 2px solid #d5b79c;
  color: var(--cinnabar);
  font:
    italic 16px/1 Georgia,
    serif;
  font-variant-numeric: tabular-nums;
}
.entry-copy {
  flex: 1;
  min-width: 0;
}
.entry-copy h3 {
  margin: 0 0 3px;
}
.entry-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 0 12px;
}
.entry-detail > :last-child {
  color: #696558;
}
.dinner-row .ink-link,
.empty-table .ink-link {
  min-height: 44px;
  padding-inline: 0;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.dining-save {
  display: grid;
  flex: none;
  place-content: center;
  justify-items: center;
  gap: 3px;
  padding: 0;
  color: #616753;
  font-size: 12px;
}
.dining-save.saved {
  color: var(--cinnabar);
  background: #f2e4d6;
  border-radius: 4px;
}
.empty-table {
  border-block: 1px dashed var(--rule);
  padding: 22px 10px 12px;
  text-align: center;
  background: #f4efe3;
  color: #5b584a;
}
.empty-table h3 {
  margin: 6px 0;
  font: 650 19px/1.5 var(--serif);
}
.empty-table p {
  font-size: 13px;
  line-height: 1.7;
}
.field-fine {
  margin-top: 0;
  padding-top: 12px;
  border-top: 1px solid var(--rule);
}
</style>
