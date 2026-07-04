#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整重写 habit 小程序三个核心文件：
  index.js  — 所有拼写错误修正
  index.wxml — 移除导入导出、支持暗色模式、修复周圆点
  index.wxss — 暗色主题、顶栏避让胶囊、番茄钟布局修复、精致动画
"""

import os

ROOT = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit"

# ======================== index.js ========================
INDEX_JS = r"""/**
 * 习惯打卡 - 主页面逻辑（完整修正版 v3）
 * 修复：所有 Unicode 同形字拼写错误
 * 新增：暗色模式完整支持
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
  },

  onUnload() {
    clearInterval(this._clockTimer)
    clearInterval(this._pomoTimer)
  },

  onShow() {
    this._refreshAll()
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

  _refreshAll() {
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
    this._updateFilteredHabits()
    this._updateStats()
    this._updateSuggestions()
    this._updateAchievements()
  },

  _updateProgress() {
    const data = app.globalData.data
    const t = time.todayStr()
    const dr = (data.records && data.records[t]) || {}
    const active = (data.habits || []).filter(function(h) { return !h.archived })
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
      const dn = Object.keys(dr).length
      const ac = data.habits.filter(function(h) { return !h.archived }).length
      let cls = 'dot'
      let label = ''
      if (ac > 0 && dn >= ac) {
        cls += ' filled'
        label = '✓'
      } else if (dn > 0) {
        cls += ' partial'
        label = String(dn)
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

  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    let list = [].concat(data.habits)
    if (this.data.showArchived) {
      list = list.filter(function(h) { return h.archived })
    } else {
      list = list.filter(function(h) { return !h.archived })
    }
    if (this.data.filterCat) {
      list = list.filter(function(h) { return h.category === this.data.filterCat }.bind(this))
    }
    if (this.data.searchText && this.data.searchText.trim()) {
      const q = this.data.searchText.trim().toLowerCase()
      list = list.filter(function(h) { return h.name.toLowerCase().indexOf(q) !== -1 })
    }
    const records = data.records || {}
    const goals = data.goals || {}
    const mon = time.getMonday(new Date())
    const today = time.todayStr()
    const todayRecord = (records[today] || {})
    list = list.map(function(h) {
      const checked = !!(todayRecord[h.id])
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
    this._refreshAll()
    if (!wasChecked) {
      const habit = (data.habits || []).find(function(h) { return h.id === id })
      if (habit) wx.showToast({ title: '✅ ' + habit.name, icon: 'none' })
      const dr = (data.records[t] || {})
      const active = (data.habits || []).filter(function(h) { return !h.archived })
      if (active.length > 0 && active.every(function(h) { return dr[h.id] })) {
        setTimeout(function() {
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
      setTimeout(function() {
        wx.showModal({
          title: '🎉 成就解锁',
          content: unlocks.join('\\n'),
          showCancel: false,
          confirmText: '太棒了！'
        })
      }, 800)
    }
  },

  toggleArchive(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (!habit) return
    this.setData({ _confirmAction: 'archive', _confirmId: id })
    this.setData({
      showConfirm: true,
      confirmText: '确定归档「' + habit.name + '」？\\n归档后数据保留，可随时恢复。'
    })
  },

  _doArchive() {
    const data = app.globalData.data
    const id = this.data._confirmId
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (habit) {
      habit.archived = true
      app.saveData(data)
      this._refreshAll()
      wx.showToast({ title: '📦 已归档', icon: 'none' })
    }
  },

  restoreHabit(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(function(h) { return h.id === id })
    if (habit) {
      habit.archived = false
      app.saveData(data)
      this._refreshAll()
      wx.showToast({ title: '↩ 已恢复', icon: 'none' })
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
    this.setData({ filterCat: cat, showArchived: false })
    this._updateFilteredHabits()
    this._updateSuggestions()
  },

  toggleArchived() {
    const arch = !this.data.showArchived
    this.setData({ showArchived: arch, filterCat: '' })
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
      archived: false,
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
      archived: false,
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
      confirmText: '⚠️ 确认重置？\\n将永久删除全部数据，此操作不可恢复！',
      _confirmAction: 'reset'
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
    const chartLabels = [0,2,4,6].map(function(i) {
      const dt = time.addDays(new Date(), -(6-i))
      return time.formatShort(dt)
    })
    const goalVal = ((data.goals || {})[id] && (data.goals || {})[id].weekly) || 0
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
    const v = vals[e.detail.value] || 0
    const id = this.data.detailId
    if (!id) return
    const data = app.globalData.data
    if (!data.goals) data.goals = {}
    if (!data.goals[id]) data.goals[id] = {}
    data.goals[id].weekly = v
    app.saveData(data)
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
    const active = (data.habits || []).filter(function(h) { return !h.archived })
    const ranked = active.map(function(h) {
      return { name: h.name, count: time.countCheckIns(h.id, data.records || {}) }
    }).sort(function(a, b) { return b.count - a.count })
    const maxCount = ranked.length ? Math.max(1, ranked[0].count) : 1
    const withPct = ranked.map(function(r) {
      return Object.assign({}, r, { pct: Math.round(r.count / maxCount * 100) })
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
      const ac = (data.habits || []).filter(function(h) { return !h.archived }).length
      const level = ac > 0 ? Math.min(Math.round(dn / Math.max(ac, 1) * 4), 4) : 0
      const isToday = ds === today
      if (ac > 0) { totalDays++; if (dn > 0) doneDays++ }
      cells.push({ day: d, level: level, isToday: isToday, count: dn, date: ds })
    }
    const calTitle = y + '年' + (m + 1) + '月'
    const calSummary = '本月 ' + totalDays + ' 天有记录，' + doneDays + ' 天完成（' + (totalDays > 0 ? Math.round(doneDays / totalDays * 100) : 0) + '%）'
    this.setData({ calendarCells: cells, calendarTitle: calTitle, calendarSummary: calSummary })
  },

  prevMonth() { this.data.calOffset--; this._updateCalendar() },
  nextMonth() { this.data.calOffset++; this._updateCalendar() },

  showDayTip(e) {
    const idx = e.currentTarget.dataset.idx
    if (idx === undefined || idx === null) return
    const dot = this.data.weekDots[idx]
    if (!dot || !dot.date) return
    this._showDateTip(dot.date)
  },

  _showDateTip(date) {
    const data = app.globalData.data
    const dr = (data.records && data.records[date]) || {}
    const names = (data.habits || []).filter(function(h) { return !h.archived && dr[h.id] }).map(function(h) { return h.name })
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
    const active = (data.habits || []).filter(function(h) { return !h.archived })
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
    const active = (data.habits || []).filter(function(h) { return !h.archived })
    const catchupHabits = active.map(function(h) { return { id: h.id, name: h.name } })
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
      if (data.pVib) wx.vibrateShort({ type: 'medium' })
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

  doConfirm() {
    const action = this.data._confirmAction
    this.setData({ showConfirm: false, _confirmAction: '', _confirmId: null })
    if (action === 'archive') { this._doArchive() }
    else if (action === 'reset') {
      const empty = app.getEmptyData()
      app.globalData.data = empty
      app.saveData(empty)
      this._refreshAll()
      wx.showToast({ title: '已重置', icon: 'none' })
    } else if (action === 'deleteCat') {
      this._doDeleteCategory()
    }
  },

  openCategoryManager() {
    this.setData({ showCategoryManager: true, newCatName: '' })
  },

  closeCategoryManagerOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showCategoryManager: false })
  },

  closeCategoryManager() { this.setData({ showCategoryManager: false }) },

  onNewCatInput(e) {
    this.setData({ newCatName: e.detail.value || '' })
  },

  addCategory() {
    const name = (this.data.newCatName || '').trim()
    if (!name) { wx.showToast({ title: '输入分类名称', icon: 'none' }); return }
    const data = app.globalData.data
    if (!data.cats) data.cats = []
    if (data.cats.indexOf(name) !== -1) {
      wx.showToast({ title: '分类已存在', icon: 'none' }); return
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
    this.setData({
      showConfirm: true,
      confirmText: '确定删除分类「' + cat + '」？' + (used ? '\\n已有习惯使用了此分类，删除后这些习惯的分类将变为空。' : ''),
      _confirmAction: 'deleteCat',
      _confirmCat: cat
    })
  },

  _doDeleteCategory() {
    const cat = this.data._confirmCat
    if (!cat) return
    const data = app.globalData.data
    const used = (data.habits || []).some(function(h) { return h.category === cat })
    if (used) {
      (data.habits || []).forEach(function(h) {
        if (h.category === cat) h.category = ''
      })
    }
    data.cats = data.cats.filter(function(c) { return c !== cat })
    app.saveData(data)
    this.setData({ cats: data.cats, _confirmCat: '' })
    this._refreshAll()
    wx.showToast({ title: '🗑 已删除', icon: 'none' })
  },
})
"""

# ======================== index.wxml ========================
INDEX_WXML = r"""<wxs module="u" src="./index.wxs"></wxs>

<!-- 习惯打卡 - 主页面 -->
<scroll-view
  class="page {{stg.theme==='dark'?'dark':''}}"
  scroll-y
  enhanced
  show-scrollbar="{{false}}"
  style="height:100vh;">

  <!-- 状态栏占位 -->
  <view style="height:{{statusBarHeight}}px"></view>

  <!-- ===== 顶栏 ===== -->
  <view class="topbar">
    <view class="title" bindtap="openDashboard">习惯</view>
    <view class="topbar-btns">
      <view class="iconbtn" bindtap="openPomodoro">🍅</view>
      <view class="iconbtn" bindtap="openDashboard">📊</view>
      <view class="iconbtn" bindtap="openSettings">⚙</view>
    </view>
  </view>
  <view class="greeting">{{greeting}}</view>
  <view class="subtitle">已连续 <text class="hl">{{apDays}}</text> 天</view>


  <!-- ===== 进度卡片 ===== -->
  <view class="head">
    <view class="head-row">
      <text class="head-time">{{clockStr}}</text>
      <text class="head-icon">🔔</text>
    </view>
    <view class="head-row" style="margin-bottom:2px">
      <text class="head-quote">{{dailyQuote}}</text>
    </view>
    <view class="head-progress">
      <text class="head-title">{{progressTitle}}</text>
      <text class="head-count">{{doneCount}}/{{totalCount}}</text>
    </view>
    <view class="progress-bar">
      <view class="progress-fill" style="width:{{progressPercent}}%"></view>
    </view>
    <text class="head-sub">{{progressSub}}</text>
  </view>


  <!-- ===== 搜索 ===== -->
  <view class="search-box">
    <text class="search-icon">🔍</text>
    <input class="search-input"
           placeholder="搜索习惯..."
           maxlength="20"
           bindconfirm="onSearchConfirm"
           confirm-type="search" />
    <text class="search-clear {{searchText?'show':''}}"
          bindtap="clearSearch">✕</text>
  </view>


  <!-- ===== 本周圆点 ===== -->
  <view class="week-section">
    <view class="week-header">
      <text class="section-label">本周</text>
      <view class="week-links">
        <text class="link" bindtap="openCatchup">补打卡</text>
        <text class="link" bindtap="openReport">周报</text>
        <text class="link" bindtap="openCalendar">日历</text>
      </view>
    </view>
    <view class="week-dots">
      <view wx:for="{{weekDots}}" wx:key="index"
            class="dot-col" bindtap="showDayTip" data-idx="{{index}}">
        <text class="dot-name">{{item.name}}</text>
        <view class="dot {{item.cls}}">
          <text wx:if="{{item.label}}">{{item.label}}</text>
        </view>
      </view>
    </view>
  </view>


  <!-- ===== 分类筛选 ===== -->
  <view class="cat-bar">
    <scroll-view class="cat-scroll" scroll-x enhanced show-scrollbar="{{false}}">
      <view class="cat-chip {{!filterCat&&!showArchived?'active':''}}"
            bindtap="setFilter" data-cat="">全部</view>
      <view wx:for="{{cats}}" wx:key="*this"
            class="cat-chip {{(filterCat===item&&!showArchived)?'active':''}}"
            bindtap="setFilter" data-cat="{{item}}">{{item}}</view>
      <view class="cat-chip arch {{showArchived?'active':''}}"
            bindtap="toggleArchived">📦</view>
    </scroll-view>
    <view class="cat-add" bindtap="openCategoryManager">+分类</view>
  </view>


  <!-- ===== 习惯列表 ===== -->
  <view class="habit-list">
    <view wx:if="{{filteredHabits.length===0}}" class="empty">
      <text wx:if="{{searchText}}">无「{{searchText}}」结果</text>
      <text wx:elif="{{showArchived}}">暂无归档习惯</text>
      <text wx:else>尚无习惯，从下方添加</text>
    </view>

    <view wx:for="{{filteredHabits}}" wx:key="id"
          class="habit-item {{u.getCatClass(item.category)}} {{item.archived?'archived':''}}">
      <!-- 勾选 -->
      <view class="check {{item._checked?'checked':''}}"
            bindtap="toggleCheckin" data-id="{{item.id}}"></view>

      <!-- 内容 -->
      <view class="habit-body">
        <!-- 编辑态 -->
        <input wx:if="{{editingId===item.id}}"
               class="edit-input"
               value="{{editingName}}"
               bindinput="onEditInput"
               bindblur="saveRename"
               bindconfirm="saveRename"
               focus
               maxlength="30" />
        <!-- 正常态 -->
        <text wx:else class="habit-name" bindtap="startEdit"
              data-id="{{item.id}}" data-name="{{item.name}}">{{item.name}}</text>

        <view class="habit-tags">
          <text wx:if="{{item.category&&!filterCat}}" class="tag-cat">{{item.category}}</text>
          <text wx:if="{{item._weeklyGoal}}" class="tag-goal {{item._goalMissed?'missed':''}}">🎯周{{item._weeklyGoal}}{{item._goalDone?'✓':''}}</text>
          <text wx:if="{{item.difficulty>0}}" class="tag-diff">
            <text wx:for="{{item.difficulty}}" wx:for-item="s" wx:key="*this">⭐</text>
          </text>
        </view>

        <text class="streak">
          <text class="streak-num {{item._checked?'done':'missed'}}">{{item._streak}}</text>
          <text class="streak-fire {{item._checked?'done':'missed'}}">🔥</text>
        </text>
      </view>

      <!-- 操作 -->
      <view class="habit-info" bindtap="openDetail" data-id="{{item.id}}">📊</view>
      <view wx:if="{{!item.archived}}" class="habit-del" bindtap="toggleArchive" data-id="{{item.id}}">⋯</view>
      <view wx:else class="habit-del" bindtap="restoreHabit" data-id="{{item.id}}">↩</view>
    </view>
  </view>


  <!-- ===== 统计卡片 ===== -->
  <view class="stats-row">
    <view class="stat-card"><text class="stat-num">{{totalHabits}}</text><text class="stat-label">总习惯</text></view>
    <view class="stat-card"><text class="stat-num">{{doneCount}}</text><text class="stat-label">今日</text></view>
    <view class="stat-card"><text class="stat-num">{{weekTotal}}</text><text class="stat-label">本周</text></view>
    <view class="stat-card"><text class="stat-num">{{progressPercent}}%</text><text class="stat-label">完成率</text></view>
  </view>


  <!-- ===== 建议 ===== -->
  <view class="sug-row" wx:if="{{suggestions.length>0}}">
    <view wx:for="{{suggestions}}" wx:key="*this"
          class="sug-chip" bindtap="addSuggestion" data-name="{{item}}">+ {{item}}</view>
  </view>


  <!-- ===== 添加习惯 ===== -->
  <view class="add-row">
    <input class="add-input"
           placeholder="添加新习惯"
           maxlength="30"
           bindinput="onNewHabitInput"
           bindconfirm="doAddHabit"
           confirm-type="done" />
    <button class="add-btn" bindtap="doAddHabit">记下</button>
  </view>

</scroll-view>




<!-- ============================================================= -->
<!-- 弹窗区域 -->
<!-- ============================================================= -->


<!-- ===== 设置弹窗 ===== -->
<view class="overlay {{showSettings?'show':''}}" bindtap="closeSettingsOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeSettings">✕</view>
    <view class="modal-title">设置</view>

    <!-- 外观 -->
    <view class="sec">
      <view class="sec-title">外观</view>
      <view class="row" bindtap="toggleTheme">
        <text>深色模式</text>
        <view class="toggle {{stg.theme==='dark'?'on':''}}"><view class="toggle-knob"></view></view>
      </view>
      <view class="row" style="align-items:flex-start">
        <text style="margin-top:4px">主题色</text>
        <view style="display:flex;gap:6px;flex-wrap:wrap">
          <view wx:for="{{themeColors}}" wx:key="*this"
                class="color-dot"
                style="background:{{item}};{{stg.accent===item?'border:2px solid #333':'border:2px solid transparent'}}"
                bindtap="setAccent" data-color="{{item}}"></view>
        </view>
      </view>
    </view>

    <!-- 提醒 -->
    <view class="sec">
      <view class="sec-title">提醒</view>
      <view class="row" bindtap="toggleReminder">
        <text>每日提醒</text>
        <view class="toggle {{stg.remind?'on':''}}"><view class="toggle-knob"></view></view>
      </view>
      <picker wx:if="{{stg.remind}}" mode="time" value="{{stg.remindT}}" bindchange="onRemindTimeChange">
        <view class="picker-val">{{stg.remindT}}</view>
      </picker>
    </view>

    <!-- 音效 -->
    <view class="sec">
      <view class="sec-title">音效</view>
      <view class="row" bindtap="toggleSound">
        <text>打卡音效</text>
        <view class="toggle {{sndEnabled?'on':''}}"><view class="toggle-knob"></view></view>
      </view>
      <view class="row" bindtap="toggleVibration">
        <text>番茄钟振动</text>
        <view class="toggle {{pVibEnabled?'on':''}}"><view class="toggle-knob"></view></view>
      </view>
    </view>

    <!-- 分类管理 -->
    <view class="sec">
      <view class="sec-title">分类管理</view>
      <button class="btn-primary full" bindtap="openCategoryManagerFromSettings">管理分类</button>
    </view>

    <!-- 数据 -->
    <view class="sec">
      <view class="sec-title">数据</view>
      <button class="btn-danger full" style="margin-top:8px" bindtap="resetAll">🗑 重置全部数据</button>
    </view>
  </view>
</view>




<!-- ===== 详情弹窗 ===== -->
<view class="overlay {{showDetail?'show':''}}" bindtap="closeDetailOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeDetail">✕</view>
    <view class="modal-title">📊 {{detailHabit.name}}</view>
    <text wx:if="{{detailHabit.category}}" class="detail-cat">分类：{{detailHabit.category}}</text>

    <!-- 统计数字 -->
    <view class="detail-stats">
      <view class="detail-stat"><text class="detail-num">{{detailStreak}}</text><text class="detail-lbl">当前连续</text></view>
      <view class="detail-stat"><text class="detail-num">{{detailBestStreak}}</text><text class="detail-lbl">最佳连续</text></view>
      <view class="detail-stat"><text class="detail-num">{{detailTotal}}</text><text class="detail-lbl">总打卡</text></view>
      <view class="detail-stat"><text class="detail-num">{{detailDifficulty}}⭐</text><text class="detail-lbl">难度</text></view>
    </view>

    <!-- 近7天图表 -->
    <view class="sec">
      <view class="sec-title">近7天</view>
      <view class="chart">
        <view wx:for="{{detailChart}}" wx:key="index"
              class="chart-bar {{index===6?'today':''}}"
              style="height:{{Math.max(item,8)}}%"></view>
      </view>
      <view class="chart-labels">
        <text wx:for="{{detailChartLabels}}" wx:key="*this">{{item}}</text>
      </view>
    </view>

    <!-- 周目标 -->
    <view class="sec">
      <view class="sec-title">周目标</view>
      <picker range="{{goalOptions}}" bindchange="onGoalChange">
        <view class="picker-val">{{currentGoalLabel}}</view>
      </picker>
    </view>

    <!-- 难度 -->
    <view class="sec">
      <view class="sec-title">难度</view>
      <view style="display:flex;gap:8px">
        <text wx:for="{{[1,2,3]}}" wx:key="*this"
              style="font-size:24px;opacity:{{item<=(detailHabit.difficulty||0)?1:0.25}}"
              bindtap="setDifficulty" data-id="{{detailId}}" data-level="{{item}}">⭐</text>
      </view>
    </view>

    <!-- 备注 -->
    <view class="sec">
      <view class="sec-title">备注</view>
      <textarea class="note-area"
                value="{{detailNote}}"
                placeholder="记录今天的感受..."
                maxlength="200"
                bindinput="onDetailNoteInput"></textarea>
      <button class="btn-primary" style="margin-top:8px" bindtap="saveDetailNote">保存备注</button>
    </view>

    <!-- 历史备注 -->
    <view class="sec" wx:if="{{detailHistory.length>0}}">
      <view class="sec-title">历史备注</view>
      <view wx:for="{{detailHistory}}" wx:key="date" class="history-item">
        <text class="history-date">{{item.date}}</text>
        <text class="history-note">{{item.note}}</text>
      </view>
    </view>
  </view>
</view>




<!-- ===== 看板弹窗 ===== -->
<view class="overlay {{showDashboard?'show':''}}" bindtap="closeDashboardOverlay">
  <view class="modal modal-lg" catchtap="stopProp">
    <view class="modal-close" bindtap="closeDashboard">✕</view>
    <view class="modal-title">看板</view>

    <!-- 概览 -->
    <view class="sec">
      <view class="sec-title">概览</view>
      <view class="dash-grid">
        <view class="dash-card"><text class="dash-num">{{totalHabits}}</text><text class="dash-lbl">习惯</text></view>
        <view class="dash-card"><text class="dash-num">{{totalCheckInsAll}}</text><text class="dash-lbl">总打卡</text></view>
        <view class="dash-card"><text class="dash-num">{{weekTotal}}</text><text class="dash-lbl">本周</text></view>
        <view class="dash-card"><text class="dash-num">{{progressPercent}}%</text><text class="dash-lbl">完成率</text></view>
      </view>
    </view>

    <!-- 排行 -->
    <view class="sec">
      <view class="sec-title">习惯排行</view>
      <view wx:if="{{rankedHabits.length===0}}" class="empty-sm">暂无数据</view>
      <view wx:for="{{rankedHabits}}" wx:key="name" class="rank-row">
        <text class="rank-idx">{{index+1}}</text>
        <text class="rank-name">{{item.name}}</text>
        <view class="rank-bar-wrap">
          <view class="rank-bar" style="width:{{item.pct}}%"></view>
        </view>
        <text class="rank-cnt">{{item.count}}次</text>
      </view>
    </view>

    <!-- 成就 -->
    <view class="sec">
      <view class="sec-title">成就（20项）</view>
      <view class="ach-grid">
        <view wx:for="{{achievements}}" wx:key="id"
              class="ach-card {{item.unlocked?'unlocked':'locked'}}">
          <text class="ach-icon">{{item.ic}}</text>
          <text class="ach-name">{{item.nm}}</text>
          <text class="ach-desc">{{item.desc}}</text>
        </view>
      </view>
    </view>
  </view>
</view>




<!-- ===== 日历弹窗 ===== -->
<view class="overlay {{showCalendar?'show':''}}" bindtap="closeCalendarOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeCalendar">✕</view>
    <view class="modal-title">打卡日历</view>

    <view class="cal-nav">
      <view class="cal-btn" bindtap="prevMonth">‹</view>
      <text class="cal-title">{{calendarTitle}}</text>
      <view class="cal-btn" bindtap="nextMonth">›</view>
    </view>

    <view class="cal-weekdays">
      <text wx:for="{{['一','二','三','四','五','六','日']}}" wx:key="*this">{{item}}</text>
    </view>

    <view class="cal-grid">
      <view wx:for="{{calendarCells}}" wx:key="index"
            class="cal-cell l{{item.level}} {{item.isToday?'today':''}}"
            bindtap="_showDateTip" data-date="{{item.date}}">
        <text>{{item.day}}</text>
        <text wx:if="{{item.count>0}}" class="cal-cnt">{{item.count}}</text>
      </view>
    </view>

    <view class="cal-legend">
      <text>少</text>
      <view class="cal-dot l0"></view>
      <view class="cal-dot l1"></view>
      <view class="cal-dot l2"></view>
      <view class="cal-dot l3"></view>
      <view class="cal-dot l4"></view>
      <text>多</text>
    </view>

    <text class="cal-summary">{{calendarSummary}}</text>
  </view>
</view>




<!-- ===== 周报弹窗 ===== -->
<view class="overlay {{showReport?'show':''}}" bindtap="closeReportOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeReport">✕</view>
    <view class="modal-title">{{reportIsWeek?'本周报告':'本月报告'}}</view>

    <view wx:if="{{reportData}}">
      <view class="report-card">
        <view class="report-row"><text>完成</text><text class="report-val">{{reportData.done}}/{{reportData.total}}（{{reportData.rate}}%）</text></view>
        <view class="report-row"><text>全勤</text><text class="report-val">{{reportData.fullDays}}天</text></view>
        <view class="report-row"><text>零打卡</text><text class="report-val">{{reportData.zeroDays}}天</text></view>
      </view>

      <view class="report-card">
        <view class="sec-title">各习惯</view>
        <view wx:for="{{reportData.habits}}" wx:key="name" class="report-row">
          <text>{{item.name}}</text>
          <text class="report-val">{{item.done}}/{{reportData.totalDays}}（{{item.rate}}%）</text>
        </view>
      </view>

      <view wx:if="{{reportData.bestDay}}" class="report-card">
        <view class="sec-title">最佳日</view>
        <view class="report-row">
          <text>{{reportData.bestDay.date}}</text>
          <text class="report-val">完成 {{reportData.bestDay.done}}/{{reportData.bestDay.total}}</text>
        </view>
      </view>

      <button class="btn-outline" style="margin-top:12px" bindtap="toggleReportMode">{{reportIsWeek?'月报':'周报'}}</button>
    </view>
  </view>
</view>




<!-- ===== 补打卡弹窗 ===== -->
<view class="overlay {{showCatchup?'show':''}}" bindtap="closeCatchupOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeCatchup">✕</view>
    <view class="modal-title">补打卡</view>
    <text class="modal-desc">选择习惯和日期</text>

    <picker range="{{catchupHabits}}" range-key="name" bindchange="onCatchupHabitChange">
      <view class="picker-val">{{catchupSelectedName||'选择习惯'}}</view>
    </picker>

    <scroll-view scroll-y style="max-height:300px;margin-top:10px">
      <view wx:for="{{catchupDays}}" wx:key="date"
            class="catchup-row">
        <text class="catchup-date">{{item.label}}</text>
        <text class="catchup-status">{{item.status}}</text>
        <button class="btn-sm {{item.checked?'done':''}}"
                disabled="{{item.checked}}"
                bindtap="doCatchup" data-date="{{item.date}}">
          {{item.checked?'✓':'补打'}}
        </button>
      </view>
    </scroll-view>
  </view>
</view>




<!-- ===== 番茄钟弹窗 ===== -->
<view class="overlay {{showPomodoro?'show':''}}" bindtap="closePomodoroOverlay">
  <view class="modal modal-pomo" catchtap="stopProp">
    <view class="modal-close" bindtap="closePomodoro">✕</view>
    <view class="modal-title">🍅 专注计时</view>

    <!-- 预设 -->
    <view class="pomo-presets">
      <view wx:for="{{pomoPresets}}" wx:key="*this"
            class="pomo-preset {{pomoFocusLen/60===item?'active':''}}"
            bindtap="setPomoPreset" data-min="{{item}}">{{item}}分</view>
    </view>

    <!-- 自定义输入 -->
    <view class="pomo-custom">
      <input class="pomo-custom-input"
             type="number"
             placeholder="分钟"
             value="{{customPomoMin}}"
             bindinput="onCustomPomoInput" />
      <button class="btn-primary sm" bindtap="setCustomPomo">设定</button>
    </view>

    <!-- 翻牌时钟 -->
    <view class="flip-clock">
      <view class="flip-unit">
        <view class="flip-card"><text>{{pomoMinStr[0]}}</text></view>
        <view class="flip-card"><text>{{pomoMinStr[1]}}</text></view>
        <text class="flip-lbl">分</text>
      </view>
      <text class="flip-colon">:</text>
      <view class="flip-unit">
        <view class="flip-card"><text>{{pomoSecStr[0]}}</text></view>
        <view class="flip-card"><text>{{pomoSecStr[1]}}</text></view>
        <text class="flip-lbl">秒</text>
      </view>
    </view>

    <!-- 阶段提示 -->
    <view class="pomo-phase {{pomoPhase==='focus'?'focus':'break'}}">
      {{pomoPhase==='focus'?'🎯 专注中':'☕ 休息中'}}
    </view>

    <!-- 控制按钮 -->
    <view class="pomo-controls">
      <button class="pomo-btn {{pomoRunning?'pause':'go'}}" bindtap="togglePomo">
        {{pomoRunning?'⏸ 暂停':'▶ 开始'}}
      </button>
      <button wx:if="{{pomoPhase==='break'&&!pomoRunning}}"
              class="pomo-btn skip" bindtap="skipBreak">⏭ 跳过</button>
      <button class="pomo-btn reset" bindtap="resetPomo">⟲ 重置</button>
    </view>

    <text class="pomo-info">今日番茄：{{pomoToday}} | 总番茄：{{pomoTotal}}</text>

    <view class="pomo-log" wx:if="{{pomoLogs.length>0}}">
      <view wx:for="{{pomoLogs}}" wx:key="time" class="pomo-log-item">
        🍅 {{item.time}} — {{item.dur}}分钟
      </view>
    </view>
  </view>
</view>




<!-- ===== 确认弹窗 ===== -->
<view class="overlay {{showConfirm?'show':''}}" bindtap="closeConfirmOverlay">
  <view class="modal modal-confirm" catchtap="stopProp">
    <view class="confirm-icon">
      <text wx:if="{{_confirmAction==='reset'}}">⚠️</text>
      <text wx:elif="{{_confirmAction==='archive'}}">📦</text>
      <text wx:elif="{{_confirmAction==='deleteCat'}}">🗑</text>
      <text wx:else>❓</text>
    </view>
    <text class="confirm-text">{{confirmText}}</text>
    <view class="confirm-btns">
      <button class="confirm-btn cancel" bindtap="cancelConfirm">取消</button>
      <button class="confirm-btn ok" bindtap="doConfirm">确定</button>
    </view>
  </view>
</view>




<!-- ===== 分类管理弹窗 ===== -->
<view class="overlay {{showCategoryManager?'show':''}}" bindtap="closeCategoryManagerOverlay">
  <view class="modal" catchtap="stopProp">
    <view class="modal-close" bindtap="closeCategoryManager">✕</view>
    <view class="modal-title">分类管理</view>

    <!-- 添加 -->
    <view class="cat-add-row">
      <input class="cat-input"
             placeholder="新分类名称"
             value="{{newCatName}}"
             bindinput="onNewCatInput"
             bindconfirm="addCategory" />
      <button class="btn-primary sm" bindtap="addCategory">添加</button>
    </view>

    <!-- 列表 -->
    <view class="sec">
      <view class="sec-title">已有分类（点击删除）</view>
      <view wx:if="{{cats.length===0}}" class="empty-sm">暂无分类</view>
      <view wx:for="{{cats}}" wx:key="*this"
            class="cat-item"
            bindtap="deleteCategory" data-cat="{{item}}">
        <text>{{item}}</text>
        <text class="cat-del">✕</text>
      </view>
    </view>

    <!-- 颜色说明 -->
    <view class="sec">
      <view class="sec-title">分类颜色</view>
      <view class="color-legend">
        <view class="color-legend-item"><view class="cl-dot" style="background:#e74c3c"></view>健康</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#3498db"></view>学习</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#9b59b6"></view>工作</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#2ecc71"></view>生活</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#e67e22"></view>运动</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#1abc9c"></view>阅读</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#f39c12"></view>饮食</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#e84393"></view>美妆</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#00cec9"></view>兴趣</view>
        <view class="color-legend-item"><view class="cl-dot" style="background:#95a5a6"></view>其他</view>
      </view>
    </view>

    <button class="btn-outline full" bindtap="closeCategoryManager">完成</button>
  </view>
</view>
"""

# ======================== index.wxss ========================
INDEX_WXSS = r"""/* =============================================================
   习惯打卡 - 主页面样式（完整修正版 v3）
   ============================================================= */

