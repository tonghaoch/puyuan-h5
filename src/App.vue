<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import MainNav from './components/MainNav.vue'
import TripBook from './components/TripBook.vue'
import GameBook from './components/GameBook.vue'
import EncounterDetail from './components/EncounterDetail.vue'
import QuestToken from './components/QuestToken.vue'
import EncounterToken from './components/EncounterToken.vue'
import DiningBook from './components/DiningBook.vue'
import { dinnerSpots, questForRoute, wanderers, type Quest } from './data/offsite'
import ParkMap from './components/ParkMap.vue'
import AppDialog from './components/AppDialog.vue'
import GeoLocationMap from './components/GeoLocationMap.vue'
import landmarkModels from './data/landmark-models.json'
import {
  activities,
  restaurants,
  places,
  categoryLabels,
  mapLayers,
  placeById,
  selectionKey,
  type Tab,
  type MapLayer,
  type Selection,
} from './data/catalog'
import { useLocation } from './lib/location'
import { walkPreviewEnabled } from './lib/walk-preview'
import { publicAsset } from './lib/public-asset'
import { t, locale, languageAction, toggleLanguage, matchesBilingual } from './i18n'
import { dayLabel, shanghaiDate, shiftDay, sessionStatus } from './lib/time'

type Overlay = 'favorites' | null
const tab = ref<Tab>('map')
const bookSection = ref('')
const activeQuest = ref<Quest>()
const activeNpc = ref<(typeof wanderers)[number]>()
const questOrigin = ref<'map' | 'games' | null>(null)
let gameOpener: HTMLElement | undefined
const selection = ref<Selection | null>(null)
const detailModelId = ref<string>()
const overlay = ref<Overlay>(null)
const showLocation = ref(false)
const query = ref('')
const visibleLayers = reactive<Record<MapLayer, boolean>>({ quest: true, npc: true, places: false })
const activityFilter = ref('all')
const dayFilter = ref(0)
const focusRequest = ref<{ id: string; nonce: number } | null>(null)
const now = ref(Date.now())
const pageVisible = ref(!document.hidden)
const toast = ref('')
let toastTimer: ReturnType<typeof setTimeout> | undefined
let clockTimer: ReturnType<typeof setInterval> | undefined
const media = window.matchMedia('(prefers-reduced-motion: reduce)')
function stored(key: string) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}
function save(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    /* Browsing remains available when storage is denied. */
  }
}
const motion = ref(!media.matches)
const validKeys = new Set([
  ...places.map((p) => `place:${p.id}`),
  ...activities.map((a) => `activity:${a.id}`),
  ...restaurants.map((r) => `restaurant:${r.id}`),
  ...dinnerSpots.map((r) => `restaurant:${r.id}`),
])
function loadFavorites(): string[] {
  try {
    const data: unknown = JSON.parse(stored('puyuan.favorites') || '[]')
    return Array.isArray(data)
      ? data.filter((v): v is string => typeof v === 'string' && validKeys.has(v))
      : []
  } catch {
    return []
  }
}
const favorites = ref<string[]>(loadFavorites())
const location = useLocation(() => !walkPreviewEnabled && pageVisible.value && tab.value === 'map')
const activeEntry = computed(() => activeQuest.value ?? activeNpc.value)
const mapEntry = computed(() => (tab.value === 'map' ? activeEntry.value : undefined))
const hasModal = computed(() => !!selection.value || !!overlay.value || !!mapEntry.value)
const motionActive = computed(
  () => motion.value && pageVisible.value && tab.value === 'map' && !hasModal.value,
)
const today = computed(() => shanghaiDate(new Date(now.value)))
function validSelection(kind: string, id: string): Selection | null {
  if (
    (kind === 'place' || kind === 'activity' || kind === 'restaurant') &&
    validKeys.has(`${kind}:${id}`)
  )
    return { kind, id }
  return null
}
function readRoute() {
  const [nextTab, kind, id, modelId] = window.location.hash.slice(1).split('/')
  if (kind === 'geopoint' || kind === 'guide') {
    route('map', false, true)
    return
  }
  tab.value =
    nextTab === 'food' || nextTab === 'activities' || nextTab === 'itinerary' || nextTab === 'games'
      ? nextTab
      : 'map'
  const sections =
    tab.value === 'itinerary'
      ? ['walk', 'studio', 'shows']
      : tab.value === 'games'
        ? ['roaming', 'tokens']
        : []
  bookSection.value = kind && sections.includes(kind) ? kind : ''
  const hadGameDetail = !!activeQuest.value || !!activeNpc.value
  activeQuest.value =
    (nextTab === 'map' || nextTab === 'games') && kind === 'task'
      ? questForRoute(id, modelId)
      : undefined
  activeNpc.value =
    (nextTab === 'map' || nextTab === 'games') && kind === 'npc'
      ? wanderers.find((npc) => npc.id === id)
      : undefined
  if (tab.value === 'games' && activeNpc.value) bookSection.value = 'roaming'
  questOrigin.value =
    window.history.state?.questOrigin ??
    (activeNpc.value && window.history.state?.puyuanModal ? 'map' : null)
  if (mapEntry.value) {
    visibleLayers[activeQuest.value ? 'quest' : 'npc'] = true
  }
  if (hadGameDetail && !activeQuest.value && !activeNpc.value && gameOpener?.isConnected) {
    const opener = gameOpener
    nextTick(() => {
      if (opener.getClientRects().length) opener.focus({ preventScroll: true })
    })
  }
  selection.value = kind && id ? validSelection(kind, id) : null
  detailModelId.value = kind === 'place' ? modelId : undefined
  overlay.value = kind === 'favorites' ? kind : null
  showLocation.value = !walkPreviewEnabled && tab.value === 'map' && kind === 'location'
}
function route(path: string, modal = false, replace = false) {
  const method = replace ? 'replaceState' : 'pushState'
  window.history[method]({ puyuanModal: modal }, '', `#${path}`)
  readRoute()
}
function changeTab(next: Tab) {
  if (next !== tab.value || hasModal.value || activeEntry.value || bookSection.value) {
    query.value = ''
    route(next)
  }
}
function openNpc(id: string, opener: HTMLElement) {
  openEntry('npc', id, opener)
}
function openQuest(id: string, opener: HTMLElement) {
  openEntry('task', id, opener)
}
function openEntry(kind: 'npc' | 'task', id: string, opener: HTMLElement) {
  gameOpener = opener
  const path = `${tab.value}/${kind}/${id}`
  window.history.pushState({ questOrigin: tab.value }, '', `#${path}`)
  readRoute()
  if (!mapEntry.value)
    nextTick(() =>
      document.querySelector<HTMLElement>('.quest-detail')?.focus({ preventScroll: true }),
    )
}
function leaveQuest() {
  if (questOrigin.value) window.history.back()
  else route(tab.value === 'games' && activeNpc.value ? 'games/roaming' : tab.value, false, true)
}
function openSelection(next: Selection, modelId?: string) {
  route(`${tab.value}/${next.kind}/${next.id}${modelId ? `/${modelId}` : ''}`, true, hasModal.value)
}
function closeModal() {
  if (window.history.state?.puyuanModal) window.history.back()
  else route(tab.value, false, true)
}
readRoute()
function notify(message: string) {
  toast.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = ''
  }, 2600)
}
function toggleFavorite(item: Selection) {
  const key = selectionKey(item)
  const exists = favorites.value.includes(key)
  favorites.value = exists ? favorites.value.filter((k) => k !== key) : [...favorites.value, key]
  save('puyuan.favorites', JSON.stringify(favorites.value))
  notify(exists ? '已从收藏中移除' : '已收藏，把美好留在行程里')
}
function isFavorite(item: Selection) {
  return favorites.value.includes(selectionKey(item))
}
function resetActivityFilters() {
  query.value = ''
  activityFilter.value = 'all'
}
function viewOnMap(id: string) {
  query.value = ''
  const npcArea = id.startsWith('npc:')
  visibleLayers[npcArea ? 'npc' : id.startsWith('quest:') ? 'quest' : 'places'] = true
  route('map', false, !npcArea)
  focusRequest.value = { id, nonce: Date.now() }
  notify(npcArea ? '已标出角色活动范围，非实时位置' : '已为你找到地图中的位置')
}
const selectedDinner = computed(() =>
  selection.value?.kind === 'restaurant'
    ? dinnerSpots.find((s) => s.id === selection.value!.id)
    : undefined,
)
const selectedDay = computed(() => shiftDay(today.value, dayFilter.value))
const visibleActivities = computed(() =>
  activities.filter(
    (a) =>
      (activityFilter.value === 'all' || a.category === activityFilter.value) &&
      a.sessions.some((s) => shanghaiDate(new Date(s.start)) === selectedDay.value) &&
      matchesBilingual(query.value, a.name, a.subtitle, placeById(a.placeId)!.name, ...a.tags),
  ),
)
const currentActivity = computed(() =>
  selection.value?.kind === 'activity'
    ? activities.find((a) => a.id === selection.value!.id)
    : undefined,
)
const currentRestaurant = computed(() =>
  selection.value?.kind === 'restaurant'
    ? restaurants.find((r) => r.id === selection.value!.id)
    : undefined,
)
const currentPlace = computed(() => {
  if (selection.value?.kind === 'place') return placeById(selection.value.id)
  const id = currentActivity.value?.placeId || currentRestaurant.value?.placeId
  return id ? placeById(id) : undefined
})
const detail = computed(() => {
  const item = currentActivity.value || currentRestaurant.value || currentPlace.value
  if (!item || !currentPlace.value) return null
  const models = landmarkModels.models.filter((entry) => entry.placeId === currentPlace.value!.id)
  const model =
    models.find((entry) => entry.id === detailModelId.value) ??
    models.find((entry) => entry.id !== 'temple-pagoda')
  const pagoda = model?.id === 'temple-pagoda'
  return {
    model,
    name: pagoda ? model.name : item.name,
    subtitle: pagoda ? model.finishLabel : item.subtitle,
    description: pagoda
      ? '导览按原图画出赭褐塔身、紧密的檐线和浅色多边形石台。上方深灰剪影是插画中可见的形状，不能据此认定它的结构或塔的实际层数。'
      : item.description,
    art: currentRestaurant.value?.art || currentPlace.value.art,
    category: currentRestaurant.value ? '寻味濮院' : categoryLabels[currentPlace.value.category],
    place: currentPlace.value,
  }
})
const placeActivities = computed(() =>
  activities.filter((a) => a.placeId === currentPlace.value?.id),
)
const placeRestaurants = computed(() =>
  restaurants.filter(
    (r) =>
      r.placeId === currentPlace.value?.id && !dinnerSpots.some((s) => s.placeId === r.placeId),
  ),
)
const linkedDinner = computed(() =>
  dinnerSpots.find((s) => s.placeId && s.placeId === currentPlace.value?.id),
)
const favoriteItems = computed(() =>
  favorites.value.flatMap((key) => {
    const [kind, id] = key.split(':')
    const sel = validSelection(kind!, id!)
    if (!sel) return []
    const item =
      sel.kind === 'place'
        ? placeById(sel.id)
        : sel.kind === 'activity'
          ? activities.find((a) => a.id === sel.id)
          : (restaurants.find((r) => r.id === sel.id) ?? dinnerSpots.find((r) => r.id === sel.id))
    if (!item) return []
    return [
      {
        selection: sel,
        name: item.name,
        subtitle: 'subtitle' in item ? item.subtitle : item.style,
        label: sel.kind === 'activity' ? '活动' : sel.kind === 'restaurant' ? '餐厅' : '地点',
      },
    ]
  }),
)
const locationMessage = computed(
  () =>
    ({
      idle: '点击下方按钮，允许设备获取你的位置。',
      loading: '正在获取位置，请稍候…',
      available: '正在更新设备位置',
      denied: '定位权限未开启。你可以继续浏览，或在系统设置中允许定位后重试。',
      unavailable: '当前环境暂不支持定位。请通过 HTTPS 地址在手机浏览器中打开。',
      timeout: '定位暂时超时，可以到开阔处后重试。',
      error: '暂时无法获取位置，请检查系统定位设置后重试。',
      stale: '位置已过期，正在等待新的定位。',
    })[location.state.value],
)
function visibility() {
  pageVisible.value = !document.hidden
  if (pageVisible.value) now.value = Date.now()
}
function pageHide() {
  pageVisible.value = false
}
function toggleMyLocation() {
  showLocation.value = !showLocation.value
  if (showLocation.value && ['loading', 'timeout', 'error', 'stale'].includes(location.state.value))
    location.retry()
}
function motionPreference() {
  motion.value = !media.matches
}
onMounted(() => {
  window.addEventListener('popstate', readRoute)
  window.addEventListener('hashchange', readRoute)
  document.addEventListener('visibilitychange', visibility)
  window.addEventListener('pagehide', pageHide)
  window.addEventListener('pageshow', visibility)
  media.addEventListener('change', motionPreference)
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 30000)
})
onBeforeUnmount(() => {
  window.removeEventListener('popstate', readRoute)
  window.removeEventListener('hashchange', readRoute)
  document.removeEventListener('visibilitychange', visibility)
  window.removeEventListener('pagehide', pageHide)
  window.removeEventListener('pageshow', visibility)
  media.removeEventListener('change', motionPreference)
  clearInterval(clockTimer)
  clearTimeout(toastTimer)
})
</script>

