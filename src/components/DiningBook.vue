<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from './AppIcon.vue'
import FieldHeading from './FieldHeading.vue'
import { dinnerSpots } from '../data/offsite'
import { matchesSearch } from '../data/catalog'
defineProps<{ favorites: string[] }>()
defineEmits<{ save: [id: string]; map: [id: string] }>()
const query = ref(''),
  group = ref('全部')
function clearFilters() {
  query.value = ''
  group.value = '全部'
}
const shown = computed(() =>
  dinnerSpots.filter(
    (s) =>
      (group.value === '全部' || s.group === group.value) &&
      matchesSearch(query.value, s.name, s.style),
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
    />
    <div class="field-inner">
      <div class="dining-note">
        <AppIcon name="bowl" :size="22" />
        <div>
          <b>自由晚餐 · 16:30 起</b>
          <p>方案参考人均 ¥80–100。两天的团队午餐另见<a href="#itinerary">行程</a>。</p>
        </div>
      </div>
      <label class="book-search"
        ><AppIcon name="search" :size="18" /><input
          v-model="query"
          name="dining"
          type="search"
          aria-label="搜索餐厅"
          placeholder="搜索店名、菜系…"
      /></label>
      <div class="dining-filters" aria-label="餐厅分类">
        <button
          v-for="g in ['全部', '水乡家常', '特色风味']"
          :key="g"
          :aria-pressed="group === g"
          @click="group = g"
        >
          {{ g }}
        </button>
      </div>
      <div class="field-section-head">
        <h2 class="field-title">古镇餐桌</h2>
        <span class="section-count">{{ shown.length }} 家推荐</span>
      </div>
      <article v-for="s in shown" :key="s.id" class="directory-row dinner-row">
        <div>
          <small>{{ s.style }}</small>
          <h3>{{ s.name }}</h3>
          <p>
            约 {{ s.seats }} 个餐位
            <button v-if="s.placeId" class="ink-link" @click="$emit('map', s.placeId)">
              在地图查看
            </button>
          </p>
        </div>
        <button
          class="dining-save"
          :class="{ saved: favorites.includes(`restaurant:${s.id}`) }"
          :aria-pressed="favorites.includes(`restaurant:${s.id}`)"
          :aria-label="`${favorites.includes(`restaurant:${s.id}`) ? '取消收藏' : '收藏'}${s.name}`"
          @click="$emit('save', s.id)"
        >
          <AppIcon name="heart" :size="18" />
        </button>
      </article>
      <div v-if="!shown.length" class="journal-panel">
        <h3>没有找到这家餐厅</h3>
        <button class="ink-link" @click="clearFilters">查看全部餐厅 →</button>
      </div>
      <p class="field-fine">餐位为总容量，不代表当晚余位；营业与价格以门店为准。</p>
    </div>
  </section>
</template>