/* ===== 页面容器 ===== */
.page {
  display: flex;
  flex-direction: column;
  padding: 0 14px 24px;
  box-sizing: border-box;
  background: var(--bg);
  color: var(--text);
  transition: background 0.35s, color 0.35s;
}
/* 暗色模式 */
.page.dark {
  --bg:       #1a1a2e;
  --text:     #e0e0e0;
  --text-muted: #8888aa;
  --text-faint: #666688;
  --card:      #22223a;
  --card-s:    rgba(255,255,255,0.06);
  --border:   #333355;
  --bl:       #2a2a44;
  --hb:       #22223a;
  --glass:     rgba(30,30,50,0.96);
  --ov:       rgba(0,0,0,0.55);
  --wdb:      #444466;
  --wdbg:     #1a1a2e;
  --wdf:      #6c5ce7;
  --wdft:     #e0e0e0;
  --inp:      #22223a;
  --hbg:      #6c5ce7;
  --htx:      #e0e0e0;
  --spd:      #f39c12;
  --spm:      #666688;
  --h0:       #22223a;
  --h1:       #1a3a2a;
  --h2:       #1a4a3a;
  --h3:       #1a5a4a;
  --h4:       #1a6a5a;
  --togbg:    #444466;
  --pomo:     #ff6b6b;
  --charttext: #cccccc;
}


