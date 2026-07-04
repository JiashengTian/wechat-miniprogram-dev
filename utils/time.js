/**
 * 时间工具函数 — 习惯打卡
 * 所有日期返回 'YYYY-MM-DD' 字符串
 */
const todayStr = () => {
  const d = new Date()
  return dateStr(d)
}

const dateStr = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return y + '-' + m + '-' + day
}

const formatDate = (d) => {
  const w = ['日','一','二','三','四','五','六'][d.getDay()]
  return (d.getMonth()+1) + '月' + d.getDate() + '日（周' + w + '）'
}

const formatShort = (d) => {
  return (d.getMonth()+1) + '/' + d.getDate()
}

const dayName = (i) => {
  return ['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][i]
}

const getMonday = (d) => {
  const dt = new Date(d)
  const day = dt.getDay()  // 0=周日
  const diff = day === 0 ? -6 : 1 - day
  dt.setDate(dt.getDate() + diff)
  return dt
}

const addDays = (d, n) => {
  const dt = new Date(d)
  dt.setDate(dt.getDate() + n)
  return dt
}

const getDailyQuote = (dq) => {
  const q = [
    '千里之行，始于足下',
    '不积跬步，无以至千里',
    '功不唐捐，玉汝于成',
    '日拱一卒，功不唐捐',
    '业精于勤，荒于嬉',
    '锲而不舍，金石可镂',
    '每天进步一点点',
    '好习惯是人生最好的投资',
    '坚持就是胜利',
    '今天的努力，明天的底气'
  ]
  // 按日期选一句（稳定）
  const d = todayStr()
  let h = 0
  for (let i = 0; i < d.length; i++) h = (h * 31 + d.charCodeAt(i)) | 0
  return q[((h % q.length) + q.length) % q.length]
}

const getGreeting = () => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  if (h < 22) return '晚上好'
  return '夜深了'
}

// 计算当前连续天数（到 today 为止）
const calcStreak = (habitId, records, today) => {
  let d = new Date(today)
  let streak = 0
  while (true) {
    const ds = dateStr(d)
    if (records[ds] && records[ds][habitId]) {
      streak++
      d.setDate(d.getDate() - 1)
    } else {
      break
    }
  }
  return streak
}

// 计算历史最佳连续
const calcBestStreak = (habitId, records) => {
  // 遍历所有有记录的日期，找最长连续
  const dates = Object.keys(records)
    .filter(d => records[d] && records[d][habitId])
    .sort()
  if (dates.length === 0) return 0
  let best = 1, cur = 1
  for (let i = 1; i < dates.length; i++) {
    const prev = new Date(dates[i-1])
    const curD = new Date(dates[i])
    prev.setDate(prev.getDate() + 1)
    if (prev.getTime() === curD.getTime()) {
      cur++
      if (cur > best) best = cur
    } else {
      cur = 1
    }
  }
  return best
}

// 统计总打卡次数
const countCheckIns = (habitId, records) => {
  let n = 0
  for (const d in records) {
    if (records[d] && records[d][habitId]) n++
  }
  return n
}

const SUGGESTIONS = [
  '晨跑', '阅读30分钟', '早睡', '早起',
  '喝水8杯', '冥想10分钟', '写日记', '学英语',
  '不吃零食', '跑步', '瑜伽', '背单词',
  '忌熬夜', '忌拖延', '忌暴饮暴暴食', '每日复盘'
]

module.exports = {
  todayStr, dateStr, formatDate, formatShort,
  dayName, getMonday, addDays,
  getDailyQuote, getGreeting,
  calcStreak, calcBestStreak, countCheckIns,
  SUGGESTIONS
}
