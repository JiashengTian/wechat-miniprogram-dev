  // ===== 搜索 =====
  onSearchConfirm(e) {
    const val = (e && e.detail && e.detail.value || '').trim()
    this.setData({ searchText: val })
    this._updateFilteredHabits()
  },
  clearSearch() {
    this.setData({ searchText: '' })
    this._updateFilteredHabits()
  },

  // ===== 分类过滤 =====
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

  // ===== 添加习惯 =====
  onNewHabitInput(e) {
    this.setData({ newHabitName: e.detail.value || '' })
  },
  doAddHabit() {
    const name = (this.data.newHabitName || '').trim()
    if (!name) { wx.showToast({ title: '输入习惯名称', icon: 'none' }); return }
    const data = app.globalData.data
    if (!data) return
    let maxId = 0
    data.habits.forEach(h => { if (h.id > maxId) maxId = h.id })
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

  // ===== 快捷建议 =====
  addSuggestion(e) {
    const name = e.currentTarget.dataset.name || ''
    if (!name) return
    const data = app.globalData.data
    if (!data) return
    let maxId = 0
    data.habits.forEach(h => { if (h.id > maxId) maxId = h.id })
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

  // ===== 设置弹窗 =====
  openSettings() { this.setData({ showSettings: true }) },
  closeSettingsOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showSettings: false })
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
    setTimeout(() => { this.setData({ showCategoryManager: true }) }, 300)
  },

  exportData() {
    const data = app.globalData.data
    const json = JSON.stringify(data, null, 2)
    wx.setClipboardData({
      data: json,
      success: () => { wx.showToast({ title: '📥 已复制', icon: 'none' }) }
    })
  },

  triggerImport() {
    wx.chooseMessageFile({
      count: 1, type: 'file', extension: ['json'],
      success: (res) => {
        const file = res.tempFiles[0]
        wx.getFileSystemManager().readFile({
          filePath: file.path, encoding: 'utf-8',
          success: (r) => {
            try {
              const imp = JSON.parse(r.data)
              if (!imp.habits || !Array.isArray(imp.habits)) {
                wx.showToast({ title: '⚠️ 无效文件', icon: 'none' }); return
              }
              const cur = app.globalData.data
              imp.stg = cur.stg
              Object.assign(app.globalData.data, imp)
              app.saveData(app.globalData.data)
              this._refreshAll()
              wx.showToast({ title: '📤 导入成功', icon: 'none' })
            } catch(err) { wx.showToast({ title: '⚠️ 格式错误', icon: 'none' }) }
          }
        })
      }
    })
  },

  resetAll() {
    wx.showModal({
      title: '确认重置',
      content: '将永久删除全部数据！此操作不可恢复。',
      success: (res) => {
        if (res.confirm) {
          const empty = app.getEmptyData()
          app.globalData.data = empty
          app.saveData(empty)
          this._refreshAll()
          wx.showToast({ title: '已重置', icon: 'none' })
        }
      }
    })
  },

  // ===== 详情弹窗 =====
  openDetail(e) {
    const id = Number(e.currentTarget.dataset.id)
    const data = app.globalData.data
    const habit = (data.habits || []).find(h => h.id === id)
    if (!habit) return
    const t = time.todayStr()
    const chart = []
    for (let i = 6; i >= 0; i--) {
      const dt = time.addDays(new Date(), -i)
      const ds = time.dateStr(dt)
      chart.push((data.records && data.records[ds] && data.records[ds][id]) ? 1 : 0)
    }
    const max = Math.max(1, chart.reduce((a,b) => a+b, 0))
    const chartPct = chart.map(v => v / max * 100)
    const chartLabels = [0,2,4,6].map(i => {
      const dt = time.addDays(new Date(), -(6-i))
      return time.formatShort(dt)
    })
    const goalVal = ((data.goals || {})[id] && (data.goals || {})[id].weekly) || 0
    const goalLabels = ['无','每周3次','每周5次','每周7次']
    const goalIdx = goalVal === 0 ? 0 : goalVal === 3 ? 1 : goalVal === 5 ? 2 : 3
    const history = []
    if (data.notes && data.notes[id]) {
      Object.keys(data.notes[id])
        .filter(d => d !== t)
        .sort()
        .reverse()
        .slice(0, 5)
        .forEach(d => {
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
    if (e && e.target === e.currentTarget) this.setData({ showDetail: false })
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
    const habit = (data.habits || []).find(h => h.id === id)
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
    // 刷新历史备注
    const history = []
    if (data.notes && data.notes[id]) {
      Object.keys(data.notes[id])
        .filter(d => d !== t)
        .sort()
        .reverse()
        .slice(0, 5)
        .forEach(d => {
          history.push({ date: d, note: data.notes[id][d] })
        })
    }
    this.setData({ detailHistory: history })
    wx.showToast({ title: '📝 已保存', icon: 'none' })
  },

  // ===== 看板弹窗 =====
  openDashboard() {
    this._updateRanked()
    this._updateAchievements()
    this.setData({ showDashboard: true })
  },
  closeDashboardOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showDashboard: false })
  },
  closeDashboard() { this.setData({ showDashboard: false }) },

  _updateRanked() {
    const data = app.globalData.data
    if (!data) return
    const active = (data.habits || []).filter(h => !h.archived)
    const ranked = active.map(h => ({
      name: h.name,
      count: time.countCheckIns(h.id, data.records || {})
    })).sort((a, b) => b.count - a.count)
    const maxCount = ranked.length ? Math.max(1, ranked[0].count) : 1
    const withPct = ranked.map(r => ({
      ...r,
      pct: Math.round(r.count / maxCount * 100)
    }))
    this.setData({ rankedHabits: withPct })
  },

  // ===== 日历弹窗 =====
  openCalendar() {
    this.setData({ calOffset: 0 })
    this._updateCalendar()
    this.setData({ showCalendar: true })
  },
  closeCalendarOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showCalendar: false })
  },
  closeCalendar() { this.setData({ showCalendar: false }) },
  prevMonth() { this.data.calOffset--; this._updateCalendar() },
  nextMonth() { this.data.calOffset++; this._updateCalendar() },

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
      const active = (data.habits || []).filter(h => !h.archived).length
      const level = active > 0 ? Math.min(Math.round(dn / Math.max(active, 1) * 4), 4) : 0
      const isToday = ds === today
      if (active > 0) { totalDays++; if (dn > 0) doneDays++ }
      cells.push({ day: d, level, isToday, count: dn, date: ds })
    }
    const calTitle = y + '年' + (m + 1) + '月'
    const calSummary = '本月 ' + totalDays + ' 天有记录，' + doneDays + ' 天完成（' + (totalDays > 0 ? Math.round(doneDays / totalDays * 100) : 0) + '%）'
    this.setData({
      calendarCells: cells,
      calendarTitle: calTitle,
      calendarSummary: calSummary
    })
  },

  showDateTip(e) {
    const date = e.currentTarget.dataset.date || ''
    if (!date) return
    const data = app.globalData.data
    const dr = (data.records && data.records[date]) || {}
    const names = (data.habits || []).filter(h => !h.archived && dr[h.id]).map(h => h.name)
    if (names.length === 0) {
      wx.showToast({ title: '📭 ' + date + ' 无打卡', icon: 'none' })
    } else {
      wx.showToast({ title: '✅ ' + date + '：' + names.join('、'), icon: 'none', duration: 3000 })
    }
  },

  // ===== 周报弹窗 =====
  openReport() {
    this.setData({ reportIsWeek: true })
    this._updateReport()
    this.setData({ showReport: true })
  },
  closeReportOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showReport: false })
  },
  closeReport() { this.setData({ showReport: false }) },
  toggleReportMode() {
    this.setData({ reportIsWeek: !this.data.reportIsWeek })
    this._updateReport()
  },

  _updateReport() {
    const data = app.globalData.data
    if (!data) return
    const active = (data.habits || []).filter(h => !h.archived)
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
    active.forEach(h => { habitCounts[h.id] = { name: h.name, done: 0 } })
    let cur = new Date(start)
    while (cur <= end) {
      const ds = time.dateStr(cur)
      const dr = (data.records && data.records[ds]) || {}
      const dayDone = active.filter(h => dr[h.id]).length
      days.push({ date: ds, done: dayDone, total: active.length })
      totalAll += active.length
      totalDone += dayDone
      if (dayDone >= active.length) fullDays++
      if (dayDone === 0) zeroDays++
      active.forEach(h => { if (dr[h.id]) habitCounts[h.id].done++ })
      cur.setDate(cur.getDate() + 1)
    }
    const rate = totalAll > 0 ? Math.round(totalDone / totalAll * 100) : 0
    const bestDay = days.reduce((best, d) => d.done > (best ? best.done : -1) ? d : best, null)
    const habitList = Object.values(habitCounts).map(h => ({
      ...h,
      rate: totalDaysCount > 0 ? Math.round(h.done / totalDaysCount * 100) : 0
    }))
    this.setData({
      reportData: {
        done: totalDone, total: totalAll, rate, fullDays, zeroDays, totalDays: totalDaysCount,
        habits: habitList,
        bestDay: (bestDay && bestDay.done > 0) ? { date: time.formatDate(new Date(bestDay.date)), done: bestDay.done, total: bestDay.total } : null
      }
    })
  },

  // ===== 补打卡弹窗 =====
  openCatchup() {
    this.setData({ catchupSelectedName: '' })
    this._updateCatchup()
    this.setData({ showCatchup: true })
  },
  closeCatchupOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showCatchup: false })
  },
  closeCatchup() { this.setData({ showCatchup: false }) },

  onCatchupHabitChange(e) {
    const idx = e.detail.value
    const habits = this.data.catchupHabits
    const sel = habits[idx]
    this.setData({ catchupSelectedName: sel ? sel.name : '' })
    this._updateCatchup()
  },

  _updateCatchup() {
    const data = app.globalData.data
    if (!data) return
    const days = []
    const today = new Date()
    const selName = this.data.catchupSelectedName
    const selId = (data.habits || []).find(h => h.name === selName)?.id
    for (let i = 1; i <= 14; i++) {
      const dt = time.addDays(today, -i)
      const ds = time.dateStr(dt)
      const checked = !!(selId && data.records && data.records[ds] && data.records[ds][selId])
      days.push({
        date: ds,
        label: time.formatShort(dt),
        checked,
        status: checked ? '已打卡' : (selId ? '未打卡' : '—')
      })
    }
    this.setData({
      catchupHabits: (data.habits || []).filter(h => !h.archived),
      catchupDays: days
    })
  },

  doCatchup(e) {
    const date = e.currentTarget.dataset.date || ''
    const name = this.data.catchupSelectedName
    if (!name) { wx.showToast({ title: '⚠️ 请先选择习惯', icon: 'none' }); return }
    const data = app.globalData.data
    const habit = (data.habits || []).find(h => h.name === name)
    if (!habit) return
    if (!data.records) data.records = {}
    if (!data.records[date]) data.records[date] = {}
    data.records[date][habit.id] = true
    ach.checkAchievements(data)
    app.saveData(data)
    this._refreshAll()
    this._updateCatchup()
    wx.showToast({ title: '✅ 已补打', icon: 'none' })
  },

  // ===== 番茄钟弹窗 =====
  openPomodoro() { this.setData({ showPomodoro: true }) },
  closePomodoroOverlay(e) {
    if (e && e.target === e.currentTarget) this.closePomodoro()
  },
  closePomodoro() {
    if (this.data.pomoRunning) this._stopPomo()
    this.setData({ showPomodoro: false })
  },

  setPomoPreset(e) {
    const min = Number(e.currentTarget.dataset.min)
    if (this.data.pomoRunning) return
    this.setData({
      pomoFocusLen: min * 60,
      pomoSeconds: min * 60,
      pomoPhase: 'focus'
    })
    this._updatePomoDisplay()
  },

  onCustomPomoInput(e) {
    this.setData({ customPomoMin: e.detail.value || '' })
  },

  setCustomPomo() {
    const min = Number(this.data.customPomoMin)
    if (!min || min < 1 || min > 120) { wx.showToast({ title: '请输入1-120分钟', icon: 'none' }); return }
    this.setData({
      pomoFocusLen: min * 60,
      pomoSeconds: min * 60,
      pomoPhase: 'focus'
    })
    this._updatePomoDisplay()
    wx.showToast({ title: '🍅 ' + min + '分钟', icon: 'none' })
  },

  focusCustom() {
    this.setData({ customPomoMin: '' })
  },

  togglePomo() {
    if (this.data.pomoRunning) this._stopPomo()
    else this._startPomo()
  },

  _startPomo() {
    if (this.data.pomoSeconds <= 0) {
      this.setData({ pomoSeconds: this.data.pomoFocusLen, pomoPhase: 'focus' })
      this._updatePomoDisplay()
    }
    this.setData({ pomoRunning: true })
    this._pomoTimer = setInterval(() => {
      let sec = this.data.pomoSeconds - 1
      if (sec <= 0) {
        clearInterval(this._pomoTimer)
        this._pomoTimer = null
        this._onPomoComplete()
      } else {
        this.setData({ pomoSeconds: sec })
        this._updatePomoDisplay()
      }
    }, 1000)
  },

  _stopPomo() {
    if (this._pomoTimer) { clearInterval(this._pomoTimer); this._pomoTimer = null }
    this.setData({ pomoRunning: false })
  },

  resetPomo() {
    this._stopPomo()
    this.setData({
      pomoSeconds: this.data.pomoFocusLen,
      pomoPhase: 'focus'
    })
    this._updatePomoDisplay()
  },

  skipBreak() {
    if (this.data.pomoPhase !== 'break') return
    this.setData({ pomoPhase: 'focus', pomoSeconds: this.data.pomoFocusLen })
    this._updatePomoDisplay()
    wx.showToast({ title: '⏭ 跳过休息', icon: 'none' })
  },

  _onPomoComplete() {
    const data = app.globalData.data
    if (!data.pomo) data.pomo = { today: 0, date: '', log: [] }
    const t = time.todayStr()
    if (data.pomo.date !== t) { data.pomo.today = 1; data.pomo.date = t }
    else data.pomo.today++
    const now = new Date()
    const timeStr = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0')
    data.pomo.log.push({ time: timeStr, dur: this.data.pomoFocusLen / 60 })
    ach.checkAchievements(data)
    app.saveData(data)
    wx.showToast({ title: '🍅 完成！', icon: 'none', duration: 2000 })
    this.setData({
      pomoPhase: 'break',
      pomoSeconds: 300,
      pomoToday: data.pomo.today,
      pomoTotal: data.pomo.log.length,
      pomoLogs: data.pomo.log.slice(-10).reverse()
    })
    this._updatePomoDisplay()
  },

  _updatePomoDisplay() {
    const s = this.data.pomoSeconds
    const min = Math.floor(s / 60)
    const sec = s % 60
    const minStr = String(min).padStart(2, '0')
    const secStr = String(sec).padStart(2, '0')
    const data = app.globalData.data
    const pomo = (data && data.pomo) || { today: 0, log: [] }
    this.setData({
      pomoMinStr: [minStr[0], minStr[1]],
      pomoSecStr: [secStr[0], secStr[1]],
      pomoToday: pomo.today || 0,
      pomoTotal: (pomo.log || []).length,
      pomoLogs: (pomo.log || []).slice(-10).reverse()
    })
  },

  // ===== 分类管理弹窗 =====
  openCategoryManager() { this.setData({ showCategoryManager: true }) },
  closeCategoryManagerOverlay(e) {
    if (e && e.target === e.currentTarget) this.setData({ showCategoryManager: false })
  },
  closeCategoryManager() { this.setData({ showCategoryManager: false }) },

  onNewCatInput(e) { this.setData({ newCatName: e.detail.value || '' }) },

  addCategory() {
    const name = (this.data.newCatName || '').trim()
    if (!name) { wx.showToast({ title: '输入分类名称', icon: 'none' }); return }
    const data = app.globalData.data
    if (!data || !data.cats) return
    if (data.cats.indexOf(name) >= 0) { wx.showToast({ title: '⚠️ 分类已存在', icon: 'none' }); return }
    data.cats.push(name)
    app.saveData(data)
    this.setData({ cats: data.cats, newCatName: '' })
    wx.showToast({ title: '✅ 已添加', icon: 'none' })
  },

  deleteCategory(e) {
    const cat = e.currentTarget.dataset.cat || ''
    if (!cat) return
    const data = app.globalData.data
    if (!data) return
    const used = (data.habits || []).some(h => h.category === cat)
    if (used) {
      wx.showModal({
        title: '确认删除',
        content: '「' + cat + '」分类下有习惯，删除后这些习惯将变为"其他"分类。确定删除？',
        success: (res) => {
          if (res.confirm) {
            (data.habits || []).forEach(h => { if (h.category === cat) h.category = '' })
            data.cats = (data.cats || []).filter(c => c !== cat)
            app.saveData(data)
            this.setData({ cats: data.cats })
            this._refreshAll()
            wx.showToast({ title: '✅ 已删除', icon: 'none' })
          }
        }
      })
      return
    }
    data.cats = (data.cats || []).filter(c => c !== cat)
    app.saveData(data)
    this.setData({ cats: data.cats })
    wx.showToast({ title: '✅ 已删除', icon: 'none' })
  },

  // ===== 确认弹窗 =====
  closeConfirmOverlay(e) {
    if (e && e.target === e.currentTarget) this.cancelConfirm()
  },
  cancelConfirm() { this.setData({ showConfirm: false, confirmCallback: null, confirmText: '' }) },
  doConfirm() {
    const cb = this.data.confirmCallback
    this.setData({ showConfirm: false, confirmCallback: null, confirmText: '' })
    if (typeof cb === 'function') {
      try { cb() } catch(e) { console.error('[确认回调失败]', e) }
    }
  },

  // ===== 阻止冒泡 =====
  stopProp() {},
})