/* ===== 顶栏 ===== */
.topbar {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 14px 100px 4px 14px;
}
.title {
  font-size: 44px;
  font-weight: 900;
  letter-spacing: 0.1em;
  color: var(--text);
  line-height: 1.1;
}
.topbar-btns {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 4px;
}
.iconbtn {
  width: 34px;
  height: 34px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--text-faint);
  transition: all 0.2s;
}
.iconbtn:active {
  background: rgba(0,0,0,0.06);
  transform: scale(0.92);
}
.greeting {
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  margin-bottom: 1px;
}
.subtitle {
  text-align: center;
  font-size: 12px;
  color: var(--text-faint);
  margin-bottom: 10px;
}
.hl {
  color: var(--text-muted);
  font-weight: 500;
}


/* ===== 进度卡片 ===== */
.head {
  background: var(--hbg);
  border-radius: 14px;
  padding: 14px 16px 16px;
  color: var(--htx);
  margin-bottom: 12px;
  box-shadow: 0 3px 12px rgba(74,63,53,0.14);
  animation: slideUp 0.5s ease-out;
}
.head-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.head-time {
  font-size: 12px;
  opacity: 0.5;
  font-weight: 300;
  letter-spacing: 0.05em;
}
.head-icon { font-size: 12px; opacity: 0.35; }
.head-quote {
  font-size: 12px;
  opacity: 0.45;
  font-style: italic;
  letter-spacing: 0.04em;
}
.head-progress {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 7px;
}
.head-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.head-count {
  font-size: 20px;
  font-weight: 600;
  opacity: 0.85;
}
.progress-bar {
  height: 4px;
  background: rgba(245,240,235,0.18);
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--htx);
  border-radius: 3px;
  transition: width 0.4s ease;
}
.head-sub {
  display: block;
  text-align: right;
  font-size: 11px;
  opacity: 0.35;
  margin-top: 5px;
  font-style: italic;
}


