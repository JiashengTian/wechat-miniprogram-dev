/**
 * 习惯打卡 - 全局配置
 * 职责：数据持久化、主题应用、全局状态
 */
const time = require('./utils/time')
const ach = require('./utils/achievements')

App({
  onLaunch() {
    const data = this.loadData()
    this.globalData.data = data
    // 启动时应用已保存的主题
    this.applyTheme(data.stg)
  },

  globalData: {
    data: null
  },

  /* ========== 数据持久化 ========== */
  loadData() {
    try {
      const raw = wx.getStorageSync('habit_data')
      if (!raw) return this.getEmptyData()
      const data = JSON.parse(raw)
      return this.mergeDefaults(data)
    } catch (e) {
      console.error('[数据加载失败]', e)
      return this.getEmptyData()
    }
  },

  saveData(data) {
    try {
      wx.setStorageSync('habit_data', JSON.stringify(data))
    } catch (e) {
      console.error('[数据保存失败]', e)
    }
  },

  getEmptyData() {
    return {
      v: 3,
      habits: [],
      records: {},   // { '2026-07-04': { 1: true, 2: true } }
      goals: {},   // { 1: { weekly: 3 } }
      notes: {},   // { 1: { '2026-07-04': '备注内容' } }
      dq: { d: '', t: '' },
      s: {},        // 成就状态
      ap: { c: 0, last: '' },
      stg: {
        theme: 'light',
        accent: '#4a3f35',
        remind: false,
        remindT: '09:00'
      },
      cats: ['健康', '学习', '工作', '生活', '运动', '阅读', '饮食', '美妆', '兴趣', '其他'],
      snd: true,
      pVib: true,
      pomo: { today: 0, date: '', log: [] }
    }
  },

  mergeDefaults(data) {
    const def = this.getEmptyData()
    const fields = [
      'habits','records','goals','notes','dq','s','ap','stg','cats'
    ]
    fields.forEach(f => {
      if (data[f] === undefined || data[f] === null) data[f] = def[f]
    })
    if (typeof data.snd !== 'boolean') data.snd = def.snd
    if (typeof data.pVib !== 'boolean') data.pVib = def.pVib
    if (!data.pomo) data.pomo = def.pomo
    return data
  },

  /* ========== 主题应用 ========== */
  applyTheme(stg) {
    // 更新全局数据
    this.globalData.data.stg = stg
    // 通知所有页面刷新 UI
    const pages = getCurrentPages()
    pages.forEach(p => {
      if (p && p.setData) p.setData({ stg: stg })
    })
  }
})
