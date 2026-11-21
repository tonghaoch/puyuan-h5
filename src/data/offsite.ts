// v1119 participant brief. Coordinates are approximate illustration points, not GPS fixes.
export interface Challenge {
  name: string
  setup: string
  goal: string
}
export interface GameSite {
  id: string
  place: string
  point: [number, number]
  challenges: Challenge[]
}
export const gameSites: GameSite[] = [
  {
    id: 'relay',
    place: '关帝庙',
    point: [1023, 1057],
    challenges: [
      {
        name: '袱传货物',
        setup: '两人一组撑开袱布，在指定区域接力。传递时只能用布，不能用手拿货物。',
        goal: '把大蒜、土豆、玉米三件货物全部传完。',
      },
    ],
  },
  {
    id: 'drum',
    place: '翠冷台',
    point: [1046, 514],
    challenges: [
      {
        name: '同心击鼓',
        setup: '队员各拉一根鼓绳，把球放上鼓面。配合收放绳子颠球，手不碰鼓面。',
        goal: '球不落地，连续颠起 8 次。',
      },
    ],
  },
  {
    id: 'lawn',
    place: '大草坪',
    point: [1008, 588],
    challenges: [
      {
        name: '蹴鞠达人',
        setup: '全队累计 15 人次，每人有两次射门机会，由守关人记录得分。',
        goal: '全队总分超过 250 分。个人双球高分还有机会抽特殊道具，门槛以裁判口径为准。',
      },
      {
        name: '一锤定音',
        setup: '15 位队员依次接力，每人有 15 秒进入指定区域敲气球。',
        goal: '全队合计敲破超过 12 个气球。',
      },
    ],
  },
  {
    id: 'mime',
    place: '梅泾剧场',
    point: [762, 757],
    challenges: [
      {
        name: '哑戏猜古词',
        setup: '选两位队员上台看词卡，只能用动作提示，不能说话。其余队员负责猜词。',
        goal: '在 120 秒内尽量猜对，交守关人计数。',
      },
    ],
  },
  {
    id: 'treasure',
    place: '珍宝馆',
    point: [967, 1076],
    challenges: [
      {
        name: '珍宝馆里的奥秘',
        setup: '全队到馆内领取奥秘卡，根据卡上的提示寻找对应藏品。',
        goal: '填齐卡上的奥秘信息，交给守关人核验。',
      },
    ],
  },
  {
    id: 'mugwort',
    place: '福善寺',
    point: [915, 674],
    challenges: [
      {
        name: '福善艾草锤',
        setup: '和队员一起领取现场材料，跟随守关人的指引制作艾草锤。',
        goal: '全队共同完成艾草锤 DIY。',
      },
    ],
  },
  {
    id: 'candy',
    place: '关王庙',
    point: [605, 695],
    challenges: [
      {
        name: '诸葛帽吃糖',
        setup: '选 7 位队员戴上诸葛帽，双手放在身后，不能用手碰帽子或糖果。',
        goal: '晃动帽枝，用嘴咬到吊起的糖果。',
      },
    ],
  },
]
export const wanderers = [
  [
    '巡捕',
    '全古镇',
    '听见铃声，留意巡捕。触发划拳后，至少半数队员获胜可免罚；否则要交出一份随机碎片。',
  ],
  ['游侠', '濮绸作坊附近', '至少 5 人结伴，向游侠学习招式，完成动作并记录后领取线索。'],
  ['镖师', '福善塔附近', '寻找 5 个装有货物的镖码宝箱，再找镖师破解谜题，换取线索。'],
  ['大理寺卿', '魔方塔附近', '抽取两宗案件，和队员一起找出疑点，提交给大理寺卿。'],
  ['黑市商人', '北更楼附近', '用本队交子换特殊卡；也可接受商人的挑战，连赢三局随机抽卡。'],
  ['蒙面大侠', 'ID 设计公寓附近', '找到蒙面大侠，挑战极速三子棋，获胜后取得线索。'],
] as const
// Only named areas that can be identified on the illustration; never a live NPC pin.
export const roamingAreas: Record<string, [number, number]> = {
  福善塔附近: [886, 378],
  北更楼附近: [515, 364],
  魔方塔附近: [827, 930],
  濮绸作坊附近: [1085, 817],
}
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