/* ===== 搜索 ===== */
.search-box {
  position: relative;
  margin-bottom: 10px;
  animation: fadeInDown 0.4s ease-out;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: var(--text-faint);
  pointer-events: none;
}
.search-input {
  width: 100%;
  height: 38px;
  padding: 0 14px 0 32px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  background: var(--inp);
  color: var(--text);
  box-sizing: border-box;
  line-height: 38px;
}
.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: var(--text-faint);
  padding: 2px 4px;
  display: none;
}
.search-clear.show { display: block; }


/* ===== 本周 ===== */
.week-section { margin-bottom: 10px; }
.week-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.section-label {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  font-weight: 400;
}
.week-links {
  display: flex;
  gap: 8px;
}
.link {
  font-size: 11px;
  color: var(--text-faint);
  font-style: italic;
  transition: color 0.2s;
}
.link:active { color: var(--p); }
.week-dots {
  display: flex;
  gap: 4px;
}
.dot-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: transform 0.2s;
}
.dot-col:active { transform: scale(0.92); }
.dot-name {
  font-size: 10px;
  color: var(--text-faint);
  letter-spacing: 0.03em;
}
.dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1.5px solid var(--wdb);
  background: var(--wdbg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--text);
  transition: all 0.3s;
}
.dot.filled {
  background: var(--wdf);
  border-color: var(--wdf);
  color: var(--wdft);
  transform: scale(1.1);
}
.dot.today { border-color: var(--p); border-width: 2px; }
.dot.partial {
  background: var(--p);
  border-color: var(--p);
  color: var(--pt);
  opacity: 0.55;
}