<template>
  <div
    class="app-shell"
    :class="{ 'reduced-motion': !motion, 'list-mode': tab !== 'map' }"
    :inert="hasModal || undefined"
  >
    <header class="app-header">
      <button class="brand" :aria-label="t('濮院漫游，返回地图')" @click="changeTab('map')">
        <span class="brand-mark"
          ><svg width="37" height="42" viewBox="0 0 42 46" fill="none">
            <path
              d="M4 13q6 1 17-8 9 8 17 8M9 15h24M12 17v18m18-18v18M6 38h30M17 35V22h8v13M3 43h36"
              stroke="currentColor"
              stroke-width="1.7"
            />
            <path d="M10 8q5 1 11-5 5 5 11 5" stroke="currentColor" stroke-width="1.5" /></svg
        ></span>
        <span class="brand-type"
          >{{ t('濮院漫游') }}<small>{{ t('PUYUAN · WANDER SLOWLY') }}</small></span
        >
      </button>

      <div class="header-actions">
        <button
          type="button"
          class="language-button"
          :aria-label="languageAction"
          :title="languageAction"
          @click="toggleLanguage"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 32 32"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
            focusable="false"
          >
            <path d="M6 1.5h20L30.5 6v20L26 30.5H6L1.5 26V6Z" fill="#faf4e6" stroke="#bca580" />
            <path d="m8 24 16-16" stroke="#c5b394" />
            <path
              d="m10.4 4.8 1.1 1.6M5.5 8h11.2m-3.1.3c-1.1 3.9-3.9 6.4-7.4 8m2-7.3c1.3 2.8 3.7 5.3 7.6 7"
              stroke="var(--lang-zh)"
              stroke-width="1.65"
            />
            <path
              d="M20.3 17.3h-4.8v8h4.8m-4.6-4.1h3.7m3 4.1v-5.6m0 2.5c.7-3.1 4.3-3.4 4.3-.3v3.4"
              stroke="var(--lang-en)"
              stroke-width="1.5"
            />
          </svg>
        </button>
      </div>
    </header>

    <main class="main-content">
      <section v-show="tab === 'map'" class="map-page reference-view" :aria-label="t('游园地图')">
        <ParkMap
          :places="places"
          :layers="visibleLayers"
          :focus-request="focusRequest"
          :motion="motionActive"
          :show-location="showLocation"
          :active-quest-id="activeQuest?.id"
          :active-npc-id="activeNpc?.id"
          @game="openQuest"
          @npc="openNpc"
          @select="(place) => openSelection({ kind: 'place', id: place.id })"
          @locate="toggleMyLocation"
        />
        <GeoLocationMap
          v-if="showLocation"
          id="map-location-note"
          :fix="location.fix.value"
          :now="now"
          :device-message="locationMessage"
          :can-retry="['denied', 'timeout', 'error', 'stale'].includes(location.state.value)"
          @retry="location.retry()"
        />
        <div class="map-topbar">
          <div class="filter-pills" role="group" :aria-label="t('地图图层')">
            <button
              v-for="layer in mapLayers"
              :key="layer.id"
              type="button"
              :data-layer="layer.id"
              :aria-pressed="visibleLayers[layer.id]"
              @click="visibleLayers[layer.id] = !visibleLayers[layer.id]"
            >
              <QuestToken v-if="layer.id === 'quest'" />
              <EncounterToken v-else-if="layer.id === 'npc'" />
              <AppIcon v-else name="lantern" :size="17" />
              {{ t(layer.name) }}
            </button>
          </div>
        </div>
        <div class="map-introduction">
          <p class="eyebrow"><span></span> {{ t('江 南 好 时 节') }}</p>
          <h1>
            {{ t('一入濮院') }}<br />{{ t('便是') }}<span>{{ t('江南') }}</span
            ><i class="title-seal">{{ t('慢') }}<br />{{ t('游') }}</i>
          </h1>
          <div class="intro-rule"><span></span><i>◇</i></div>
          <p class="intro-copy">
            {{ t('循水巷，过石桥，听一曲婉转。') }}<br />{{ t('把脚步放慢，让风景发生。') }}
          </p>
          <span class="intro-caption">{{ t('A LITTLE WANDER, A LOT TO DISCOVER.') }}</span>
        </div>
        <div v-if="visibleLayers.quest || visibleLayers.npc" class="map-bottom-note">
          <span v-if="visibleLayers.quest" class="quest-legend"
            ><QuestToken />{{ t('江湖令 · 团建挑战') }}</span
          >
          <span v-if="visibleLayers.npc" class="quest-legend"
            ><EncounterToken />{{ t('行走 NPC · 活动范围') }}</span
          >
          <span class="note-separator">/</span
          ><span class="map-hint">{{ t('拖动探索 · 双指缩放') }}</span>
        </div>
        <div class="map-vignette" aria-hidden="true"></div>
      </section>

      <TripBook v-if="tab === 'itinerary'" :key="bookSection" :section="bookSection" />
      <GameBook
        v-if="tab === 'games'"
        v-show="!activeEntry"
        :section="bookSection"
        @open="openQuest"
        @npc="openNpc"
        @map="viewOnMap"
      />
      <EncounterDetail
        v-if="activeEntry && !mapEntry"
        :key="activeEntry.id"
        :entry="activeEntry"
        tabindex="-1"
        @back="leaveQuest"
        @map="viewOnMap"
      />
      <DiningBook
        v-if="tab === 'food'"
        :favorites="favorites"
        @map="viewOnMap"
        @save="(id) => toggleFavorite({ kind: 'restaurant', id })"
      />

      <section
        v-if="tab === 'activities'"
        class="catalog-page activities-page"
        :aria-label="t('活动列表')"
      >
        <div class="catalog-heading">
          <div>
            <p class="eyebrow">{{ t('MOMENTS WORTH WANDERING FOR') }}</p>
            <h1>
              {{ t('好时光，') }}<span>{{ t('当有好相逢。') }}</span>
            </h1>
            <p>{{ t('听戏、寻艺、逛风物。在濮院，赴一场风雅之约。') }}</p>
          </div>
          <div class="heading-stamp">{{ t('雅') }}<br />{{ t('集') }}</div>
        </div>
        <div class="catalog-toolbar">
          <div class="text-filters" :aria-label="t('活动分类')">
            <button
              v-for="filter in [
                { id: 'all', label: '全部活动' },
                { id: 'performance', label: '水乡演艺' },
                { id: 'craft', label: '风物雅集' },
                { id: 'scenic', label: '古镇漫游' },
              ]"
              :key="filter.id"
              :class="{ active: activityFilter === filter.id }"
              :aria-pressed="activityFilter === filter.id"
              @click="activityFilter = filter.id"
            >
              {{ t(filter.label) }}
            </button>
          </div>
          <label class="search-field"
            ><AppIcon name="search" :size="18" /><input
              v-model="query"
              :aria-label="t('搜索活动')"
              :placeholder="t('寻找一场心动的相遇')" /><button
              v-if="query"
              class="clear-search"
              :aria-label="t('清空搜索')"
              @click.prevent="query = ''"
            >
              <AppIcon name="close" :size="15" /></button
          ></label>
        </div>
        <div class="activity-day-row">
          <div class="day-buttons">
            <button
              v-for="(label, index) in ['今天', '明天', '后天']"
              :key="label"
              :class="{ active: dayFilter === index }"
              :aria-pressed="dayFilter === index"
              @click="dayFilter = index"
            >
              {{ t(label) }}<small>{{ shiftDay(today, index).slice(5).replace('-', '.') }}</small>
            </button>
          </div>
          <span class="demo-label">{{ t('演示日程 · 非实际演出安排') }}</span>
        </div>
        <div class="activity-grid">
          <article v-for="activity in visibleActivities" :key="activity.id" class="activity-card">
            <button
              class="activity-art"
              :aria-label="t('查看{name}详情', { name: activity.name })"
              @click="openSelection({ kind: 'activity', id: activity.id })"
            >
              <img
                :src="publicAsset(`/art/${placeById(activity.placeId)?.art}.svg`)"
                :alt="t('{name}意境插画', { name: activity.name })"
                loading="lazy"
              /><span class="cover-category">{{ t(categoryLabels[activity.category]) }}</span>
            </button>
            <div class="activity-card-body">
              <div class="activity-time">
                <AppIcon name="clock" :size="14" />{{ activity.time
                }}<span
                  v-if="
                    dayFilter === 0 &&
                    sessionStatus(
                      activity.sessions.filter((s) => shanghaiDate(new Date(s.start)) === today),
                      now,
                    ) === 'ongoing'
                  "
                  class="live-label"
                  >{{ t('进行中') }}</span
                >
              </div>
              <button
                class="activity-title"
                @click="openSelection({ kind: 'activity', id: activity.id })"
              >
                <h2>{{ t(activity.name) }}</h2>
              </button>
              <p class="card-subtitle">{{ t(activity.subtitle) }}</p>
              <div class="tag-row">
                <span v-for="tag in activity.tags" :key="tag">{{ t(tag) }}</span>
              </div>
              <div class="activity-card-footer">
                <span
                  ><AppIcon name="pin" :size="14" />{{ t(placeById(activity.placeId)?.name) }}</span
                ><button @click="openSelection({ kind: 'activity', id: activity.id })">
                  {{ t('赴约详情') }}<AppIcon name="arrow" :size="17" />
                </button>
              </div>
            </div>
            <button
              class="activity-favorite"
              :class="{ saved: isFavorite({ kind: 'activity', id: activity.id }) }"
              :aria-label="
                t(
                  isFavorite({ kind: 'activity', id: activity.id })
                    ? '取消收藏{name}'
                    : '收藏{name}',
                  { name: activity.name },
                )
              "
              :aria-pressed="isFavorite({ kind: 'activity', id: activity.id })"
              @click="toggleFavorite({ kind: 'activity', id: activity.id })"
            >
              <AppIcon name="heart" :size="18" />
            </button>
          </article>
        </div>
        <div v-if="!visibleActivities.length" class="catalog-empty">
          <AppIcon name="fan" :size="38" />
          <h2>{{ t('暂时没有这类活动') }}</h2>
          <p>{{ t('试着换个关键词或分类，发现另一种相遇。') }}</p>
          <button class="primary-button" @click="resetActivityFilters">
            {{ t('查看全部活动') }}
          </button>
        </div>
        <p class="catalog-footnote">{{ t('— 不赶时间，只赴好时光 —') }}</p>
      </section>
    </main>
    <MainNav :current="tab" @navigate="changeTab" />
  </div>

  <Transition name="quest-rise" :css="motion" appear>
    <AppDialog v-if="mapEntry" class="quest-sheet" :label="mapEntry.name" @close="leaveQuest">
      <EncounterDetail :key="mapEntry.id" :entry="mapEntry" sheet />
    </AppDialog>
  </Transition>

  <Transition name="sheet">
    <AppDialog
      v-if="selection && (selectedDinner || detail)"
      :label="(selectedDinner || detail)!.name"
      @close="closeModal"
    >
      <div v-if="selectedDinner" class="simple-dialog">
        <p class="section-kicker">{{ t('自由晚餐 · 餐厅推荐') }}</p>
        <h2>{{ t(selectedDinner.name) }}</h2>
        <p>
          {{ t(selectedDinner.style) }} ·
          {{ t('约 {count} 个餐位', { count: selectedDinner.seats }) }}
        </p>
        <button
          v-if="selectedDinner.placeId"
          class="field-action"
          @click="viewOnMap(selectedDinner.placeId)"
        >
          {{ t('在地图中查看') }}
        </button>
      </div>
      <template v-else-if="detail">
        <div class="detail-hero" :class="{ 'model-hero': detail.model }">
          <img
            :src="
              publicAsset(
                detail.model?.heroAsset || detail.model?.asset || `/art/${detail.art}.svg`,
              )
            "
            :alt="t('{name}意境插画', { name: detail.name })"
          /><span class="detail-category">{{ t(detail.category) }}</span>
        </div>
        <div class="detail-body">
          <p class="eyebrow">{{ t('A MOMENT IN PUYUAN') }}</p>
          <h2>{{ t(detail.name) }}</h2>
          <p class="detail-subtitle">{{ t(detail.subtitle) }}</p>
          <p class="detail-description">{{ t(detail.description, { name: detail.place.name }) }}</p>
          <div class="detail-facts">
            <div>
              <AppIcon name="pin" :size="18" /><span
                ><small>{{ t('所在地点') }}</small
                >{{ t(detail.place.name) }}</span
              >
            </div>
            <div v-if="currentActivity">
              <AppIcon name="clock" :size="18" /><span
                ><small>{{ t(currentActivity.duration) }}</small
                >{{ currentActivity.time }}</span
              >
            </div>
            <div v-if="currentRestaurant">
              <AppIcon name="clock" :size="18" /><span
                ><small>{{ t('示例营业时间') }}</small
                >{{ currentRestaurant.hours }}</span
              >
            </div>
            <div v-if="currentRestaurant">
              <AppIcon name="tea" :size="18" /><span
                ><small>{{ t('示例人均') }}</small
                >¥{{ currentRestaurant.price }} {{ t('/ 人') }}</span
              >
            </div>
          </div>
          <div v-if="currentActivity" class="session-list">
            <h3>
              {{ t('场次一览') }} <span>{{ t('演示日程') }}</span>
            </h3>
            <div v-for="session in currentActivity.sessions" :key="session.start">
              <span
                >{{ dayLabel(session.start, new Date(now), locale) }}
                <small>{{
                  shanghaiDate(new Date(session.start)).slice(5).replace('-', '.')
                }}</small></span
              ><strong>{{ currentActivity.time }}</strong
              ><span class="session-state" :class="sessionStatus([session], now)">{{
                t(
                  { ongoing: '进行中', upcoming: '待开始', ended: '已结束' }[
                    sessionStatus([session], now)
                  ],
                )
              }}</span>
            </div>
          </div>
          <div
            v-if="
              selection.kind === 'place' &&
              (placeActivities.length || placeRestaurants.length || linkedDinner)
            "
            class="place-content"
          >
            <h3>{{ t('在这里，可以遇见') }}</h3>
            <button
              v-if="linkedDinner"
              @click="openSelection({ kind: 'restaurant', id: linkedDinner.id })"
            >
              <AppIcon name="bowl" /><span
                ><strong>{{ t(linkedDinner.name) }}</strong
                ><small>{{ t('自由晚餐推荐 ·') }} {{ t(linkedDinner.style) }}</small></span
              ><AppIcon name="chevron" />
            </button>
            <button
              v-for="activity in placeActivities"
              :key="activity.id"
              @click="openSelection({ kind: 'activity', id: activity.id })"
            >
              <AppIcon name="fan" :size="20" /><span
                ><strong>{{ t(activity.name) }}</strong
                ><small>{{ activity.time }}</small></span
              ><AppIcon name="chevron" :size="17" /></button
            ><button
              v-for="restaurant in placeRestaurants"
              :key="restaurant.id"
              @click="openSelection({ kind: 'restaurant', id: restaurant.id })"
            >
              <AppIcon name="tea" :size="20" /><span
                ><strong>{{ t(restaurant.name) }}</strong
                ><small
                  >{{ t(restaurant.cuisine) }} {{ t('· 示例人均 ¥') }}{{ restaurant.price }}</small
                ></span
              ><AppIcon name="chevron" :size="17" />
            </button>
          </div>
          <div class="demo-notice">
            <AppIcon name="info" :size="15" />
            <p>
              {{
                t(
                  '当前为游园体验版。地点布局、活动、营业时间及价格为演示内容，实际信息请以园区公告为准。',
                )
              }}
            </p>
          </div>
        </div>
        <div class="detail-actions">
          <button
            class="save-button"
            :class="{ saved: isFavorite(selection) }"
            :aria-pressed="isFavorite(selection)"
            @click="toggleFavorite(selection)"
          >
            <AppIcon name="heart" :size="20" />{{
              t(isFavorite(selection) ? '已收藏' : '收藏')
            }}</button
          ><button class="primary-button" @click="viewOnMap(detail.place.id)">
            <AppIcon name="map" :size="18" />{{ t('在地图中查看')
            }}<AppIcon name="arrow" :size="18" />
          </button>
        </div> </template
    ></AppDialog>
  </Transition>

  <Transition name="sheet">
    <AppDialog v-if="overlay === 'favorites'" label="我的收藏" @close="closeModal"
      ><div class="simple-dialog">
        <span class="dialog-emblem"><AppIcon name="heart" :size="28" /></span>
        <p class="eyebrow">{{ t('SAVE A LITTLE WONDER') }}</p>
        <h2>{{ t('把美好，留在行程里') }}</h2>
        <p class="dialog-intro">
          {{ t('已收藏 {count} 份心动 · 保存在这台设备', { count: favoriteItems.length }) }}
        </p>
        <div v-if="!favoriteItems.length" class="favorites-empty">
          <AppIcon name="leaf" :size="42" />
          <p>{{ t('还没有收藏。') }}<br />{{ t('遇见喜欢的地点、活动与餐厅，点亮那颗心。') }}</p>
          <button class="primary-button" @click="closeModal">{{ t('去发现美好') }}</button>
        </div>
        <div v-else class="favorite-list">
          <div v-for="item in favoriteItems" :key="selectionKey(item.selection)">
            <button @click="openSelection(item.selection)">
              <span class="favorite-type">{{ t(item.label) }}</span><span
                ><strong>{{ t(item.name) }}</strong
                ><small>{{ t(item.subtitle) }}</small></span
              ><AppIcon name="chevron" :size="18" /></button
            ><button
              class="remove-favorite"
              :aria-label="t('取消收藏{name}', { name: item.name })"
              @click="toggleFavorite(item.selection)"
            >
              <AppIcon name="heart" :size="18" />
            </button>
          </div>
        </div></div
    ></AppDialog>
  </Transition>
  <Transition name="toast"
    ><div v-if="toast" class="toast-message" role="status">
      <AppIcon name="check" :size="17" />{{ t(toast) }}
    </div></Transition
  >
</template>
