// Illustration-plane points registered from the pin tips in references/offsite-registration.json.
type FieldPhoto = [label: string, caption: string, layout?: 'contain' | 'portrait']

export interface FieldEntry {
  id: string
  name: string
  description: string
  setup: string
  goal: string
  note?: string
  photos: [FieldPhoto, ...FieldPhoto[]]
}
export interface Quest extends FieldEntry {
  place: string
  point: [number, number]
}
export function encounterImage(id: string, plate: number | 'thumb') {
  return `/art/encounters/${id}-${plate}.webp`
}
export const quests: Quest[] = [
  {
    id: 'relay',
    place: '关帝庙',
    name: '袱传货物',
    point: [1049, 1008],
    description: '货物不能经手。三件货物要沿着队列传下去，每一棒都靠两个人撑起的一方袱布。',
    photos: [
      ['接力', '队员两两撑布，面对面接力传递。'],
      ['地点', '关帝庙前的石马与庙门。'],
    ],
    setup: '两人一组撑开袱布，在指定区域接力。传递时只能用布，不能用手拿货物。',
    goal: '把大蒜、土豆、玉米三件货物全部传完。',
  },
  {
    id: 'drum',
    place: '翠冷台',
    name: '同心击鼓',
    point: [1124, 510],
    description: '一面鼓，一圈绳。大家手里各有一根绳，球能颠多高、多稳，取决于全队的节奏。',
    photos: [
      ['鼓绳', '队员围住鼓面，各执一根长绳。'],
      ['地点', '从空中看翠冷台的场地。'],
    ],
    setup: '队员各拉一根鼓绳，把球放上鼓面。配合收放绳子颠球，手不碰鼓面。',
    goal: '球不落地，连续颠起 8 次。',
  },
  {
    id: 'cuju',
    place: '大草坪',
    name: '蹴鞠达人',
    point: [1085, 564],
    description: '草坪上立着一面计分靶。队员轮流起脚，每一球的得分都算进全队的成绩。',
    photos: [
      ['射门', '队员将足球踢向圆形计分靶。'],
      ['地点', '古镇建筑旁的大草坪。'],
    ],
    setup: '全队累计 15 人次，每人有两次射门机会，由守关人记录得分。',
    goal: '全队总分超过 250 分。',
    note: '个人两球合计超过 32 分，可随机抽取一张能免一次惩罚的道具卡。恰好 32 分是否计入，以现场裁判为准。',
  },
  {
    id: 'hammer',
    place: '大草坪',
    name: '一锤定音',
    point: [1084, 603],
    description: '气球区只留给每位队员十五秒。场内的人抓紧时间挥锤，场外的人排好下一棒。',
    photos: [
      ['道具', '「一锤定音」挑战的充气锤道具。'],
      ['地点', '俯瞰绿树围合的大草坪。'],
    ],
    setup: '15 位队员依次接力，每人有 15 秒进入指定区域敲气球。',
    goal: '全队合计敲破超过 12 个气球。',
  },
  {
    id: 'mime',
    place: '梅泾剧场',
    name: '哑戏猜古词',
    point: [734, 757],
    description: '在梅泾剧场演一出没有台词的戏：台上两人知道谜底，台下队友要把他们的动作猜成古词。',
    photos: [
      ['比划', '「你比划我猜」的动作游戏示意。', 'contain'],
      ['地点', '梅泾剧场的临街正面。'],
    ],
    setup: '选两位队员上台看词卡，只能用动作提示，不能说话。其余队员负责猜词。',
    goal: '在 120 秒内尽量猜对，交守关人计数。',
  },
  {
    id: 'treasure',
    place: '珍宝馆',
    name: '珍宝馆里的奥秘',
    point: [988, 1027],
    description: '奥秘卡就是这次看展的题单。与队友在展柜之间循题找物，把线索一条条填回卡上。',
    photos: [
      ['展厅', '珍宝馆内环形步道与展柜。'],
      ['展签', '馆内展陈文字示例。', 'contain'],
    ],
    setup: '全队到馆内领取奥秘卡，根据卡上的提示寻找对应藏品。',
    goal: '填齐卡上的奥秘信息，交给守关人核验。',
  },
  {
    id: 'mugwort',
    place: '福善寺',
    name: '福善艾草锤',
    point: [904, 671],
    description: '到福善寺暂歇脚步，和队友一起动手，把艾草做成一柄小锤。图中的成品可作样式参考。',
    photos: [
      ['成品', '红柄艾草锤与挂绳的成品示例。', 'contain'],
      ['地点', '福善寺的山门与屋檐。'],
    ],
    setup: '和队员一起领取现场材料，跟随守关人的指引制作艾草锤。',
    goal: '全队共同完成艾草锤 DIY。',
  },
  {
    id: 'candy',
    place: '关王庙',
    name: '诸葛帽吃糖',
    point: [565, 718],
    description: '帽枝上的糖近在眼前，伸手却不算数。戴帽的人得让糖摆到嘴边，才能吃到这一口。',
    photos: [
      ['戴帽', '队员仰头去够帽枝上悬着的糖。'],
      ['地点', '关王庙的门楼。'],
    ],
    setup: '选 7 位队员戴上诸葛帽，双手放在身后，不能用手碰帽子或糖果。',
    goal: '晃动帽枝，用嘴咬到吊起的糖果。',
  },
]
export function questForRoute(id?: string, legacyIndex?: string) {
  const questId = id === 'lawn' ? (legacyIndex === '1' ? 'hammer' : 'cuju') : id
  return quests.find((quest) => quest.id === questId)
}
export interface Wanderer extends FieldEntry {
  area: string
  point?: [number, number]
}
export const wanderers: Wanderer[] = [
  {
    id: 'constable',
    name: '巡捕',
    area: '全古镇',
    description:
      '先闻铃声，再见其人。巡捕双脚系着铃铛，携带软质道具，在全古镇巡游，没有固定守候点。',
    setup: '任一队员被巡捕的软质道具碰到，在场队员就要依次和巡捕划拳。',
    goal: '至少半数队员获胜即可免罚；若巡捕赢过半数，就会从队伍手中随机抽走一份碎片。',
    photos: [
      ['装束', '黑红捕快服与高帽的造型参考。', 'contain'],
      ['划拳', '巡捕划拳挑战的手势示意。', 'contain'],
    ],
  },
  {
    id: 'ranger',
    name: '游侠',
    area: '濮绸作坊附近',
    point: [1148, 800],
    description: '濮绸作坊一带有位黑袍游侠。凑齐至少 5 位同伴，就能向他讨教一套「盖世武功」。',
    setup: '全员跟着游侠学三招：闪身步、浪子踢球、狗熊哆嗦毛。',
    goal: '拍摄记录学会的动作，得到游侠认可后领取线索。',
    photos: [
      ['身影', '黑袍游侠的背影与动作参考。', 'contain'],
      ['招式', '活动方案中的三招动作示意。', 'contain'],
    ],
  },
  {
    id: 'escort',
    name: '镖师',
    area: '福善塔附近',
    point: [883, 406],
    description: '镖码散落在福善塔周围。先找宝箱，再去见镖师，这趟寻镖才算走完。',
    setup: '在塔周围寻找 5 个装有货物的镖码宝箱，再前往镖师处，解开箱中的谜题。',
    goal: '替镖师找回散落的镖码，他会赠给队伍一条线索。',
    photos: [
      ['人物', '镖局门前的镖师造型参考。'],
      ['宝箱', '寻找镖码时留意这样的宝箱。', 'contain'],
    ],
  },
  {
    id: 'magistrate',
    name: '大理寺卿',
    area: '魔方塔附近',
    point: [821, 926],
    description:
      '魔方塔旁，大理寺卿正在办案。画面里一处穿帮、两幅图间一点差异，都可能是破案的关键。',
    setup: '随机抽取 2 宗「案件」，全队一起找不同、找不合理之处或穿帮细节。',
    goal: '指出两宗案件里的疑点，协助结案后向大理寺卿领取奖励线索。',
    photos: [
      ['官服', '大理寺卿的红色官服与冠帽。', 'portrait'],
      ['案卷', '古装场景「大家来找茬」题型示意。', 'contain'],
    ],
  },
  {
    id: 'trader',
    name: '黑市商人',
    area: '北更楼附近',
    point: [524, 399],
    description: '北更楼旁的黑袍商人做两种生意：可以明码换卡，也可以凭本事向他赢一张。',
    setup: '攒下的本队交子可以换特殊卡。想比试，就和商人连玩三局；具体比什么，由商人现场出题。',
    goal: '连赢三局，可随机抽取一张卡。直接购买时，不同卡片的价格和用途各不相同。',
    photos: [['装束', '黑市商人全身披着带兜帽的黑袍。', 'portrait']],
  },
  {
    id: 'masked',
    name: '蒙面大侠',
    area: 'ID 设计公寓附近',
    point: [1316, 377],
    description: '在入住酒店右侧的公寓楼附近寻找蒙面人。他摆下的不是擂台，而是一局「极速三子棋」。',
    setup: '找到大侠并发起对局。赶往棋盘落子，在速度与布局之间做决定。',
    goal: '在极速三子棋中战胜蒙面大侠，即可获得线索。',
    photos: [
      ['装束', '蒙面大侠的黑衣与面罩。', 'portrait'],
      ['落子', '队员跑向地面九宫格摆放棋子。', 'contain'],
      ['对局', '队员在九宫格棋盘前争先落子。', 'contain'],
    ],
  },
]
export const tools = [
  ['通关卡', 50, '领取一个 NPC 任务的通关奖励。'],
  ['运气卡', 50, '掷出 4、5、6 点可得 100 交子。'],
  ['免罚卡', 100, '免去一次巡捕惩罚。'],
  ['神偷卡', 120, '从巡捕处随机取一份碎片。'],
  ['改命卡', 500, '指定一位 NPC 向后续队伍给出假消息；全场仅一张。'],
] as const