/* ===== 分类筛选栏 ===== */
.cat-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.cat-scroll {
  flex: 1;
  white-space: nowrap;
  display: flex;
  gap: 4px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.cat-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 8px;
  background: transparent;
  color: var(--text-faint);
  border: 1px solid var(--bl);
  font-size: 11px;
  letter-spacing: 0.03em;
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1.5;
  height: 24px;
  transition: all 0.2s;
}
.cat-chip.active {
  background: var(--p);
  color: var(--pt);
  border-color: var(--p);
}
.cat-chip.arch { border-style: dashed; }
.cat-add {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 8px;
  background: var(--hb);
  color: var(--text-muted);
  border: 1px dashed var(--bl);
  font-size: 11px;
  height: 24px;
  line-height: 1.5;
  white-space: nowrap;
}


/* ===== 习惯列表 ===== */
.habit-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}
.empty {
  text-align: center;
  padding: 28px 20px;
  color: var(--text-faint);
  font-size: 14px;
  letter-spacing: 0.05em;
}
.habit-item {
  background: var(--card);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 1px 5px var(--card-s);
  position: relative;
  border-left: 3px solid #95a5a6;
  transition: transform 0.15s, box-shadow 0.15s;
  animation: popIn 0.3s ease-out;
  animation-fill-mode: backwards;
  will-change: transform, opacity;
}
.habit-item:active { transform: scale(0.98); }
.habit-item.archived { opacity: 0.45; }
.habit-item.archived .habit-name { text-decoration: line-through; }

