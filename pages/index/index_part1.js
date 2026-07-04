/**
 * 习惯打卡 - 主页面逻辑（完整版）
 * 所有函数在 WXML 中引用均有对应实现
 */
const time = require('../../utils/time')
const ach = require('../../utils/achievements')
const app = getApp()

Page({
  data: {
    statusBarHeight: 20,
    clockStr: '',
    greeting: '',
    dailyQuote: '',
    apDays: 0,
    doneCount: 0,
    totalCount: 0,
    progressPercent: 0,
    progressTitle: '尚无习惯',
    progressSub: '千里之行，始于足下',
    searchText: '',
    filterCat: '',
    showArchived: false,
    cats: [],
    weekDots: [],
    weekTotal: 0,
    habits: [],
    filteredHabits: [],
    editingId: null,
    editingName: '',
    totalHabits: 0,
    suggestions: [],
    newHabitName: '',
    showSettings: false,
    showDetail: false,
    showDashboard: false,
    showCalendar: false,
    showReport: false,
    showCatchup: false,
    showPomodoro: false,
    showConfirm: false,
    showCategoryManager: false,
    stg: {},
    sndEnabled: true,
    pVibEnabled: true,
    themeColors: ['#4a3f35','#2d6a4f','#1e3a5f','#7b2d3e','#5e3a7a','#c76d2e'],
    detailId: null,
    detailHabit: {},
    detailStreak: 0,
    detailBestStreak: 0,
    detailTotal: 0,
    detailDifficulty: 0,
    detailChart: [0,0,0,0,0,0,0],
    detailChartLabels: [],
    detailNote: '',
    detailHistory: [],
    goalOptions: ['无','每周3次','每周5次','每周7次'],
    currentGoalLabel: '无',
    goals: {},
    totalCheckInsAll: 0,
    rankedHabits: [],
    achievements: [],
    calOffset: 0,
    calendarCells: [],
    calendarTitle: '',
    calendarSummary: '',
    reportIsWeek: true,
    reportData: null,
    catchupHabits: [],
    catchupSelectedName: '',
    catchupDays: [],
    pomoFocusLen: 1500,
    pomoSeconds: 1500,
    pomoRunning: false,
    pomoPhase: 'focus',
    pomoPresets: [15,25,30,45],
    customPomoMin: '25',
    pomoMinStr: ['2','5'],
    pomoSecStr: ['0','0'],
    pomoToday: 0,
    pomoTotal: 0,
    pomoLogs: [],
    confirmText: '',
    confirmCallback: null,
    newCatName: '',
  },

  onLoad() {
    try {
      const win = wx.getWindowInfo()
      this.setData({ statusBarHeight: win.statusBarHeight || 20 })
    } catch(e) {
      this.setData({ statusBarHeight: 20 })
    }
    this._initData()
    this._updateClock()
    this._clockTimer = setInterval(() => this._updateClock(), 1000)
    this._page = this
  },

  onUnload() {
    clearInterval(this._clockTimer)
    clearInterval(this._pomoTimer)
  },

  onShow() {
    this._refreshAll()
  },

  // ===== 私有方法（命名加下划线前缀区分）=====
  _initData() {
    const data = app.globalData.data
    if (!data) return
    const q = time.getDailyQuote(data.dq)
    if (!data.dq) data.dq = {}
    data.dq.d = time.todayStr()
    data.dq.t = q
    if (!data.ap) data.ap = { c:0, last:'' }
    const t = time.todayStr()
    if (data.ap.last !== t) {
      const y = new Date(); y.setDate(y.getDate()-1)
      if (data.ap.last === time.dateStr(y)) {
        data.ap.c++
      } else {
        data.ap.c = 1
      }
      data.ap.last = t
    }
    app.saveData(data)
    this._refreshAll()
  },

  _updateClock() {
    const n = new Date()
    const h = String(n.getHours()).padStart(2,'0')
    const m = String(n.getMinutes()).padStart(2,'0')
    const s = String(n.getSeconds()).padStart(2,'0')
    const ds = time.formatDate(n)
    this.setData({
      clockStr: ds + ' ' + h + ':' + m + ':' + s,
      greeting: time.getGreeting()
    })
  },

  _refreshAll() {
    const data = app.globalData.data
    if (!data) return
    this.setData({
      habits: data.habits || [],
      todayStr: time.todayStr(),
      goals: data.goals || {},
      cats: data.cats || [],
      stg: data.stg || {},
      sndEnabled: !!data.snd,
      pVibEnabled: !!data.pVib,
      dailyQuote: (data.dq && data.dq.t) || '日拱一卒',
      apDays: (data.ap && data.ap.c) || 0,
    })
    this._updateProgress()
    this._updateWeekDots()
    this._updateFilteredHabits()
    this._updateStats()
    this._updateSuggestions()
    this._updateAchievements()
  },

  _updateProgress() {
    const data = app.globalData.data
    const t = time.todayStr()
    const dr = (data.records && data.records[t]) || {}
    const active = (data.habits || []).filter(h => !h.archived)
    const done = active.filter(h => !!dr[h.id]).length
    const total = active.length
    const rate = total > 0 ? Math.round(done / total * 100) : 0
    let title = '尚无习惯'
    let sub = '千里之行，始于足下'
    if (total > 0) {
      if (done === total) {
        title = '诸事皆毕 🎉'
        sub = '功不唐捐，日有所进'
      } else {
        title = '已完成 ' + done + '/' + total
        sub = '行远自迩，登高自卑'
      }
    }
    this.setData({ doneCount: done, totalCount: total, progressPercent: rate, progressTitle: title, progressSub: sub })
  },

  _updateWeekDots() {
    const data = app.globalData.data
    const mon = time.getMonday(new Date())
    const today = time.todayStr()
    const dots = [0,1,2,3,4,5,6].map(i => {
      const dt = time.addDays(mon, i)
      const ds = time.dateStr(dt)
      const dr = (data.records && data.records[ds]) || {}
      const doneCount = Object.keys(dr).length
      const activeCount = (data.habits || []).filter(h => !h.archived).length
      let cls = 'dot'
      let label = ''
      if (activeCount > 0 && doneCount >= activeCount) {
        cls += ' filled'
        label = '✓'
      } else if (doneCount > 0) {
        cls += ' partial'
        label = String(doneCount)
      }
      if (ds === today) cls += ' today'
      return { name: time.dayName(i), cls, label, date: ds }
    })
    let weekTotal = 0
    for (let w = 0; w < 7; w++) {
      const wds = time.dateStr(time.addDays(mon, w))
      const wr = (data.records && data.records[wds]) || {}
      for (const k in wr) if (wr[k]) weekTotal++
    }
    this.setData({ weekDots: dots, weekTotal })
  },

  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    let list = data.habits.slice()
    if (this.data.showArchived) {
      list = list.filter(h => h.archived)
    } else {
      list = list.filter(h => !h.archived)
    }
    if (this.data.filterCat) {
      list = list.filter(h => h.category === this.data.filterCat)
    }
    if (this.data.searchText && this.data.searchText.trim()) {
      const q = this.data.searchText.trim().toLowerCase()
      list = list.filter(h => h.name.toLowerCase().indexOf(q) !== -1)
    }
    const records = data.records || {}
    const goals = data.goals || {}
    const mon = time.getMonday(new Date())
    const today = time.todayStr()
    const todayRecord = (records[today] || {})
    list = list.map(h => {
      const checked = !!todayRecord[h.id]
      const streak = time.calcStreak(h.id, records, today)
      const weeklyGoal = (goals[h.id] && goals[h.id].weekly) || 0
      let goalDone = false
      let goalMissed = false
      if (weeklyGoal > 0) {
        let cnt = 0
        for (let w = 0; w < 7; w++) {
          const ds = time.dateStr(time.addDays(mon, w))
          if (records[ds] && records[ds][h.id]) cnt++
        }
        goalDone = cnt >= weeklyGoal
        goalMissed = !goalDone
      }
      return Object.assign({}, h, {
        _checked: checked,
        _streak: streak,
        _weeklyGoal: weeklyGoal,
        _goalDone: goalDone,
        _goalMissed: goalMissed,
      })
    })
    this.setData({ filteredHabits: list })
  },

  _updateStats() {
    const data = app.globalData.data
    if (!data) return
    const active = (data.habits || []).filter(h => !h.archived)
    let total = 0
    const recs = data.records || {}
    for (const d in recs) {
      const r = recs[d]
      if (r) for (const k in r) if (r[k]) total++
    }
    this.setData({ totalHabits: active.length, totalCheckInsAll: total })
  },

  _updateSuggestions() {
    const data = app.globalData.data
    if (!data) return
    const used = (data.habits || []).map(h => h.name)
    const available = time.SUGGESTIONS.filter(s => used.indexOf(s) === -1)
    const shuffled = available.sort(() => Math.random() - 0.5)
    this.setData({ suggestions: shuffled.slice(0, 5) })
  },

  _updateAchievements() {
    const data = app.globalData.data
    if (!data) return
    const list = ach.getAchievements(data)
    this.setData({ achievements: list })
  },

  // ===== 打卡/取消 =====
  toggleCheckin(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const t = time.todayStr()
    if (!data.records) data.records = {}
    if (!data.records[t]) data.records[t] = {}
    const wasChecked = !!data.records[t][id]
    if (wasChecked) {
      delete data.records[t][id]
    } else {
      data.records[t][id] = true
    }
    const unlocks = ach.checkAchievements(data)
    app.saveData(data)
    this._refreshAll()
    if (!wasChecked) {
      const habit = (data.habits || []).find(h => h.id === id)
      if (habit) wx.showToast({ title: '✅ ' + habit.name, icon: 'none' })
      const dr2 = (data.records[t] || {})
      const active2 = (data.habits || []).filter(h => !h.archived)
      if (active2.length > 0 && active2.every(h => dr2[h.id])) {
        setTimeout(() => {
          wx.showModal({
            title: '🎉 诸事皆毕',
            content: '今日所有习惯已完成，功不唐捐！',
            showCancel: false,
            confirmText: '👍'
          })
        }, 600)
      }
    }
    if (unlocks && unlocks.length > 0) {
      setTimeout(() => {
        wx.showModal({
          title: '🎉 成就解锁',
          content: unlocks.join('\n'),
          showCancel: false,
          confirmText: '太棒了！'
        })
      }, 800)
    }
  },

  // ===== 归档/恢复 =====
  toggleArchive(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(h => h.id === id)
    if (!habit) return
    wx.showModal({
      title: '归档确认',
      content: '归档「' + habit.name + '」？归档后数据保留，可在归档区恢复。',
      success: (res) => {
        if (res.confirm) {
          habit.archived = true
          app.saveData(data)
          this._refreshAll()
          wx.showToast({ title: '📦 已归档', icon: 'none' })
        }
      }
    })
  },

  restoreHabit(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(h => h.id === id)
    if (habit) {
      habit.archived = false
      app.saveData(data)
      this._refreshAll()
      wx.showToast({ title: '↩ 已恢复', icon: 'none' })
    }
  },

  // ===== 编辑习惯名称 =====
  startEdit(e) {
    const id = Number(e.currentTarget.dataset.id)
    const name = e.currentTarget.dataset.name || ''
    this.setData({ editingId: id, editingName: name })
  },

  onEditInput(e) {
    this.setData({ editingName: e.detail.value || '' })
  },

  saveRename() {
    const id = this.data.editingId
    if (!id) { this.setData({ editingId: null }); return }
    const name = (this.data.editingName || '').trim()
    if (!name) { this.setData({ editingId: null }); return }
    const data = app.globalData.data
    const habit = (data.habits || []).find(h => h.id === id)
    if (habit) {
      habit.name = name
      app.saveData(data)
      this._refreshAll()
    }
    this.setData({ editingId: null })
  },