export const days = [
  {
    number: '01',
    title: '到濮院，入戏',
    rows: [
      ['10:00–11:30', '苏州集合 · 乘大巴出发', '苏州微软公司集合，乘车前往濮院。'],
      ['11:30–12:30', '酒店入住', '梅尚度假酒店 · 濮院镇寺浜路，濮院时尚古镇。'],
      ['12:30–13:30', '午餐', '梅尚度假酒店 · 梅园厅，团队桌餐。'],
      ['13:30–13:50', '全员合影', '按现场通知集合。'],
      [
        '13:50–16:30',
        '濮院诗简 · 团建挑战',
        '领取任务卡，组队寻找诗句碎片。',
        'games',
        '翻开游戏手册',
      ],
      ['16:30 起', '自由活动 · 晚餐自理', '留一段水巷时光，自行安排晚餐。', 'food', '看看餐厅推荐'],
    ],
  },
  {
    number: '02',
    title: '慢游水乡，返程',
    rows: [
      [
        '10:00–12:00',
        '跟讲解游古镇，或参加已报名体验',
        '两项择一；讲解按每组 45 人组织。',
        'itinerary/walk',
        '查看游览安排',
      ],
      ['12:00', '酒店退房', '请提前整理行李。'],
      ['12:30–13:30', '酒店自助午餐', '梅尚度假酒店 · 梅园厅。'],
      ['13:30–15:00', '集合返程', '乘大巴返回苏州；上车点以现场通知为准。'],
    ],
  },
] as const
export const experiences = [
  ['布艺冰箱贴', '和茂新衣庄', 40, 20],
  ['老布银杏发夹', '和茂新衣庄', 30, 38],
  ['竹编风铃', '竹器坊', 60, 48],
  ['竹编冰箱贴', '竹器坊', 30, 38],
  ['打香篆', '福善濮香堂', 30, 79],
  ['银杏书签', '一叶一菩提', 15, 20],
  ['手工书签', '一叶一菩提', 30, 15],
  ['换装体验', '换装店', 180, 50, '需预留 3 小时，留意退房与返程时间'],
  ['宋式点茶', '松月寮', 45, 158, '需提前预约'],
  ['颂钵疗愈', '酒店疗愈中心', 60, 160, '需提前预约'],
  ['圣诞树挂件', '毛线馆', 30, 19, '方案注明无库存'],
  ['小花挂件', '毛线馆', 30, 39],
] as const
export const dinnerSpots = [
  { id: 'xianzi', name: '蚬子滩客栈', style: '农家本地菜', seats: 20, group: '水乡家常' },
  { id: 'gujing', name: '古井餐厅', style: '本地私房菜', seats: 40, group: '水乡家常' },
  { id: 'xiushui', name: '秀水客栈', style: '本地农家菜', seats: 22, group: '水乡家常' },
  { id: 'pujia', name: '濮家小菜馆', style: '融合菜 · 家常小炒', seats: 30, group: '水乡家常' },
  { id: 'shilang', name: '侍郎客栈', style: '农家菜 · 偏辣', seats: 32, group: '水乡家常' },
  {
    id: 'late-supper',
    name: '深夜食堂',
    style: '本地小炒',
    seats: 50,
    group: '水乡家常',
    placeId: 'teahouse',
  },
  { id: 'songyan', name: '宋宴', style: '本地融合菜', seats: 50, group: '水乡家常' },
  { id: 'sanshi', name: '三事阁', style: '南洋铁锅菜 · 江南菜', seats: 145, group: '特色风味' },
  { id: 'leli', name: '乐里冰室', style: '粤菜 · 广式点心', seats: 82, group: '特色风味' },
  { id: 'beilang', name: '北廊棚川式火锅', style: '川式火锅', seats: 80, group: '特色风味' },
]
