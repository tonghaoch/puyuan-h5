import { shanghaiDate, shiftDay } from '../lib/time'
import referenceMap from './reference-map.json'

export type Category = 'performance' | 'craft' | 'food' | 'scenic' | 'service'
export type Tab = 'map' | 'food' | 'activities'
export type Selection = { kind: 'place' | 'activity' | 'restaurant'; id: string }
export interface ScenePoint {
  x: number
  y: number
}
export interface Place {
  id: string
  name: string
  subtitle: string
  category: Category
  point: ScenePoint
  description: string
  art: string
  reference: [number, number]
  secondary: boolean
}
export interface Activity {
  id: string
  placeId: string
  name: string
  subtitle: string
  category: 'performance' | 'craft' | 'scenic'
  description: string
  duration: string
  time: string
  price: string
  sessions: { start: string; end: string }[]
  tags: string[]
}
export interface Restaurant {
  id: string
  placeId: string
  name: string
  subtitle: string
  description: string
  cuisine: string
  price: number
  hours: string
  tags: string[]
  art: string
}

export const categoryLabels: Record<Category, string> = {
  performance: '水乡演艺',
  craft: '风物雅集',
  food: '寻味濮院',
  scenic: '古镇漫游',
  service: '游园服务',
}
export const mapFilters: { id: Category | 'all'; name: string; icon: string }[] = [
  { id: 'all', name: '全部', icon: 'sparkles' },
  { id: 'performance', name: '演艺', icon: 'fan' },
  { id: 'craft', name: '雅集', icon: 'flower' },
  { id: 'food', name: '美食', icon: 'tea' },
  { id: 'service', name: '服务', icon: 'bell' },
  { id: 'scenic', name: '探景', icon: 'lantern' },
]
export const places: Place[] = referenceMap.landmarks.map((landmark, index) => ({
  id: landmark.id,
  name: landmark.name,
  subtitle: landmark.subtitle,
  category: landmark.category as Category,
  point: {
    x: landmark.anchor[0]! + referenceMap.sourceOffset.x,
    y: landmark.anchor[1]! + referenceMap.sourceOffset.y,
  },
  reference: landmark.anchor as [number, number],
  secondary: index >= 9,
  description:
    landmark.id === 'temple'
      ? '按参考图保留“福善寺”的标注，寺院位于古塔南侧。公开地图写作“福山寺”，名称及现场状态还需核实。这里可查看古建漫游的演示内容。'
      : landmark.id === 'visitor'
        ? '对应参考图西北侧的游客中心建筑组团。现场服务内容、入口和开放时间请以景区公告为准。'
        : '按参考图保留' +
          landmark.name +
          '的建筑位置与周边水巷关系。停下来看看屋檐、桥梁与院落；下列活动和餐饮信息用于体验演示，实际开放情况以景区公告为准。',
  art: landmark.art,
}))

