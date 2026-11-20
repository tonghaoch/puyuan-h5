<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import ParkMap from './components/ParkMap.vue'
import AppDialog from './components/AppDialog.vue'
import GeoLocationMap from './components/GeoLocationMap.vue'
import { isGeographicView, geoName, type MapView } from './lib/park-geography'
import type { GeoCollection, GeoFeature } from './lib/geography'
import geographicPois from './data/geographic-pois.json'
import landmarkModels from './data/landmark-models.json'
import {
  activities,
  restaurants,
  places,
  categoryLabels,
  mapFilters,
  matchesSearch,
  placeById,
  selectionKey,
  type Tab,
  type Category,
  type Selection,
} from './data/catalog'
import { useLocation } from './lib/location'
import { dayLabel, shanghaiDate, shiftDay, sessionStatus } from './lib/time'

type Overlay = 'guide' | 'favorites' | 'location' | 'geopoint' | null
const tab = ref<Tab>('map')
const mapView = ref<MapView>('reference')
const geographicView = computed(() => isGeographicView(mapView.value))
const focusLocation = ref(0)
const geoSelection = ref<GeoFeature | null>(null)
const mapViews: { id: MapView; name: string }[] = [
  { id: 'reference', name: '导览' },
  { id: 'geographic', name: '路网' },
]
const selection = ref<Selection | null>(null)
const detailModelId = ref<string>()
const overlay = ref<Overlay>(null)
const query = ref('')
const mapFilter = ref<Category | 'all'>('all')
const foodFilter = ref('全部')
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
const motion = ref(stored('puyuan.motion') !== 'off' && !media.matches)
const validKeys = new Set([
  ...places.map((p) => `place:${p.id}`),
  ...activities.map((a) => `activity:${a.id}`),
  ...restaurants.map((r) => `restaurant:${r.id}`),
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
const location = useLocation()
const hasModal = computed(() => !!selection.value || !!overlay.value)
const motionActive = computed(
  () => motion.value && pageVisible.value && tab.value === 'map' && !hasModal.value,
)
const today = computed(() => shanghaiDate(new Date(now.value)))
const tabs: { id: Tab; label: string; icon: string; english: string }[] = [
  { id: 'map', label: '游园地图', icon: 'map', english: 'EXPLORE' },
  { id: 'food', label: '寻味濮院', icon: 'tea', english: 'TASTE' },
  { id: 'activities', label: '风雅之约', icon: 'fan', english: 'DISCOVER' },
]
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
  tab.value = nextTab === 'food' || nextTab === 'activities' ? nextTab : 'map'
  selection.value = kind && id ? validSelection(kind, id) : null
  detailModelId.value = kind === 'place' ? modelId : undefined
  geoSelection.value =
    kind === 'geopoint'
      ? ((geographicPois as unknown as GeoCollection).features.find(
          (f) => f.id?.replace('/', '-') === id,
        ) ?? null)
      : null
  if (geoSelection.value && !isGeographicView(mapView.value)) mapView.value = 'geographic'
  overlay.value = geoSelection.value
    ? 'geopoint'
    : kind === 'guide' || kind === 'favorites' || kind === 'location'
      ? kind
      : null
}
function route(path: string, modal = false, replace = false) {
  const method = replace ? 'replaceState' : 'pushState'
  window.history[method]({ puyuanModal: modal }, '', `#${path}`)
  readRoute()
}
function changeTab(next: Tab) {
  if (next !== tab.value || hasModal.value) {
    query.value = ''
    route(next)
  }
}
function openSelection(next: Selection, modelId?: string) {
  route(`${tab.value}/${next.kind}/${next.id}${modelId ? `/${modelId}` : ''}`, true, hasModal.value)
}
function openOverlay(next: Exclude<Overlay, null>) {
  route(`${tab.value}/${next}`, true, hasModal.value)
}
function openGeoPoint(feature: GeoFeature) {
  route(`${tab.value}/geopoint/${feature.id!.replace('/', '-')}`, true, hasModal.value)
}
function changeMapView(next: MapView) {
  mapView.value = next
  query.value = ''
}
function viewLocationOnMap() {
  mapView.value = 'geographic'
  query.value = ''
  route('map', false, true)
  focusLocation.value = Date.now()
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
function toggleMotion() {
  motion.value = !motion.value
  save('puyuan.motion', motion.value ? 'on' : 'off')
  notify(motion.value ? '已开启地图动态效果' : '已减少地图动态效果')
}
function resetFilters(target: Tab) {
  query.value = ''
  if (target === 'map') mapFilter.value = 'all'
  if (target === 'food') foodFilter.value = '全部'
  if (target === 'activities') activityFilter.value = 'all'
}
function viewOnMap(placeId: string) {
  mapView.value = 'reference'
  query.value = ''
  mapFilter.value = 'all'
  route('map', false, true)
  focusRequest.value = { id: placeId, nonce: Date.now() }
  notify('已为你找到地图中的位置')
}
const visiblePlaces = computed(() =>
  places.filter((place) => mapFilter.value === 'all' || place.category === mapFilter.value),
)
const visibleRestaurants = computed(() =>
  restaurants.filter(
    (r) =>
      (foodFilter.value === '全部' || r.cuisine === foodFilter.value) &&
      matchesSearch(query.value, r.name, r.cuisine, r.subtitle, ...r.tags),
  ),
)
const selectedDay = computed(() => shiftDay(today.value, dayFilter.value))
const visibleActivities = computed(() =>
  activities.filter(
    (a) =>
      (activityFilter.value === 'all' || a.category === activityFilter.value) &&
      a.sessions.some((s) => shanghaiDate(new Date(s.start)) === selectedDay.value) &&
      matchesSearch(query.value, a.name, a.subtitle, placeById(a.placeId)!.name, ...a.tags),
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
  restaurants.filter((r) => r.placeId === currentPlace.value?.id),
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
          : restaurants.find((r) => r.id === sel.id)
    if (!item) return []
    return [
      {
        selection: sel,
        name: item.name,
        subtitle: item.subtitle,
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
      available: '已获取设备位置',
      denied: '定位权限未开启。你仍然可以自由浏览地图和全部内容。',
      unavailable: '当前环境暂不支持定位。请通过 HTTPS 地址在手机浏览器中打开。',
      timeout: '定位暂时超时，可以到开阔处后重试。',
      error: '暂时无法获取位置，请检查系统定位设置后重试。',
    })[location.state.value],
)
function visibility() {
  pageVisible.value = !document.hidden
  if (pageVisible.value) now.value = Date.now()
}
function motionPreference() {
  if (media.matches) motion.value = false
}
onMounted(() => {
  window.addEventListener('popstate', readRoute)
  window.addEventListener('hashchange', readRoute)
  document.addEventListener('visibilitychange', visibility)
  media.addEventListener('change', motionPreference)
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 30000)
})
onBeforeUnmount(() => {
  window.removeEventListener('popstate', readRoute)
  window.removeEventListener('hashchange', readRoute)
  document.removeEventListener('visibilitychange', visibility)
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
      <button class="brand" aria-label="濮院漫游，返回地图" @click="changeTab('map')">
        <span class="brand-mark"
          ><svg width="37" height="42" viewBox="0 0 42 46" fill="none">
            <path
              d="M4 13q6 1 17-8 9 8 17 8M9 15h24M12 17v18m18-18v18M6 38h30M17 35V22h8v13M3 43h36"
              stroke="currentColor"
              stroke-width="1.7"
            />
            <path d="M10 8q5 1 11-5 5 5 11 5" stroke="currentColor" stroke-width="1.5" /></svg
        ></span>
        <span class="brand-type">濮院漫游<small>PUYUAN · WANDER SLOWLY</small></span>
      </button>

      <div class="header-actions">
        <button class="guide-button" @click="openOverlay('guide')">
          <AppIcon name="book" :size="18" /><span>游园手帖</span>
        </button>
      </div>
    </header>

    <main class="main-content">
      <section
        v-show="tab === 'map'"
        class="map-page"
        :class="{ 'reference-view': mapView === 'reference', 'geographic-view': geographicView }"
        aria-label="游园地图"
      >
        <ParkMap
          :places="visiblePlaces"
          :all-places="places"
          :focus-request="focusRequest"
          :motion="motionActive"
          :view="mapView"
          :fix="location.fix.value"
          :now="now"
          :focus-location="focusLocation"
          @geoselect="openGeoPoint"
          @outside="notify('当前位置在园区视野之外，未将定位点移入园区')"
          @select="(place) => openSelection({ kind: 'place', id: place.id })"
          @locate="openOverlay('location')"
        />
        <div class="map-topbar">
          <div v-if="!geographicView" class="filter-pills" aria-label="地图地点分类">
            <button
              v-for="filter in mapFilters"
              :key="filter.id"
              :class="{ active: mapFilter === filter.id }"
              :aria-pressed="mapFilter === filter.id"
              @click="mapFilter = filter.id"
            >
              <AppIcon :name="filter.icon" :size="17" />{{ filter.name }}
            </button>
          </div>
          <div v-else class="geo-layer-legend">
            <span><i class="water-line"></i>真实水道</span
            ><span><i class="road-line"></i>道路与桥梁</span
            ><span><i class="boundary-line"></i>园区边界</span>
          </div>
        </div>
        <div class="map-view-switch" aria-label="地图视图">
          <button
            v-for="view in mapViews"
            :key="view.id"
            :class="{ active: mapView === view.id }"
            :aria-pressed="mapView === view.id"
            @click="changeMapView(view.id)"
          >
            {{ view.name }}
          </button>
        </div>
        <div class="map-introduction">
          <p class="eyebrow"><span></span> 江 南 好 时 节</p>
          <h1>
            一入濮院<br />便是<span>江南</span><i class="title-seal">慢<br />游</i>
          </h1>
          <div class="intro-rule"><span></span><i>◇</i></div>
          <p class="intro-copy">循水巷，过石桥，听一曲婉转。<br />把脚步放慢，让风景发生。</p>
          <span class="intro-caption">A LITTLE WANDER, A LOT TO DISCOVER.</span>
        </div>
        <div v-if="!geographicView && !visiblePlaces.length" class="map-empty">
          <AppIcon name="search" :size="24" />
          <p>还没有找到这处风景</p>
          <button @click="resetFilters('map')">查看全部地点</button>
        </div>
        <div class="map-bottom-note">
          <span class="demo-dot"></span
          ><span v-if="!geographicView">水乡漫游 · {{ places.length }} 处地点</span
          ><span v-else
            ><a
              href="https://www.openstreetmap.org/copyright"
              target="_blank"
              rel="noopener noreferrer"
              >© OpenStreetMap</a
            ></span
          ><span class="note-separator">/</span><span class="map-hint">拖动探索 · 双指缩放</span>
        </div>
        <button
          class="motion-control"
          v-if="!geographicView"
          :aria-pressed="motion"
          :aria-label="motion ? '减少动态效果' : '开启动效'"
          @click="toggleMotion"
        >
          <AppIcon name="leaf" :size="16" /><span>{{
            motion ? '风物有声，草木有灵' : '静赏江南'
          }}</span
          ><i :class="{ on: motion }"></i>
        </button>
        <div class="map-vignette" aria-hidden="true"></div>
      </section>

      <section v-if="tab === 'food'" class="catalog-page food-page" aria-label="餐厅列表">
        <div class="catalog-heading">
          <div>
            <p class="eyebrow">A TASTE OF JIANGNAN</p>
            <h1>人间烟火，<span>最是江南。</span></h1>
            <p>一盏茶，一碗面。把水乡的好滋味，慢慢尝遍。</p>
          </div>
          <div class="heading-stamp">食<br />味</div>
        </div>
        <div class="catalog-toolbar">
          <div class="text-filters" aria-label="餐厅分类">
            <button
              v-for="filter in ['全部', '茶馆', '江南菜', '小吃']"
              :key="filter"
              :class="{ active: foodFilter === filter }"
              :aria-pressed="foodFilter === filter"
              @click="foodFilter = filter"
            >
              {{ filter }}
            </button>
          </div>
          <label class="search-field"
            ><AppIcon name="search" :size="18" /><input
              v-model="query"
              aria-label="搜索餐厅"
              placeholder="寻找你喜欢的滋味" /><button
              v-if="query"
              class="clear-search"
              aria-label="清空搜索"
              @click.prevent="query = ''"
            >
              <AppIcon name="close" :size="15" /></button
          ></label>
        </div>
        <div class="results-line">
          <span>共 {{ visibleRestaurants.length }} 处好滋味</span
          ><span>演示商户 · 价格与营业时间仅供体验</span>
        </div>
        <div class="food-grid">
          <article v-for="restaurant in visibleRestaurants" :key="restaurant.id" class="food-card">
            <button
              class="card-cover"
              :aria-label="`查看${restaurant.name}详情`"
              @click="openSelection({ kind: 'restaurant', id: restaurant.id })"
            >
              <img
                :src="`/art/${restaurant.art}.svg`"
                :alt="`${restaurant.name}意境插画`"
                loading="lazy"
              /><span class="cover-category">{{ restaurant.cuisine }}</span>
            </button>
            <button
              class="card-favorite"
              :class="{ saved: isFavorite({ kind: 'restaurant', id: restaurant.id }) }"
              :aria-label="`${isFavorite({ kind: 'restaurant', id: restaurant.id }) ? '取消收藏' : '收藏'}${restaurant.name}`"
              :aria-pressed="isFavorite({ kind: 'restaurant', id: restaurant.id })"
              @click="toggleFavorite({ kind: 'restaurant', id: restaurant.id })"
            >
              <AppIcon name="heart" :size="18" />
            </button>
            <div class="food-card-body">
              <div class="card-title-line">
                <button @click="openSelection({ kind: 'restaurant', id: restaurant.id })">
                  <h2>{{ restaurant.name }}</h2></button
                ><span class="price"
                  >¥<strong>{{ restaurant.price }}</strong
                  ><small> / 人</small></span
                >
              </div>
              <p class="card-subtitle">{{ restaurant.subtitle }}</p>
              <div class="tag-row">
                <span v-for="tag in restaurant.tags" :key="tag">{{ tag }}</span>
              </div>
              <div class="card-footer">
                <span
                  ><AppIcon name="pin" :size="14" />{{ placeById(restaurant.placeId)?.name }}</span
                ><button aria-label="在地图中查看餐厅" @click="viewOnMap(restaurant.placeId)">
                  地图中查看<AppIcon name="arrow" :size="15" />
                </button>
              </div>
            </div>
          </article>
        </div>
        <div v-if="!visibleRestaurants.length" class="catalog-empty">
          <AppIcon name="tea" :size="38" />
          <h2>这一味，还在寻找中</h2>
          <p>换个关键词，或看看全部餐厅。</p>
          <button class="primary-button" @click="resetFilters('food')">查看全部餐厅</button>
        </div>
        <p class="catalog-footnote">— 让一餐一饭，成为旅途的一部分 —</p>
      </section>

      <section
        v-if="tab === 'activities'"
        class="catalog-page activities-page"
        aria-label="活动列表"
      >
        <div class="catalog-heading">
          <div>
            <p class="eyebrow">MOMENTS WORTH WANDERING FOR</p>
            <h1>好时光，<span>当有好相逢。</span></h1>
            <p>听戏、寻艺、逛风物。在濮院，赴一场风雅之约。</p>
          </div>
          <div class="heading-stamp">雅<br />集</div>
        </div>
        <div class="catalog-toolbar">
          <div class="text-filters" aria-label="活动分类">
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
              {{ filter.label }}
            </button>
          </div>
          <label class="search-field"
            ><AppIcon name="search" :size="18" /><input
              v-model="query"
              aria-label="搜索活动"
              placeholder="寻找一场心动的相遇" /><button
              v-if="query"
              class="clear-search"
              aria-label="清空搜索"
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
              {{ label }}<small>{{ shiftDay(today, index).slice(5).replace('-', '.') }}</small>
            </button>
          </div>
          <span class="demo-label">演示日程 · 非实际演出安排</span>
        </div>
        <div class="activity-grid">
          <article v-for="activity in visibleActivities" :key="activity.id" class="activity-card">
            <button
              class="activity-art"
              :aria-label="`查看${activity.name}详情`"
              @click="openSelection({ kind: 'activity', id: activity.id })"
            >
              <img
                :src="`/art/${placeById(activity.placeId)?.art}.svg`"
                :alt="`${activity.name}意境插画`"
                loading="lazy"
              /><span class="cover-category">{{ categoryLabels[activity.category] }}</span>
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
                  >进行中</span
                >
              </div>
              <button
                class="activity-title"
                @click="openSelection({ kind: 'activity', id: activity.id })"
              >
                <h2>{{ activity.name }}</h2>
              </button>
              <p class="card-subtitle">{{ activity.subtitle }}</p>
              <div class="tag-row">
                <span v-for="tag in activity.tags" :key="tag">{{ tag }}</span>
              </div>
              <div class="activity-card-footer">
                <span><AppIcon name="pin" :size="14" />{{ placeById(activity.placeId)?.name }}</span
                ><button @click="openSelection({ kind: 'activity', id: activity.id })">
                  赴约详情<AppIcon name="arrow" :size="17" />
                </button>
              </div>
            </div>
            <button
              class="activity-favorite"
              :class="{ saved: isFavorite({ kind: 'activity', id: activity.id }) }"
              :aria-label="`${isFavorite({ kind: 'activity', id: activity.id }) ? '取消收藏' : '收藏'}${activity.name}`"
              :aria-pressed="isFavorite({ kind: 'activity', id: activity.id })"
              @click="toggleFavorite({ kind: 'activity', id: activity.id })"
            >
              <AppIcon name="heart" :size="18" />
            </button>
          </article>
        </div>
        <div v-if="!visibleActivities.length" class="catalog-empty">
          <AppIcon name="fan" :size="38" />
          <h2>暂时没有这类活动</h2>
          <p>试着换个关键词或分类，发现另一种相遇。</p>
          <button class="primary-button" @click="resetFilters('activities')">查看全部活动</button>
        </div>
        <p class="catalog-footnote">— 不赶时间，只赴好时光 —</p>
      </section>
    </main>
    <nav class="main-nav" aria-label="主要导航">
      <button
        v-for="item in tabs"
        :key="item.id"
        :class="{ active: tab === item.id }"
        :aria-current="tab === item.id ? 'page' : undefined"
        @click="changeTab(item.id)"
      >
        <AppIcon :name="item.icon" :size="21" /><span>{{ item.label }}</span
        ><small>{{ item.english }}</small>
      </button>
    </nav>
  </div>

  <Transition name="sheet">
    <AppDialog v-if="selection && detail" :label="detail.name" @close="closeModal">
      <div class="detail-hero" :class="{ 'model-hero': detail.model }">
        <img
          :src="detail.model?.heroAsset || detail.model?.asset || `/art/${detail.art}.svg`"
          :alt="`${detail.name}意境插画`"
        /><span class="detail-category">{{ detail.category }}</span>
      </div>
      <div class="detail-body">
        <p class="eyebrow">A MOMENT IN PUYUAN</p>
        <h2>{{ detail.name }}</h2>
        <p class="detail-subtitle">{{ detail.subtitle }}</p>
        <p class="detail-description">{{ detail.description }}</p>
        <div class="detail-facts">
          <div>
            <AppIcon name="pin" :size="18" /><span
              ><small>所在地点</small>{{ detail.place.name }}</span
            >
          </div>
          <div v-if="currentActivity">
            <AppIcon name="clock" :size="18" /><span
              ><small>{{ currentActivity.duration }}</small
              >{{ currentActivity.time }}</span
            >
          </div>
          <div v-if="currentRestaurant">
            <AppIcon name="clock" :size="18" /><span
              ><small>示例营业时间</small>{{ currentRestaurant.hours }}</span
            >
          </div>
          <div v-if="currentRestaurant">
            <AppIcon name="tea" :size="18" /><span
              ><small>示例人均</small>¥{{ currentRestaurant.price }} / 人</span
            >
          </div>
        </div>
        <div v-if="currentActivity" class="session-list">
          <h3>场次一览 <span>演示日程</span></h3>
          <div v-for="session in currentActivity.sessions" :key="session.start">
            <span
              >{{ dayLabel(session.start, new Date(now)) }}
              <small>{{
                shanghaiDate(new Date(session.start)).slice(5).replace('-', '.')
              }}</small></span
            ><strong>{{ currentActivity.time }}</strong
            ><span class="session-state" :class="sessionStatus([session], now)">{{
              { ongoing: '进行中', upcoming: '待开始', ended: '已结束' }[
                sessionStatus([session], now)
              ]
            }}</span>
          </div>
        </div>
        <div
          v-if="selection.kind === 'place' && (placeActivities.length || placeRestaurants.length)"
          class="place-content"
        >
          <h3>在这里，可以遇见</h3>
          <button
            v-for="activity in placeActivities"
            :key="activity.id"
            @click="openSelection({ kind: 'activity', id: activity.id })"
          >
            <AppIcon name="fan" :size="20" /><span
              ><strong>{{ activity.name }}</strong
              ><small>{{ activity.time }}</small></span
            ><AppIcon name="chevron" :size="17" /></button
          ><button
            v-for="restaurant in placeRestaurants"
            :key="restaurant.id"
            @click="openSelection({ kind: 'restaurant', id: restaurant.id })"
          >
            <AppIcon name="tea" :size="20" /><span
              ><strong>{{ restaurant.name }}</strong
              ><small>{{ restaurant.cuisine }} · 示例人均 ¥{{ restaurant.price }}</small></span
            ><AppIcon name="chevron" :size="17" />
          </button>
        </div>
        <div class="demo-notice">
          <AppIcon name="info" :size="15" />
          <p>
            当前为游园体验版。地点布局、活动、营业时间及价格为演示内容，实际信息请以园区公告为准。
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
          <AppIcon name="heart" :size="20" />{{ isFavorite(selection) ? '已收藏' : '收藏' }}</button
        ><button class="primary-button" @click="viewOnMap(detail.place.id)">
          <AppIcon name="map" :size="18" />在地图中查看<AppIcon name="arrow" :size="18" />
        </button>
      </div>
    </AppDialog>
  </Transition>

  <Transition name="sheet">
    <AppDialog v-if="overlay === 'guide'" label="游园手帖" @close="closeModal"
      ><div class="simple-dialog guide-dialog">
        <span class="dialog-emblem"><AppIcon name="book" :size="28" /></span>
        <p class="eyebrow">YOUR LITTLE GUIDE</p>
        <h2>游园手帖</h2>
        <p class="dialog-intro">不必赶路，把时光交给水乡。</p>
        <div class="guide-step">
          <span>壹</span>
          <div>
            <h3>循着地图，随心慢游</h3>
            <p>拖动地图、双指缩放，按分类浏览地点，点击标记查看详情。</p>
          </div>
        </div>
        <div class="guide-step">
          <span>贰</span>
          <div>
            <h3>寻味赴约，各有欢喜</h3>
            <p>在「寻味濮院」寻找餐厅，在「风雅之约」查看活动。收藏喜欢的内容，随时回来查看。</p>
          </div>
        </div>
        <div class="guide-step">
          <span>叁</span>
          <div>
            <h3>留一点时间，静赏风物</h3>
            <p>地图支持减少动态效果。收藏保存在当前设备，关闭页面后仍然保留。</p>
          </div>
        </div>
        <div class="demo-notice">
          <AppIcon name="info" :size="17" />
          <p>
            导览是古镇示意图；路网按地理坐标展示，可以查看设备位置。暂不提供步行导航。
          </p>
        </div>
        <button class="primary-button full-width" @click="closeModal">
          开始慢游<AppIcon name="arrow" :size="18" />
        </button></div
    ></AppDialog>
  </Transition>
  <Transition name="sheet">
    <AppDialog v-if="overlay === 'favorites'" label="我的收藏" @close="closeModal"
      ><div class="simple-dialog">
        <span class="dialog-emblem"><AppIcon name="heart" :size="28" /></span>
        <p class="eyebrow">SAVE A LITTLE WONDER</p>
        <h2>把美好，留在行程里</h2>
        <p class="dialog-intro">已收藏 {{ favoriteItems.length }} 份心动 · 保存在这台设备</p>
        <div v-if="!favoriteItems.length" class="favorites-empty">
          <AppIcon name="leaf" :size="42" />
          <p>还没有收藏。<br />遇见喜欢的地点、活动与餐厅，点亮那颗心。</p>
          <button class="primary-button" @click="closeModal">去发现美好</button>
        </div>
        <div v-else class="favorite-list">
          <div v-for="item in favoriteItems" :key="selectionKey(item.selection)">
            <button @click="openSelection(item.selection)">
              <span class="favorite-type">{{ item.label }}</span><span
                ><strong>{{ item.name }}</strong
                ><small>{{ item.subtitle }}</small></span
              ><AppIcon name="chevron" :size="18" /></button
            ><button
              class="remove-favorite"
              :aria-label="`取消收藏${item.name}`"
              @click="toggleFavorite(item.selection)"
            >
              <AppIcon name="heart" :size="18" />
            </button>
          </div>
        </div></div
    ></AppDialog>
  </Transition>
  <Transition name="sheet">
    <AppDialog v-if="overlay === 'location'" label="我的位置" @close="closeModal"
      ><div class="simple-dialog location-dialog">
        <span class="dialog-emblem"><AppIcon name="locate" :size="30" /></span>
        <p class="eyebrow">FIND YOUR PLACE</p>
        <h2>此刻，你在何处</h2>
        <p class="dialog-intro">位置仅用于当前设备，不会上传或保存轨迹。</p>
        <div class="location-state" :class="location.state.value" role="status">
          <span v-if="location.state.value === 'loading'" class="spinner"></span
          ><AppIcon
            v-else
            :name="location.state.value === 'available' ? 'check' : 'pin'"
            :size="28"
          />
          <p>{{ locationMessage }}</p>
          <small v-if="location.fix.value"
            >设备报告精度约 {{ Math.round(location.fix.value.accuracy) }} 米 ·
            {{
              new Date(location.fix.value.timestamp).toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
              })
            }}
            获取</small
          >
        </div>
        <div class="demo-notice">
          <AppIcon name="info" :size="17" />
          <p>
            当前古风地图尚未进行地理校准，暂不在示意图上显示定位点。路网使用真实地理坐标；公开边界不代表实际开放范围。
          </p>
        </div>
        <GeoLocationMap :fix="location.fix.value" :now="now" />
        <button
          v-if="location.fix.value"
          class="secondary-button full-width"
          @click="viewLocationOnMap"
        >
          <AppIcon name="map" :size="17" />在路网中查看位置
        </button>
        <button
          v-if="location.state.value !== 'denied'"
          class="primary-button full-width"
          :disabled="location.state.value === 'loading'"
          @click="location.locate()"
        >
          <AppIcon name="locate" :size="18" />{{
            location.state.value === 'loading'
              ? '正在定位…'
              : location.state.value === 'idle'
                ? '获取设备位置'
                : '重新获取位置'
          }}</button
        ><button v-else class="primary-button full-width" @click="closeModal">继续浏览地图</button>
      </div></AppDialog
    >
  </Transition>
  <Transition name="sheet">
    <AppDialog
      v-if="overlay === 'geopoint' && geoSelection"
      :label="geoName(geoSelection)"
      @close="closeModal"
    >
      <div class="simple-dialog geo-place-dialog">
        <span class="dialog-emblem"><AppIcon name="pin" :size="28" /></span>
        <p class="eyebrow">A PLACE ON THE MAP</p>
        <h2>{{ geoName(geoSelection) }}</h2>
        <p class="dialog-intro">公开地图地标 · 地理坐标视图</p>
        <p class="geo-place-description">
          此处位置来自 OpenStreetMap
          的原始地标记录，未使用手绘图像推算。地标名称、开放状态与现场情况可能存在差异。
        </p>
        <div v-if="geoSelection.geometry.type === 'Point'" class="geo-coordinates">
          <span>经度 {{ geoSelection.geometry.coordinates[0].toFixed(7) }}</span
          ><span>纬度 {{ geoSelection.geometry.coordinates[1].toFixed(7) }}</span>
        </div>
        <a
          class="secondary-button full-width"
          :href="String(geoSelection.properties.source_url)"
          target="_blank"
          rel="noopener noreferrer"
          >查看地图来源<AppIcon name="arrow" :size="17" /></a
        ><button class="primary-button full-width" @click="closeModal">继续看地图</button>
      </div>
    </AppDialog>
  </Transition>
  <Transition name="toast"
    ><div v-if="toast" class="toast-message" role="status">
      <AppIcon name="check" :size="17" />{{ toast }}
    </div></Transition
  >
</template>
