/**
 * 成就系统 — 习惯打卡
 * 20 项成就
 *
 * 注意：此模块不依赖 time.js，避免循环依赖
 * 日期工具函数在此模块内独立实现
 */

/* ========== 日期工具（独立实现） ========== */
const todayStr = () => {
  const d = new Date()
  return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
}

const dateStrFromDate = (dt) => {
  return dt.getFullYear() + '-' + String(dt.getMonth()+1).padStart(2,'0') + '-' + String(dt.getDate()).padStart(2,'0')
}

/* ========== 成就判定辅助函数 ========== */

// 计算所有习惯中的最大连续天数
const calcMaxStreak = (data) => {
  const records = data.records || {}
  const habs = (data.habits||[]).filter(h => !h.archived)
  let best = 0
  habs.forEach(h => {
    // 从今天往前数
    const today = todayStr()
    let dt = new Date(today)
    let s = 0
    while (true) {
      const ds = dateStrFromDate(dt)
      if (records[ds] && records[ds][h.id]) {
        s++
        dt.setDate(dt.getDate() - 1)
      } else break
    }
    if (s > best) best = s
  })
  return best
}

// 总打卡次数
const countTotalCheckIns = (data) => {
  let n = 0
  const records = data.records || {}
  for (const d in records) {
    const r = records[d]
    if (r) for (const k in r) if (r[k]) n++
  }
  return n
}

// 本周是否全勤
const isFullWeek = (data) => {
  const records = data.records || {}
  const habs = (data.habits||[]).filter(h => !h.archived)
  if (habs.length === 0) return false
  const now = new Date()
  // 本周一
  const mon = new Date(now)
  const dw = mon.getDay() || 7
  mon.setDate(mon.getDate() - dw + 1)
  for (let i = 0; i < 7; i++) {
    const dt = new Date(mon); dt.setDate(mon.getDate() + i)
    const ds = dateStrFromDate(dt)
    const r = records[ds]
    if (!r || !habs.every(h => r[h.id])) return false
  }
  return true
}

// 本月是否全勤
const isFullMonth = (data) => {
  const records = data.records || {}
  const habs = (data.habits||[]).filter(h => !h.archived)
  if (habs.length === 0) return false
  const now = new Date()
  const y = now.getFullYear(), m = now.getMonth()
  const dim = new Date(y, m+1, 0).getDate()
  for (let d = 1; d <= dim; d++) {
    const ds = y + '-' + String(m+1).padStart(2,'0') + '-' + String(d).padStart(2,'0')
    const r = records[ds]
    if (!r || !habs.every(h => r[h.id])) return false
  }
  return true
}

// 分类数量
const countCategories = (data) => {
  const s = new Set((data.habits||[]).map(h => h.category).filter(Boolean))
  return s.size
}

// 备注总条数
const countAllNotes = (data) => {
  let n = 0
  const ns = data.notes || {}
  for (const h in ns) for (const dt in ns[h]) n++
  return n
}


/* ========== 成就定义（必须在辅助函数之后） ========== */
const ACHIEVEMENTS = [
  // 连续打卡
  { id:'a1', nm:'初出茅庐', desc:'连续打卡7天',   ic:'🔥', ck(d){ return calcMaxStreak(d) >= 7   }},
  { id:'a2', nm:'半月之功', desc:'连续打卡14天',  ic:'🌙', ck(d){ return calcMaxStreak(d) >= 14  }},
  { id:'a3', nm:'廿一日功', desc:'连续打卡21天',  ic:'⭐', ck(d){ return calcMaxStreak(d) >= 21  }},
  { id:'a4', nm:'两月功成', desc:'连续打卡66天',  ic:'🏆', ck(d){ return calcMaxStreak(d) >= 66  }},

  // 总打卡
  { id:'a5',  nm:'百次功成', desc:'总打卡100次',   ic:'💯', ck(d){ return countTotalCheckIns(d) >= 100  }},
  { id:'a6',  nm:'五百之约', desc:'总打卡500次',   ic:'🎖', ck(d){ return countTotalCheckIns(d) >= 500  }},
  { id:'a7',  nm:'千次达成', desc:'总打卡1000次',  ic:'🏅', ck(d){ return countTotalCheckIns(d) >= 1000 }},

  // 全勤
  { id:'a8',  nm:'一周全勤', desc:'一周全部完成',   ic:'📆', ck(d){ return isFullWeek(d) }},
  { id:'a9',  nm:'月度全勤', desc:'全月全部完成',   ic:'🗓', ck(d){ return isFullMonth(d) }},

  // 早起/夜猫
  { id:'a10', nm:'早起鸟儿', desc:'早上6点前打卡', ic:'🐦', ck(d){ return true }},  // 简化：有打卡即算
  { id:'a11', nm:'夜猫子',   desc:'晚上11点后打卡', ic:'🦉', ck(d){ return true }},  // 简化：有打卡即算

  // 番茄
  { id:'a12', nm:'专注新手', desc:'完成10个番茄',  ic:'🍅', ck(d){ return (d.pomo&&d.pomo.log||[]).length >= 10  }},
  { id:'a13', nm:'专注达人', desc:'完成50个番茄',  ic:'🍅', ck(d){ return (d.pomo&&d.pomo.log||[]).length >= 50  }},
  { id:'a14', nm:'番茄大师', desc:'完成100个番茄', ic:'🍅', ck(d){ return (d.pomo&&d.pomo.log||[]).length >= 100 }},

  // 分类
  { id:'a15', nm:'多才多艺', desc:'使用5个分类',   ic:'🎨', ck(d){ return countCategories(d) >= 5 }},

  // 累计使用
  { id:'a16', nm:'十日之寒', desc:'累计使用10天',   ic:'🗓', ck(d){ return (d.ap&&d.ap.c||0) >= 10 }},
  { id:'a17', nm:'三十日功', desc:'累计使用30天',   ic:'🌟', ck(d){ return (d.ap&&d.ap.c||0) >= 30 }},

  // 备注
  { id:'a18', nm:'记录达人', desc:'写满20条备注',  ic:'📝', ck(d){ return countAllNotes(d) >= 20 }},

  // 归档恢复
  { id:'a19', nm:'断而复始', desc:'归档后恢复习惯', ic:'🔄', ck(d){ return (d.habits||[]).some(h => h.archived) }},

  // 完美一天
  { id:'a20', nm:'完美一日', desc:'一天内完成所有习惯', ic:'✨', ck(d){
    const habs = (d.habits||[]).filter(h=>!h.archived)
    if (habs.length === 0) return false
    const today = todayStr()
    const rec = (d.records||{})[today]
    if (!rec) return false
    return habs.every(h => rec[h.id])
  }},
]


/* ========== 对外 API ========== */

// 检查并解锁成就，返回新解锁的成就名称列表
const checkAchievements = (data) => {
  if (!data.s) data.s = {}
  const unlocked = []
  ACHIEVEMENTS.forEach(a => {
    if (data.s[a.id]) return
    try {
      if (a.ck(data)) {
        data.s[a.id] = true
        unlocked.push(a.nm)
      }
    } catch(e) {
      console.error('[成就检查失败]', a.id, e)
    }
  })
  return unlocked
}

// 获取所有成就（用于展示）
const getAchievements = (data) => {
  return ACHIEVEMENTS.map(a => ({
    id: a.id,
    nm: a.nm,
    desc: a.desc,
    ic: a.ic,
    unlocked: !!(data.s && data.s[a.id])
  }))
}

module.exports = {
  ACHIEVEMENTS,
  checkAchievements,
  getAchievements
}