/* 分类颜色条 */
.cat-jk { border-left-color: #e74c3c; background: linear-gradient(to right, rgba(231,76,60,0.09), transparent 55%); }
.cat-xx { border-left-color: #3498db; background: linear-gradient(to right, rgba(52,152,219,0.09), transparent 55%); }
.cat-gz { border-left-color: #9b59b6; background: linear-gradient(to right, rgba(155,89,182,0.09), transparent 55%); }
.cat-sh { border-left-color: #2ecc71; background: linear-gradient(to right, rgba(46,204,113,0.09), transparent 55%); }
.cat-yd { border-left-color: #e67e22; background: linear-gradient(to right, rgba(230,126,34,0.09), transparent 55%); }
.cat-yued { border-left-color: #1abc9c; background: linear-gradient(to right, rgba(26,188,156,0.09), transparent 55%); }
.cat-ys { border-left-color: #f39c12; background: linear-gradient(to right, rgba(243,156,18,0.09), transparent 55%); }
.cat-mz { border-left-color: #e84393; background: linear-gradient(to right, rgba(232,67,147,0.09), transparent 55%); }
.cat-xq { border-left-color: #00cec9; background: linear-gradient(to right, rgba(0,206,201,0.09), transparent 55%); }
.cat-qt { border-left-color: #95a5a6; background: linear-gradient(to right, rgba(149,165,166,0.09), transparent 55%); }

/* 勾选框 */
.check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1.5px solid var(--wdb);
  background: var(--card);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.25s;
}
.check.checked {
  background: var(--p);
  border-color: var(--p);
  animation: popCheck 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.check.checked::after {
  content: '';
  display: block;
  width: 6px;
  height: 9px;
  border: solid var(--pt);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 1px;
}

/* 习惯内容 */
.habit-body {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 5px;
  overflow: hidden;
}
.edit-input {
  font-size: 15px;
  font-weight: 450;
  color: var(--text);
  border: none;
  border-bottom: 1.5px solid var(--p);
  background: transparent;
  padding: 0;
  height: 28px;
  min-width: 60px;
  line-height: 28px;
}
.habit-name {
  font-size: 16px;
  font-weight: 450;
  color: var(--text);
  padding: 2px 0;
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.03em;
  line-height: 1.5;
}
.habit-tags {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.tag-cat {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  background: var(--hb);
  color: var(--text-muted);
  letter-spacing: 0.03em;
}
.tag-goal {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 6px;
  background: var(--sucb);
  color: var(--suc);
  letter-spacing: 0.02em;
}
.tag-goal.missed { background: var(--dngb); color: var(--dng); }
.tag-diff { font-size: 10px; letter-spacing: 0; }

.streak {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
  margin-left: auto;
  padding-left: 6px;
  font-size: 13px;
}
.streak-num { min-width: 10px; text-align: center; }
.streak-num.done { color: var(--acc); }
.streak-num.missed { color: var(--text-faint); }
.streak-fire.done { color: var(--spd); }
.streak-fire.missed { filter: grayscale(1); opacity: 0.45; color: var(--spm); }

.habit-info {
  width: 24px; height: 24px;
  font-size: 12px;
  color: var(--text-faint);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.habit-del {
  width: 24px; height: 24px;
  font-size: 12px;
  color: var(--text-faint);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}


/* ===== 统计卡片 ===== */
.stats-row {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}
.stat-card {
  background: var(--card);
  border-radius: 10px;
  padding: 12px 4px;
  flex: 1;
  text-align: center;
  box-shadow: 0 1px 4px var(--card-s);
  min-width: 0;
  animation: popIn 0.4s ease-out;
}
.stat-num {
  font-size: 20px;
  font-weight: 700;
  color: var(--p);
  white-space: nowrap;
  display: block;
}
.stat-label {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 2px;
  letter-spacing: 0.02em;
  display: block;
}


/* ===== 建议 ===== */
.sug-row {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.sug-chip {
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 16px;
  background: var(--hb);
  color: var(--text-muted);
  border: 1px dashed var(--border);
  transition: all 0.2s;
}
.sug-chip:active { background: var(--p); color: var(--pt); }


/* ===== 添加习惯 ===== */
.add-row {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
}
.add-input {
  flex: 1;
  height: 40px;
  padding: 0 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  background: var(--inp);
  color: var(--text);
  box-sizing: border-box;
  line-height: 40px;
}
.add-btn {
  height: 40px;
  padding: 0 18px;
  border: none;
  background: var(--p);
  color: var(--pt);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.05em;
  line-height: 40px;
  transition: transform 0.15s, opacity 0.15s;
}
.add-btn::after { border: none; }
.add-btn:active { transform: scale(0.95); opacity: 0.9; }


/* ===== 弹窗通用 ===== */
.overlay {
  position: fixed;
  inset: 0;
  background: var(--ov);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}
.overlay.show {
  opacity: 1;
  pointer-events: auto;
}
.modal {
  background: var(--glass);
  border-radius: 18px 18px 0 0;
  padding: 16px 18px 24px;
  max-width: 440px;
  width: 100%;
  border: none;
  box-shadow: 0 -4px 28px rgba(0,0,0,0.13);
  max-height: 82vh;
  overflow-y: auto;
  position: relative;
  animation: slideUpModal 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 26px;
  height: 26px;
  background: var(--hb);
  border-radius: 50%;
  font-size: 13px;
  color: var(--text-faint);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.2s;
}
.modal-close:active { background: var(--p); color: var(--pt); transform: scale(0.9); }
.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: 0.06em;
  margin-bottom: 10px;
  text-align: center;
}
.modal-desc {
  font-size: 12px;
  color: var(--text-faint);
  text-align: center;
  margin-bottom: 10px;
  display: block;
}


/* ===== 确认弹窗（精致版） ===== */
.modal-confirm {
  background: var(--glass);
  border-radius: 16px;
  padding: 24px 20px;
  max-width: 320px;
  width: 85%;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  text-align: center;
  animation: popIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.confirm-icon {
  font-size: 36px;
  margin-bottom: 10px;
}
.confirm-text {
  font-size: 14px;
  font-weight: 400;
  color: var(--text);
  margin-bottom: 20px;
  line-height: 1.7;
  text-align: center;
  display: block;
}
.confirm-btns {
  display: flex;
  gap: 10px;
}
.confirm-btn {
  flex: 1;
  height: 38px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  line-height: 38px;
  border: none;
  transition: all 0.2s;
}
.confirm-btn::after { border: none; }
.confirm-btn.cancel {
  background: var(--hb);
  color: var(--text-muted);
}
.confirm-btn.cancel:active { background: var(--bl); }
.confirm-btn.ok {
  background: var(--p);
  color: var(--pt);
}
.confirm-btn.ok:active { opacity: 0.85; transform: scale(0.97); }
.confirm-btn.ok.danger { background: var(--dng); color: #fff; }


/* ===== 区块 ===== */
.sec { margin-bottom: 12px; }
.sec:last-child { margin-bottom: 0; }
.sec-title {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  margin-bottom: 5px;
  font-weight: 400;
  display: block;
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}
.row text { font-size: 14px; color: var(--text); }


/* ===== Toggle 开关 ===== */
.toggle {
  width: 38px;
  height: 22px;
  background: var(--togbg);
  border-radius: 11px;
  position: relative;
  flex-shrink: 0;
  transition: background 0.25s;
}
.toggle.on { background: var(--p); }
.toggle .toggle-knob {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.18);
  transition: transform 0.25s;
}
.toggle.on .toggle-knob { transform: translateX(16px); }


/* ===== 颜色圆点 ===== */
.color-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid transparent;
  transition: transform 0.2s, border-color 0.2s;
}
.color-dot:active { transform: scale(1.15); }


/* ===== 按钮 ===== */
.btn-primary {
  padding: 7px 14px;
  border: none;
  border-radius: 8px;
  background: var(--p);
  color: var(--pt);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.03em;
  transition: all 0.2s;
}
.btn-primary.sm { padding: 5px 12px; font-size: 12px; }
.btn-primary.full { width: 100%; }
.btn-primary::after { border: none; }
.btn-primary:active { opacity: 0.85; transform: scale(0.97); }

.btn-outline {
  padding: 7px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text);
  font-size: 13px;
}
.btn-outline.full { width: 100%; }
.btn-outline::after { border: none; }

.btn-danger {
  padding: 7px 14px;
  border: none;
  border-radius: 8px;
  background: var(--dng);
  color: #fff;
  font-size: 13px;
  transition: all 0.2s;
}
.btn-danger.full { width: 100%; }
.btn-danger.sm { padding: 5px 12px; font-size: 12px; }
.btn-danger::after { border: none; }
.btn-danger:active { opacity: 0.85; transform: scale(0.97); }

.btn-sm {
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  font-size: 11px;
  background: var(--hb);
  color: var(--text);
}
.btn-sm.done { background: var(--suc); color: #fff; }
.btn-sm::after { border: none; }


/* ===== 选择器值 ===== */
.picker-val {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text);
  display: inline-block;
  transition: border-color 0.2s;
}
.picker-val:active { border-color: var(--p); }


/* =============================================================
   弹窗内容样式
   ============================================================= */

/* ----- 详情弹窗 ----- */
.detail-cat {
  font-size: 12px;
  color: var(--text-faint);
  text-align: center;
  margin-bottom: 10px;
  display: block;
}
.detail-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  margin-bottom: 12px;
}
.detail-stat {
  background: var(--hb);
  border-radius: 10px;
  padding: 10px 4px;
  text-align: center;
}
.detail-num {
  font-size: 18px;
  font-weight: 600;
  color: var(--p);
  display: block;
}
.detail-lbl {
  font-size: 10px;
  color: var(--text-faint);
  margin-top: 2px;
  display: block;
}

/* 图表 */
.chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 40px;
  margin-top: 4px;
}
.chart-bar {
  flex: 1;
  border-radius: 3px 3px 0 0;
  background: var(--p);
  opacity: 0.45;
  min-height: 3px;
  transition: height 0.3s;
}
.chart-bar.today { opacity: 0.85; }
.chart-labels {
  display: flex;
  gap: 3px;
  margin-top: 3px;
}
.chart-labels text {
  flex: 1;
  text-align: center;
  font-size: 8px;
  color: var(--text-faint);
}

/* 备注 */
.note-area {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  background: var(--inp);
  color: var(--text);
  min-height: 50px;
  box-sizing: border-box;
  line-height: 1.6;
}
/* 历史备注 */
.history-item {
  display: flex;
  gap: 6px;
  padding: 5px 0;
  border-bottom: 1px solid var(--bl);
  font-size: 12px;
}
.history-date {
  color: var(--text-faint);
  white-space: nowrap;
  flex-shrink: 0;
}
.history-note {
  color: var(--text-muted);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.empty-sm {
  text-align: center;
  padding: 14px;
  color: var(--text-faint);
  font-size: 13px;
}


/* ----- 看板弹窗 ----- */
.modal-lg { max-width: 480px; }

.dash-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}
.dash-card {
  background: var(--hb);
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
}
.dash-num {
  font-size: 22px;
  font-weight: 700;
  color: var(--p);
  display: block;
}
.dash-lbl {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 2px;
  display: block;
}

/* 排行 */
.rank-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--card);
  font-size: 13px;
  margin-bottom: 4px;
}
.rank-idx {
  width: 20px;
  font-weight: 600;
  color: var(--text-faint);
  text-align: center;
}
.rank-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
  font-weight: 400;
}
.rank-bar-wrap {
  flex: 2;
  height: 6px;
  border-radius: 3px;
  background: var(--bl);
  overflow: hidden;
  min-width: 30px;
}
.rank-bar {
  height: 100%;
  border-radius: 3px;
  background: var(--p);
  transition: width 0.4s;
}
.rank-cnt {
  width: 40px;
  text-align: right;
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

/* 成就 */
.ach-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.ach-card {
  background: var(--card);
  border-radius: 10px;
  padding: 12px 6px;
  text-align: center;
  border: 1px solid var(--bl);
  transition: all 0.3s;
}
.ach-card.locked { opacity: 0.35; filter: grayscale(1); }
.ach-card.unlocked {
  opacity: 1;
  border-color: rgba(241,196,15,0.5);
  box-shadow: 0 0 14px rgba(241,196,15,0.18);
}
.ach-icon { font-size: 22px; display: block; margin-bottom: 4px; }
.ach-name { font-size: 11px; color: var(--text); font-weight: 500; display: block; }
.ach-desc { font-size: 9px; color: var(--text-faint); margin-top: 2px; display: block; }


/* ----- 日历弹窗 ----- */
.cal-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.cal-btn {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--hb);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--text);
  transition: background 0.2s;
}
.cal-btn:active { background: var(--p); color: var(--pt); }
.cal-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.05em;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}
.cal-weekdays text {
  text-align: center;
  font-size: 10px;
  color: var(--text-faint);
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}
.cal-cell {
  aspect-ratio: 1;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--text-faint);
  position: relative;
  transition: transform 0.15s, background 0.2s;
}
.cal-cell.l0 { background: var(--h0); }
.cal-cell.l1 { background: var(--h1); }
.cal-cell.l2 { background: var(--h2); }
.cal-cell.l3 { background: var(--h3); }
.cal-cell.l4 { background: var(--h4); color: #fff; }
.cal-cell.today { border: 1.5px solid var(--p); }
.cal-cnt {
  position: absolute;
  bottom: 0px;
  right: 1px;
  font-size: 7px;
  opacity: 0.65;
}

.cal-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 10px;
  justify-content: center;
}
.cal-legend text { font-size: 10px; color: var(--text-faint); }
.cal-dot {
  width: 11px; height: 11px;
  border-radius: 3px;
}
.cal-summary {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
  display: block;
}


/* ----- 周报弹窗 ----- */
.report-card {
  background: var(--hb);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.report-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
  padding: 3px 0;
}
.report-val {
  color: var(--text);
  font-weight: 400;
}


/* ----- 补打卡弹窗 ----- */
.catchup-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--hb);
  font-size: 12px;
  margin-bottom: 4px;
}
.catchup-date {
  min-width: 60px;
  color: var(--text);
}
.catchup-status {
  flex: 1;
  text-align: center;
  font-size: 11px;
  color: var(--text-faint);
}


/* ----- 番茄钟弹窗 ----- */
.modal-pomo { max-width: 380px; }

.pomo-presets {
  display: flex;
  gap: 5px;
  justify-content: center;
  margin: 4px 0;
  flex-wrap: wrap;
}
.pomo-preset {
  padding: 5px 14px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: transparent;
  color: var(--text-faint);
  font-size: 12px;
  transition: all 0.2s;
}
.pomo-preset.active {
  background: var(--pomo);
  color: #fff;
  border-color: var(--pomo);
}
.pomo-preset:active { transform: scale(0.95); }
.pomo-preset.custom {
  background: var(--hb);
  border-style: dashed;
}

.pomo-custom {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 12px 0 16px;
}
.pomo-custom-input {
  width: 55px;
  height: 34px;
  padding: 0 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--inp);
  color: var(--text);
  font-size: 14px;
  text-align: center;
  line-height: 34px;
}