const today = shanghaiDate(new Date())
function sessions(hour: string, end: string) {
  return [0, 1, 2].map((offset) => ({
    start: `${shiftDay(today, offset)}T${hour}:00+08:00`,
    end: `${shiftDay(today, offset)}T${end}:00+08:00`,
  }))
}
export const activities: Activity[] = [
  {
    id: 'waterside-opera',
    placeId: 'water-stage',
    name: '水岸听曲',
    subtitle: '一曲婉转，听见江南',
    category: 'performance',
    description:
      '以水为幕，以戏为引。跟随清婉曲声，走进一段水乡故事。可以提前到河岸边，找一个适合听戏的位置。',
    duration: '约 30 分钟',
    time: '19:00 — 19:30',
    price: '演示场次',
    sessions: sessions('19:00', '19:30'),
    tags: ['水乡戏曲', '夜游好时光'],
  },
  {
    id: 'silk-workshop',
    placeId: 'guildhall',
    name: '一缕丝·织江南',
    subtitle: '让指尖，记住一座城',
    category: 'craft',
    description:
      '从一根丝线开始，认识传统织造的细密与耐心。体验简单织作，感受濮院与丝绸之间的故事。',
    duration: '约 60 分钟',
    time: '14:00 — 15:00',
    price: '体验信息待确认',
    sessions: sessions('14:00', '15:00'),
    tags: ['非遗手作', '慢享时光'],
  },
  {
    id: 'theater-show',
    placeId: 'theater',
    name: '梅泾戏梦',
    subtitle: '一方舞台，一段旧梦',
    category: 'performance',
    description:
      '在剧场中听一段江南小调，跟随曲词和身段走入故事。节目为交互演示内容，真实演出以园区公告为准。',
    duration: '约 40 分钟',
    time: '15:30 — 16:10',
    price: '演示场次',
    sessions: sessions('15:30', '16:10'),
    tags: ['室内演出', '江南曲韵'],
  },
  {
    id: 'artisan-market',
    placeId: 'market',
    name: '巷陌风物集',
    subtitle: '好物有来处，生活有诗意',
    category: 'craft',
    description:
      '逛一逛古镇的风物小集，看看器物、织品和手作。用一段没有目的的散步，发现旅途的小惊喜。',
    duration: '自由体验',
    time: '10:00 — 18:00',
    price: '演示活动',
    sessions: sessions('10:00', '18:00'),
    tags: ['风物市集', '随心慢逛'],
  },
  {
    id: 'temple-walk',
    placeId: 'temple',
    name: '寻檐·古建漫游',
    subtitle: '在一砖一瓦之间，读懂时光',
    category: 'scenic',
    description:
      '从飞檐到院落，从石桥到水巷，用散步的速度观察古镇。这里提供一个古建主题漫游内容示例，不代表已安排导览。',
    duration: '约 45 分钟',
    time: '09:30 — 10:15',
    price: '演示活动',
    sessions: sessions('09:30', '10:15'),
    tags: ['古建寻访', '人文漫步'],
  },
]
export const restaurants: Restaurant[] = [
  {
    id: 'r-tea',
    placeId: 'teahouse',
    name: '水巷茶事',
    subtitle: '一盏清茶，半日江南',
    description: '倚窗临水，慢饮一盏。茶点与热茶相伴，给游园留一段松弛的时光。',
    cuisine: '茶馆',
    price: 58,
    hours: '10:00 — 20:00',
    tags: ['临河茶席', '中式茶点'],
    art: 'tea',
  },
  {
    id: 'r-river',
    placeId: 'dining',
    name: '龙湾食坊',
    subtitle: '寻常烟火，也有江南滋味',
    description: '以家常水乡风味为灵感的餐厅示例。小炒、汤羹和时令菜，适合走累后慢慢吃一餐。',
    cuisine: '江南菜',
    price: 88,
    hours: '11:00 — 21:00',
    tags: ['水乡小菜', '好友聚餐'],
    art: 'food',
  },
  {
    id: 'r-noodle',
    placeId: 'dining',
    name: '巷里一碗面',
    subtitle: '热气升起来，旅途慢下来',
    description: '清汤一碗，浇头几味。在古镇街巷中，用一碗热面补充散步的能量。',
    cuisine: '小吃',
    price: 32,
    hours: '08:00 — 19:00',
    tags: ['现做面食', '一人食'],
    art: 'noodles',
  },
  {
    id: 'r-dessert',
    placeId: 'market',
    name: '桂花小院',
    subtitle: '把一点甜，留在旅途中',
    description: '糯香糕点与清甜茶饮组成的一间点心铺示例。小小一份，适合边逛边品尝。',
    cuisine: '小吃',
    price: 28,
    hours: '10:00 — 18:00',
    tags: ['时令点心', '桂花香'],
    art: 'dessert',
  },
]

export function placeById(id: string) {
  return places.find((p) => p.id === id)
}
export function matchesSearch(query: string, ...values: string[]) {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean)
  const haystack = values.join(' ').toLocaleLowerCase()
  return terms.every((term) => haystack.includes(term))
}
export function selectionKey(selection: Selection) {
  return `${selection.kind}:${selection.id}`
}
