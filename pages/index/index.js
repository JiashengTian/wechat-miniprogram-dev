/**
 * 习惯打卡 - 主页面逻辑（完整修正版 v4）
 * 修复：标题对齐、番茄钟下移、添加删除功能、精致确认弹窗
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
    progressStyle: 'width:0%',
    progressTitle: '尚无习惯',
    progressSub: '千里之行，始于足下',
    searchText: '',
    filterCat: '',
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
    showCatPicker: false,
    catPickerId: null,
    catPickerName: '',
    catPickerCur: '',
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
    _confirmAction: '',
    _confirmId: null,
    _confirmEmoji: '❓',
    _confirmTitle: '',
    _confirmDanger: false,
    dragId: null,
    showAchievePopup: false,
    achievePopupData: null,
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
  },

  onUnload() {
    clearInterval(this._clockTimer)
    clearInterval(this._pomoTimer)
  },

  onShow() {
    this._refreshAll()
  },

  onReady() {
    this._measureItemHeight()
  },

  _measureItemHeight() {
    const self = this
    const query = wx.createSelectorQuery()
    query.select('.habit-item').boundingClientRect(function(rect) {
      if (rect && rect.height) self._itemHeight = rect.height
    }).exec()
  },

  stopProp() {},

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

  _refreshAll(animate) {
    const data = app.globalData.data
    if (!data) return
    const pomoToday = (data.pomo && data.pomo.date === time.todayStr()) ? (data.pomo.today || 0) : 0
    const pomoLogs = (data.pomo && data.pomo.log) || []
    this.setData({
      habits: data.habits,
      todayStr: time.todayStr(),
      goals: data.goals || {},
      cats: data.cats,
      stg: data.stg,
      sndEnabled: data.snd,
      pVibEnabled: data.pVib,
      dailyQuote: data.dq && data.dq.t || '日拱一卒',
      apDays: (data.ap && data.ap.c) || 0,
      pomoToday: pomoToday,
      pomoTotal: (data.pomo && data.pomo.total) || 0,
      pomoLogs: pomoLogs,
    })
    this._updateProgress()
    this._updateWeekDots()
    this._updateFilteredHabits(animate)
    this._updateStats()
    this._updateSuggestions()
    this._updateAchievements()
  },

  // 防抖：避免短时间内多次刷新
  _refreshAllDebounced() {
    if (this._refreshTimer) clearTimeout(this._refreshTimer)
    this._refreshTimer = setTimeout(function() {
      this._refreshAll()
    }.bind(this), 100)
  },

  _updateProgress() {
    const data = app.globalData.data
    const t = time.todayStr()
    const dr = (data.records && data.records[t]) || {}
    const active = (data.habits || [])
    const done = active.filter(function(h) { return dr[h.id] }).length
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
    this.setData({
      doneCount: done,
      totalCount: total,
      progressPercent: rate,
      progressStyle: 'width:' + rate + '%',
      progressTitle: title,
      progressSub: sub,
    })
  },

  _updateWeekDots() {
    const data = app.globalData.data
    const mon = time.getMonday(new Date())
    const today = time.todayStr()
    const dots = [0,1,2,3,4,5,6].map(function(i) {
      const dt = time.addDays(mon, i)
      const ds = time.dateStr(dt)
      const dr = (data.records && data.records[ds]) || {}
      const dc = Object.keys(dr).length
      const ac = data.habits.length
      let cls = 'dot'
      let label = ''
      if (ac > 0 && dc >= ac) {
        cls += ' filled'
        label = '✓'
      } else if (dc > 0) {
        cls += ' partial'
        label = String(dc)
      }
      if (ds === today) cls += ' today'
      return { name: time.dayName(i), cls: cls, label: label, date: ds }
    })
    let weekTotal = 0
    for (let w = 0; w < 7; w++) {
      const wds = time.dateStr(time.addDays(mon, w))
      const wr = (data.records && data.records[wds]) || {}
      for (const k in wr) if (wr[k]) weekTotal++
    }
    this.setData({ weekDots: dots, weekTotal: weekTotal })
  },

  _updateFilteredHabits(animate) {
    const data = app.globalData.data
    if (!data || !data.habits) return
    const records = data.records || {}
    const todayStr = time.todayStr()
    const todayRec = records[todayStr] || {}

    // 计算火花值、打勾状态、连续天数
    // 本周一（Date 对象，用于周目标统计）
    const weekStart = (function() {
      const d = new Date()
      const day = d.getDay()
      const diff = day === 0 ? -6 : 1 - day
      d.setDate(d.getDate() + diff)
      return d
    })()

    let list = data.habits.map(function(h) {
      const total = time.countCheckIns(h.id, records)
      const streak = time.calcStreak(h.id, records, todayStr)
      const checked = !!todayRec[h.id]
      // 周目标
      const _goalRaw = (this.data.goals && this.data.goals[h.id]) || 0
      const goal = typeof _goalRaw === 'object' ? (_goalRaw.weekly || 0) : _goalRaw
      let weekCount = 0
      if (goal > 0) {
        for (let i = 0; i < 7; i++) {
          const dt = time.addDays(weekStart, i)
          const ds = time.dateStr(dt)
          if (ds > todayStr) break
          if (records[ds] && records[ds][h.id]) weekCount++
        }
      }
      return Object.assign({}, h, {
        spark: total + streak * 2,
        _checked: checked,
        _streak: streak,
        _total: total,
        _weeklyGoal: goal,
        _goalDone: goal > 0 && weekCount >= goal,
        _goalMissed: goal > 0 && weekCount < goal
      })
    }.bind(this))
    list.sort(function(a, b) { return (b.spark || 0) - (a.spark || 0) })

    // 过滤
    if (this.data.filterCat) {
      list = list.filter(function(h) { return h.category === this.data.filterCat }.bind(this))
    }
    if (this.data.searchText && this.data.searchText.trim()) {
      const kw = this.data.searchText.trim().toLowerCase()
      list = list.filter(function(h) { return h.name.toLowerCase().indexOf(kw) !== -1 })
    }

    // 是否需要滑动动画：只在顺序改变且非首次加载时
    const oldList = this.data.filteredHabits || []
    const orderChanged = oldList.length > 0 && list.length > 0 &&
      oldList.some(function(h, i) { return h.id !== (list[i] && list[i].id) })

    if (animate && orderChanged && this._itemHeight) {
      this._runReorderAnimation(oldList, list)
    } else {
      this.setData({ filteredHabits: list, itemAnimations: {} })
    }
  },

  _runReorderAnimation(oldList, newList) {
    const self = this
    const itemHeight = this._itemHeight || 70
    const oldIndexMap = {}
    oldList.forEach(function(h, i) { oldIndexMap[h.id] = i })

    const anims = {}
    newList.forEach(function(h, newIdx) {
      const oldIdx = oldIndexMap[h.id]
      if (typeof oldIdx === 'number' && oldIdx !== newIdx) {
        anims[h.id] = { moveDistance: (oldIdx - newIdx) * itemHeight }
      }
    })

    // 先设置偏移量，再下一帧更新列表，让新列表里的项以旧位置出现
    this.setData({ itemAnimations: anims })

    setTimeout(function() {
      self.setData({ filteredHabits: newList }, function() {
        setTimeout(function() {
          self.setData({ itemAnimations: {} })
        }, 30)
      })
    }, 30)

    // 550ms 后强制清空，防止残留
    if (this._animTimer) clearTimeout(this._animTimer)
    this._animTimer = setTimeout(function() {
      self.setData({ itemAnimations: {} })
    }, 600)
  },

  _updateStats() {
    const data = app.globalData.data
    if (!data) return
    const active = (data.habits || []).filter(function(h) { return !h.archived })
    let total = 0
    const records = data.records || {}
    for (const d in records) {
      const r = records[d]
      if (r) for (const k in r) if (r[k]) total++
    }
    this.setData({
      totalHabits: active.length,
      totalCheckInsAll: total,
    })
  },

  _updateSuggestions() {
    const data = app.globalData.data
    if (!data) return
    const used = (data.habits || []).map(function(h) { return h.name })
    const available = time.SUGGESTIONS.filter(function(s) { return used.indexOf(s) === -1 })
    const shuffled = available.sort(function() { return Math.random() - 0.5 })
    this.setData({ suggestions: shuffled.slice(0, 5) })
  },

  _updateAchievements() {
    const data = app.globalData.data
    if (!data) return
    const list = ach.getAchievements(data)
    this.setData({ achievements: list })
  },

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
    this._refreshAll(true)
    if (!wasChecked) {
      const habit = (data.habits || []).find(function(h) { return h.id === id })
      if (habit) wx.showToast({ title: '✅ ' + habit.name, icon: 'none' })
      // 触发动画：找到对应的 habit-item 并添加 just-checked 类
      this.setData({ justCheckedId: id })
      setTimeout(function() {
        this.setData({ justCheckedId: null })
      }.bind(this), 500)
      const dr = (data.records[t] || {})
      const active = (data.habits || []).filter(function(h) { return !h.archived })
      if (active.length > 0 && active.every(function(h) { return dr[h.id] })) {
        setTimeout(function() {
          this.setData({ showAllDonePopup: true })
        }.bind(this), 600)
      }
    }
    if (unlocks && unlocks.length > 0) {
      setTimeout(function() {
        // 使用自定义弹窗
        this.setData({
          showAchievementPopup: true,
          achievementPopupData: { ic: '🏆', nm: unlocks.join('\n') }
        })
}.bind(this), 800)
    }
  },

  confirmDeleteHabit(e) {
    const id = Number(e.currentTarget.dataset.id)
    const name = e.currentTarget.dataset.name || ''
    this.setData({
      showConfirm: true,
      confirmText: '确定删除习惯「' + name + '」？\n删除后数据不可恢复',
      _confirmAction: 'deleteHabit',
      _confirmId: id,
      _confirmEmoji: '🗑',
      _confirmTitle: '删除习惯',
      _confirmDanger: true,
    })
  },

  doDeleteHabit() {
    const id = this.data._confirmId
    const data = app.globalData.data
    data.habits = (data.habits || []).filter(function(h) { return h.id !== id })
    // Also clean up related data
    if (data.records) {
      for (const d in data.records) {
        if (data.records[d] && data.records[d][id]) {
          delete data.records[d][id]
        }
      }
    }
    if (data.notes && data.notes[id]) delete data.notes[id]
    if (data.goals && data.goals[id]) delete data.goals[id]
    app.saveData(data)

    this._refreshAll()
    wx.showToast({ title: '🗑 已删除', icon: 'none' })
  },


  onNameTap(e) {
    const now = Date.now()
    const last = this.data._lastNameTap || 0
    if (now - last < 350) {
      // 双击：进入编辑
      this.setData({ _lastNameTap: 0 })
      this.startEdit(e)
    } else {
      // 轻点：显示全名
      this.setData({ _lastNameTap: now })
      const name = e.currentTarget.dataset.name || ''
      wx.showToast({ title: name, icon: 'none', duration: 1500 })
    }
  },

  startEdit(e) {
    const id = Number(e.currentTarget.dataset.id)
    const name = e.currentTarget.dataset.name || ''
    this.setData({ editingId: id, editingName: name })
  },

  onEditInput(e) {
    this.setData({ editingName: e.detail.value })
  },

  saveRename(e) {
    const id = this.data.editingId
    if (!id) return
    const name = (this.data.editingName || '').trim()
    if (!name) { this.setData({ editingId: null }); return }
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (habit) {
      habit.name = name
      app.saveData(data)
      this._refreshAll()
    }
    this.setData({ editingId: null })
  },

  onSearchInput(e) {
    const val = (e && e.detail && e.detail.value || '').trim()
    this.setData({ searchText: val })
    this._updateFilteredHabits()
  },

  onSearchConfirm(e) {
    const val = (e && e.detail && e.detail.value || '').trim()
    this.setData({ searchText: val })
    this._updateFilteredHabits()
  },

  clearSearch() {
    this.setData({ searchText: '' })
    this._updateFilteredHabits()
  },

  setFilter(e) {
    const cat = (e.currentTarget.dataset.cat || '').trim()
    this.setData({ filterCat: cat })
    this._updateFilteredHabits()
    this._updateSuggestions()
  },

  onNewHabitInput(e) {
    this.setData({ newHabitName: e.detail.value || '' })
  },

  doAddHabit() {
    const name = (this.data.newHabitName || '').trim()
    if (!name) { wx.showToast({ title: '输入习惯名称', icon: 'none' }); return }
    const data = app.globalData.data
    if (!data || !data.habits) return
    let maxId = 0
    data.habits.forEach(function(h) { if (h.id > maxId) maxId = h.id })
    const cat = (this.data.filterCat && !this.data.showArchived) ? this.data.filterCat : ''
    data.habits.push({
      id: maxId + 1,
      name: name,
      category: cat,
      difficulty: 0,
    })
    app.saveData(data)
    this.setData({ newHabitName: '' })
    this._refreshAll()
    wx.showToast({ title: '✨ 已添加', icon: 'none' })
  },

  addSuggestion(e) {
    const name = e.currentTarget.dataset.name || ''
    if (!name) return
    const data = app.globalData.data
    if (!data || !data.habits) return
    let maxId = 0
    data.habits.forEach(function(h) { if (h.id > maxId) maxId = h.id })
    data.habits.push({
      id: maxId + 1,
      name: name,
      category: '',
      difficulty: 0,
    })
    app.saveData(data)
    this._refreshAll()
    wx.showToast({ title: '✨ 已添加', icon: 'none' })
  },

  openSettings() { this.setData({ showSettings: true }) },

  closeSettingsOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showSettings: false })
  },

  closeSettings() { this.setData({ showSettings: false }) },

  toggleTheme() {
    const data = app.globalData.data
    data.stg.theme = data.stg.theme === 'light' ? 'dark' : 'light'
    app.saveData(data)
    this.setData({ stg: data.stg })
    app.applyTheme(data.stg)
  },

  setAccent(e) {
    const color = e.currentTarget.dataset.color || ''
    if (!color) return
    const data = app.globalData.data
    data.stg.accent = color
    app.saveData(data)
    this.setData({ stg: data.stg })
    app.applyTheme(data.stg)
  },

  toggleReminder() {
    const data = app.globalData.data
    data.stg.remind = !data.stg.remind
    app.saveData(data)
    this.setData({ stg: data.stg })
  },

  onRemindTimeChange(e) {
    const data = app.globalData.data
    data.stg.remindT = e.detail.value || '09:00'
    app.saveData(data)
    this.setData({ stg: data.stg })
  },

  toggleSound() {
    const data = app.globalData.data
    data.snd = !data.snd
    app.saveData(data)
    this.setData({ sndEnabled: data.snd })
  },

  toggleVibration() {
    const data = app.globalData.data
    data.pVib = !data.pVib
    app.saveData(data)
    this.setData({ pVibEnabled: data.pVib })
  },

  openCategoryManagerFromSettings() {
    this.setData({ showSettings: false })
    setTimeout(function() { this.setData({ showCategoryManager: true }) }.bind(this), 300)
  },

  resetAll() {
    this.setData({
      showConfirm: true,
      confirmText: '将永久删除全部数据，此操作不可恢复！',
      _confirmAction: 'reset',
      _confirmEmoji: '⚠️',
      _confirmTitle: '重置所有数据',
      _confirmDanger: true,
    })
  },

  openDetail(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (!habit) return
    const t = time.todayStr()
    const chart = []
    for (let i = 6; i >= 0; i--) {
      const dt = time.addDays(new Date(), -i)
      const ds = time.dateStr(dt)
      chart.push((data.records && data.records[ds] && data.records[ds][id]) ? 1 : 0)
    }
    const max = Math.max(1, chart.reduce(function(a,b){ return a+b }, 0))
    const chartPct = chart.map(function(v) { return v / max * 100 })
    const detailChartStyles = chartPct.map(function(v) { return 'height:' + Math.round(v) + '%' })
    const chartLabels = [0,1,2,3,4,5,6].map(function(i) {
      const dt = time.addDays(new Date(), -(6-i))
      return time.formatShort(dt)
    })
    const _goalRaw = ((data.goals || {})[id]) || 0
    const goalVal = typeof _goalRaw === 'object' ? (_goalRaw.weekly || 0) : _goalRaw
    const goalLabels = ['无','每周3次','每周5次','每周7次']
    const goalIdx = goalVal === 0 ? 0 : goalVal === 3 ? 1 : goalVal === 5 ? 2 : 3
    const history = []
    if (data.notes && data.notes[id]) {
      Object.keys(data.notes[id])
        .filter(function(d) { return d !== t })
        .sort()
        .reverse()
        .slice(0, 5)
        .forEach(function(d) {
          history.push({ date: d, note: data.notes[id][d] })
        })
    }
    this.setData({
      showDetail: true,
      detailId: id,
      detailHabit: habit,
      detailStreak: time.calcStreak(id, data.records || {}, t),
      detailBestStreak: time.calcBestStreak(id, data.records || {}),
      detailTotal: time.countCheckIns(id, data.records || {}),
      detailDifficulty: habit.difficulty || 0,
      detailChart: chartPct,
      detailChartStyles: detailChartStyles,
      detailChartLabels: chartLabels,
      detailNote: (data.notes && data.notes[id] && data.notes[id][t]) || '',
      detailHistory: history,
      currentGoalLabel: goalLabels[goalIdx],
    })
  },

  closeDetailOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showDetail: false })
  },

  closeDetail() { this.setData({ showDetail: false, detailId: null }) },

  onGoalChange(e) {
    const vals = [0, 3, 5, 7]
    const labels = ['无','每周3次','每周5次','每周7次']
    const idx = e.detail.value
    const v = vals[idx] || 0
    const id = this.data.detailId
    if (!id) return
    const data = app.globalData.data
    if (!data.goals) data.goals = {}
    data.goals[id] = v
    app.saveData(data)
    this.setData({ currentGoalLabel: labels[idx] })
    this._refreshAll()
    wx.showToast({ title: '🎯 已保存', icon: 'none' })
  },

  setDifficulty(e) {
    const id = Number(e.currentTarget.dataset.id)
    const level = Number(e.currentTarget.dataset.level)
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (habit) {
      habit.difficulty = habit.difficulty === level ? 0 : level
      app.saveData(data)
      this.setData({
        detailDifficulty: habit.difficulty,
        detailHabit: Object.assign({}, habit)
      })
    }
  },

  onDetailNoteInput(e) {
    this.setData({ detailNote: e.detail.value || '' })
  },

  saveDetailNote() {
    const id = this.data.detailId
    if (!id) return
    const note = this.data.detailNote || ''
    const data = app.globalData.data
    if (!data.notes) data.notes = {}
    if (!data.notes[id]) data.notes[id] = {}
    const t = time.todayStr()
    data.notes[id][t] = note
    app.saveData(data)
    const history = []
    if (data.notes && data.notes[id]) {
      Object.keys(data.notes[id])
        .filter(function(d) { return d !== t })
        .sort()
        .reverse()
        .slice(0, 5)
        .forEach(function(d) {
          history.push({ date: d, note: data.notes[id][d] })
        })
    }
    this.setData({ detailHistory: history })
    wx.showToast({ title: '📝 已保存', icon: 'none' })
  },

  openDashboard() {
    this._updateRanked()
    this._updateAchievements()
    this.setData({ showDashboard: true })
  },

  closeDashboardOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showDashboard: false })
  },

  closeDashboard() { this.setData({ showDashboard: false }) },

  _updateRanked() {
    const data = app.globalData.data
    if (!data) return
    const ranked = (data.habits || []).map(function(h) {
      return { name: h.name, count: time.countCheckIns(h.id, data.records || {}) }
    }).sort(function(a, b) { return b.count - a.count })
    const maxCount = ranked.length ? Math.max(1, ranked[0].count) : 1
    const withPct = ranked.map(function(r) {
      var pct = Math.round(r.count / maxCount * 100)
      return Object.assign({}, r, { pct: pct, barStyle: 'width:' + pct + '%' })
    })
    this.setData({ rankedHabits: withPct })
  },

  openCalendar() {
    this.setData({ calOffset: 0 })
    this._updateCalendar()
    this.setData({ showCalendar: true })
  },

  closeCalendarOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showCalendar: false })
  },

  closeCalendar() { this.setData({ showCalendar: false }) },

  _updateCalendar() {
    const data = app.globalData.data
    if (!data) return
    const n = new Date()
    const y = n.getFullYear()
    const m = n.getMonth() + this.data.calOffset
    const fd = new Date(y, m, 1)
    const ld = new Date(y, m + 1, 0)
    const dim = ld.getDate()
    let sd = fd.getDay() - 1
    if (sd < 0) sd = 6
    const today = time.todayStr()
    const cells = []
    for (let i = 0; i < sd; i++) {
      cells.push({ day: '', level: 0, isToday: false, count: 0, date: '' })
    }
    let totalDays = 0, doneDays = 0
    for (let d = 1; d <= dim; d++) {
      const dt = new Date(y, m, d)
      const ds = time.dateStr(dt)
      const dr = (data.records && data.records[ds]) || {}
      const dn = dr ? Object.keys(dr).length : 0
      const active = data.habits.length
      const level = active > 0 ? Math.min(Math.round(dn / Math.max(active, 1) * 4), 4) : 0
      const isToday = ds === today
      if (active > 0) { totalDays++; if (dn > 0) doneDays++ }
      cells.push({ day: d, level: level, isToday: isToday, count: dn, date: ds })
    }
    const calTitle = y + '年' + (m + 1) + '月'
    const calSummary = '本月 ' + totalDays + ' 天有记录，' + doneDays + ' 天完成（' + (totalDays > 0 ? Math.round(doneDays / totalDays * 100) : 0) + '%）'
    this.setData({ calendarCells: cells, calendarTitle: calTitle, calendarSummary: calSummary })
  },

  prevMonth() { this.data.calOffset--; this._updateCalendar() },
  nextMonth() { this.data.calOffset++; this._updateCalendar() },

  showDateTip(e) {
    const date = e.currentTarget.dataset.date || ''
    if (!date) return
    const data = app.globalData.data
    const dr = (data.records && data.records[date]) || {}
    const names = (data.habits || []).filter(function(h) { return dr[h.id] }).map(function(h) { return h.name })
    if (names.length === 0) {
      wx.showToast({ title: '📭 ' + date + ' 无打卡', icon: 'none' })
    } else {
      wx.showToast({ title: '✅ ' + date + '：' + names.join('、'), icon: 'none', duration: 3000 })
    }
  },

  openReport() {
    this.setData({ reportIsWeek: true })
    this._updateReport()
    this.setData({ showReport: true })
  },

  closeReportOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showReport: false })
  },

  closeReport() { this.setData({ showReport: false }) },

  toggleReportMode() {
    this.setData({ reportIsWeek: !this.data.reportIsWeek })
    this._updateReport()
  },

  _updateReport() {
    const data = app.globalData.data
    if (!data) return
    const active = (data.habits || [])
    if (active.length === 0) { this.setData({ reportData: null }); return }
    const n = new Date()
    let start, end, totalDaysCount
    if (this.data.reportIsWeek) {
      start = time.getMonday(n)
      end = time.addDays(start, 6)
      totalDaysCount = 7
    } else {
      start = new Date(n.getFullYear(), n.getMonth(), 1)
      end = new Date(n.getFullYear(), n.getMonth() + 1, 0)
      totalDaysCount = end.getDate()
    }
    const days = []
    let totalDone = 0, totalAll = 0, fullDays = 0, zeroDays = 0
    const habitCounts = {}
    active.forEach(function(h) { habitCounts[h.id] = { name: h.name, done: 0 } })
    let cur = new Date(start)
    while (cur <= end) {
      const ds = time.dateStr(cur)
      const dr = (data.records && data.records[ds]) || {}
      const dayDone = active.filter(function(h) { return dr[h.id] }).length
      days.push({ date: ds, done: dayDone, total: active.length })
      totalAll += active.length
      totalDone += dayDone
      if (dayDone >= active.length) fullDays++
      if (dayDone === 0) zeroDays++
      active.forEach(function(h) { if (dr[h.id]) habitCounts[h.id].done++ })
      cur.setDate(cur.getDate() + 1)
    }
    const rate = totalAll > 0 ? Math.round(totalDone / totalAll * 100) : 0
    const bestDay = days.reduce(function(best, d) { return d.done > (best ? best.done : -1) ? d : best }, null)
    const habitList = Object.values(habitCounts).map(function(h) {
      return Object.assign({}, h, {
        rate: totalDaysCount > 0 ? Math.round(h.done / totalDaysCount * 100) : 0
      })
    })
    this.setData({
      reportData: {
        done: totalDone, total: totalAll, rate: rate, fullDays: fullDays, zeroDays: zeroDays, totalDays: totalDaysCount,
        habits: habitList,
        bestDay: (bestDay && bestDay.done > 0) ? { date: time.formatDate(new Date(bestDay.date)), done: bestDay.done, total: bestDay.total } : null
      }
    })
  },

  openCatchup() {
    const data = app.globalData.data
    const catchupHabits = (data.habits || []).map(function(h) { return { id: h.id, name: h.name } })
    const catchupDays = []
    for (let i = 13; i >= 0; i--) {
      const dt = time.addDays(new Date(), -i)
      const ds = time.dateStr(dt)
      catchupDays.push({
        date: ds,
        label: time.formatShort(dt),
        checked: false,
        status: '',
      })
    }
    this.setData({
      showCatchup: true,
      catchupHabits: catchupHabits,
      catchupDays: catchupDays,
      catchupSelectedName: '',
      _catchupId: null,
    })
  },

  closeCatchupOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showCatchup: false })
  },

  closeCatchup() { this.setData({ showCatchup: false }) },

  onCatchupHabitChange(e) {
    const idx = e.detail.value
    const habit = this.data.catchupHabits[idx]
    if (!habit) return
    const data = app.globalData.data
    const id = habit.id
    const catchupDays = this.data.catchupDays.map(function(d) {
      const checked = !!(data.records && data.records[d.date] && data.records[d.date][id])
      const status = checked ? '已打卡' : (d.date < time.todayStr() ? '未打卡' : '今天')
      return Object.assign({}, d, { checked: checked, status: status })
    })
    this.setData({
      catchupSelectedName: habit.name,
      _catchupId: id,
      catchupDays: catchupDays,
    })
  },

  doCatchup(e) {
    const date = e.currentTarget.dataset.date || ''
    if (!date || !this.data._catchupId) return
    const data = app.globalData.data
    if (!data.records) data.records = {}
    if (!data.records[date]) data.records[date] = {}
    data.records[date][this.data._catchupId] = true
    app.saveData(data)
    const id = this.data._catchupId
    const catchupDays = this.data.catchupDays.map(function(d) {
      const checked = !!(data.records && data.records[d.date] && data.records[d.date][id])
      const status = checked ? '已打卡' : (d.date < time.todayStr() ? '未打卡' : '今天')
      return Object.assign({}, d, { checked: checked, status: status })
    })
    this.setData({ catchupDays: catchupDays })
    this._refreshAll()
    wx.showToast({ title: '✅ 已补打', icon: 'none' })
  },

  openPomodoro() {
    this._updatePomoDisplay()
    this.setData({ showPomodoro: true })
  },

  closePomodoroOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showPomodoro: false })
  },

  closePomodoro() {
    if (this._pomoTimer) { clearInterval(this._pomoTimer); this._pomoTimer = null }
    this.setData({ showPomodoro: false, pomoRunning: false })
  },

  setPomoPreset(e) {
    const min = Number(e.currentTarget.dataset.min) || 25
    const sec = min * 60
    this.setData({
      pomoFocusLen: sec,
      pomoSeconds: sec,
      pomoPhase: 'focus',
      pomoRunning: false,
    })
    this._updatePomoDisplay()
    if (this._pomoTimer) { clearInterval(this._pomoTimer); this._pomoTimer = null }
  },

  onCustomPomoInput(e) {
    this.setData({ customPomoMin: e.detail.value || '' })
  },

  setCustomPomo() {
    const min = parseInt(this.data.customPomoMin) || 25
    const sec = Math.max(1, Math.min(120, min)) * 60
    this.setData({
      pomoFocusLen: sec,
      pomoSeconds: sec,
      pomoPhase: 'focus',
      pomoRunning: false,
    })
    this._updatePomoDisplay()
    if (this._pomoTimer) { clearInterval(this._pomoTimer); this._pomoTimer = null }
    wx.showToast({ title: '✅ ' + min + '分钟', icon: 'none' })
  },

  togglePomo() {
    if (this.data.pomoRunning) {
      clearInterval(this._pomoTimer)
      this._pomoTimer = null
      this.setData({ pomoRunning: false })
    } else {
      this.setData({ pomoRunning: true })
      this._startPomo()
    }
  },

  _startPomo() {
    if (this._pomoTimer) clearInterval(this._pomoTimer)
    this._pomoTimer = setInterval(function() {
      const sec = this.data.pomoSeconds - 1
      if (sec <= 0) {
        clearInterval(this._pomoTimer)
        this._pomoTimer = null
        this._onPomoComplete()
        return
      }
      this.setData({ pomoSeconds: sec })
      this._updatePomoDisplay()
    }.bind(this), 1000)
  },

  _onPomoComplete() {
    const data = app.globalData.data
    if (this.data.pomoPhase === 'focus') {
      if (!data.pomo) data.pomo = { today: 0, date: '', total: 0, log: [] }
      if (data.pomo.date !== time.todayStr()) {
        data.pomo.today = 0
        data.pomo.date = time.todayStr()
      }
      data.pomo.today = (data.pomo.today || 0) + 1
      data.pomo.total = (data.pomo.total || 0) + 1
      data.pomo.log = data.pomo.log || []
      data.pomo.log.push({
        time: time.formatDate(new Date()),
        dur: Math.round(this.data.pomoFocusLen / 60)
      })
      if (data.pomo.log.length > 20) data.pomo.log = data.pomo.log.slice(-20)
      app.saveData(data)
      if (data.pVib)
this.setData({
        pomoPhase: 'break',
        pomoSeconds: 300,
        pomoRunning: false,
        pomoToday: data.pomo.today,
        pomoTotal: data.pomo.total,
        pomoLogs: data.pomo.log,
      })
      this._updatePomoDisplay()
      wx.showModal({
        title: '🍅 专注完成',
        content: '休息5分钟吧！',
        showCancel: true,
        confirmText: '开始休息',
        cancelText: '跳过',
        success: function(res) {
          if (res.confirm) {
            this.setData({ pomoRunning: true })
            this._startPomo()
          }
        }.bind(this)
      })
    } else {
      this.setData({
        pomoPhase: 'focus',
        pomoSeconds: this.data.pomoFocusLen,
        pomoRunning: false,
      })
      this._updatePomoDisplay()
    }
  },

  skipBreak() {
    if (this.data.pomoPhase === 'break') {
      clearInterval(this._pomoTimer)
      this._pomoTimer = null
      this.setData({
        pomoPhase: 'focus',
        pomoSeconds: this.data.pomoFocusLen,
        pomoRunning: false,
      })
      this._updatePomoDisplay()
    }
  },

  resetPomo() {
    if (this._pomoTimer) { clearInterval(this._pomoTimer); this._pomoTimer = null }
    this.setData({
      pomoSeconds: this.data.pomoFocusLen,
      pomoRunning: false,
      pomoPhase: 'focus',
    })
    this._updatePomoDisplay()
  },

  _updatePomoDisplay() {
    const sec = this.data.pomoSeconds
    const m = String(Math.floor(sec / 60)).padStart(2, '0')
    const s = String(sec % 60).padStart(2, '0')
    this.setData({
      pomoMinStr: [m[0], m[1]],
      pomoSecStr: [s[0], s[1]],
    })
  },

  closeConfirmOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showConfirm: false })
  },

  cancelConfirm() {
    this.setData({ showConfirm: false, _confirmAction: '', _confirmId: null })
  },

  
  closeAllDonePopup() {
    this.setData({ showAllDonePopup: false })
  },
  doConfirm() {
    const action = this.data._confirmAction
    this.setData({ showConfirm: false, _confirmAction: '', _confirmId: null })
    if (action === 'reset') {
      const empty = app.getEmptyData()
      app.globalData.data = empty
      app.saveData(empty)
      this._refreshAll()
      wx.showToast({ title: '已重置', icon: 'none' })
    } else if (action === 'deleteHabit') {
      this.doDeleteHabit()
    }
  },

  openCategoryManager() {
    this.setData({ showCategoryManager: true, newCatName: '' })
  },

  closeCategoryManagerOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showCategoryManager: false })
  },

  closeCategoryManager() { this.setData({ showCategoryManager: false }) },
  openCatPicker(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (!habit) return
    this.setData({
      showCatPicker: true,
      catPickerId: id,
      catPickerName: habit.name,
      catPickerCur: habit.category || '',
    })
  },

  closeCatPicker() {
    this.setData({ showCatPicker: false, catPickerId: null })
  },

  closeCatPickerOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.closeCatPicker()
  },

  pickCategory(e) {
    const cat = e.currentTarget.dataset.cat || ''
    const id = this.data.catPickerId
    if (!id) return
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (!habit) return
    habit.category = cat
    app.saveData(data)
    this.setData({ catPickerCur: cat })
    this._refreshAll()
    wx.showToast({ title: cat ? '已设为「' + cat + '」' : '已设为无分类', icon: 'none' })
  },

  openCategoryManagerFromPicker() {
    this.closeCatPicker()
    setTimeout(function() { this.setData({ showCategoryManager: true }) }.bind(this), 300)
  },



  onNewCatInput(e) {
    this.setData({ newCatName: e.detail.value || '' })
  },

  addCategory() {
    const name = (this.data.newCatName || '').trim()
    if (!name) {
      wx.showToast({ title: '输入分类名称', icon: 'none' })
      return
    }
    const data = app.globalData.data
    if (!data.cats) data.cats = []
    if (data.cats.indexOf(name) !== -1) {
      wx.showToast({ title: '分类已存在', icon: 'none' })
      return
    }
    data.cats.push(name)
    app.saveData(data)
    this.setData({ cats: data.cats, newCatName: '' })
    this._refreshAll()
    wx.showToast({ title: '✅ 已添加', icon: 'none' })
  },

  deleteCategory(e) {
    const cat = e.currentTarget.dataset.cat || ''
    if (!cat) return
    const data = app.globalData.data
    const used = (data.habits || []).some(function(h) { return h.category === cat })
    let content = '确定删除分类「' + cat + '」？'
    if (used) content += '\n（已有习惯使用了此分类，删除后这些习惯的分类将变为空）'
    wx.showModal({
      title: '删除分类',
      content: content,
      success: function(res) {
        if (res.confirm) {
          if (used) {
            (data.habits || []).forEach(function(h) {
              if (h.category === cat) h.category = ''
            })
          }
          data.cats = data.cats.filter(function(c) { return c !== cat })
          app.saveData(data)
          this.setData({ cats: data.cats })
          this._refreshAll()
          wx.showToast({ title: '🗑 已删除', icon: 'none' })
        }
      }.bind(this)
    })
  },

  // ===== 成就弹窗 =====
  closeAllDonePopup() {
    this.setData({ showAllDonePopup: false })
  },

  showDayTip(e) {
    const idx = e.currentTarget.dataset.idx
    if (idx === undefined || idx === null) return
    const dot = this.data.weekDots[idx]
    if (!dot || !dot.date) return
    this.showDateTip({ currentTarget: { dataset: { date: dot.date } } })
  },
})