/* 翻牌时钟 */
.flip-clock {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 16px 0 10px;
}
.flip-unit {
  display: flex;
  gap: 4px;
}
.flip-card {
  width: 52px;
  height: 64px;
  border-radius: 10px;
  background: var(--pomo);
  color: #fff;
  font-size: 40px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 10px rgba(231,76,60,0.35);
  transition: background 0.3s;
}
.flip-colon {
  font-size: 36px;
  font-weight: 300;
  color: var(--pomo);
  padding-top: 8px;
}
.flip-lbl {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 5px;
  text-align: center;
  display: block;
}

.pomo-phase {
  text-align: center;
  font-size: 14px;
  margin: 10px 0;
  letter-spacing: 0.06em;
}
.pomo-phase.focus { color: var(--pomo); font-weight: 500; }
.pomo-phase.break { color: var(--suc); font-weight: 500; }

.pomo-controls {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}
.pomo-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}
.pomo-btn::after { border: none; }
.pomo-btn.go { background: var(--pomo); color: #fff; }
.pomo-btn.pause { background: #f39c12; color: #fff; }
.pomo-btn.reset { background: var(--hb); color: var(--text); }
.pomo-btn.skip { background: var(--hb); color: var(--text-muted); }
.pomo-btn:active { opacity: 0.85; transform: scale(0.97); }

.pomo-info {
  text-align: center;
  font-size: 12px;
  color: var(--text-faint);
  margin-top: 8px;
  display: block;
}
.pomo-log {
  max-height: 110px;
  overflow-y: auto;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.pomo-log-item {
  padding: 4px 0;
  border-bottom: 1px solid var(--border);
}


/* ----- 分类管理弹窗 ----- */
.cat-add-row {
  display: flex;
  gap: 6px;
  margin-bottom: 14px;
}
.cat-input {
  flex: 1;
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--inp);
  color: var(--text);
  font-size: 13px;
  line-height: 34px;
}

.cat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 8px;
  background: var(--hb);
  margin-bottom: 5px;
  font-size: 13px;
  color: var(--text);
  transition: background 0.2s;
}
.cat-item:active { background: var(--p); color: var(--pt); }
.cat-del {
  font-size: 11px;
  color: var(--text-faint);
  padding: 2px 4px;
}

.color-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}
.color-legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
}
.cl-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}


/* ===== 动画 ===== */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUpModal {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes popIn {
  0% { opacity: 0; transform: scale(0.82); }
  70% { transform: scale(1.04); }
  100% { opacity: 1; transform: scale(1); }
}
@keyframes popCheck {
  0% { transform: scale(1); }
  40% { transform: scale(1.35); }
  70% { transform: scale(0.88); }
  100% { transform: scale(1); }
}
"""


# ======================== 写入文件 ========================
def write_file(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {path}')

write_file('pages/index/index.js', INDEX_JS)
write_file('pages/index/index.wxml', INDEX_WXML)
write_file('pages/index/index.wxss', INDEX_WXSS)

print('\\nAll files written successfully!')
