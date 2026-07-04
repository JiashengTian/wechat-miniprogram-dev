  /* ========== 补打卡弹窗 ========== */
  openCatchup() {
    this.setData({ catchupSelectedName: '' })
    this.updateCatchup()
    this.setData({ showCatchup: true })
  },
  closeCatchupOverlay(e) {
    if (e && e.target && e.target === e.currentTarget) this.setData({ showCatchup: false })
  },
  closeCatchup() { this.setData({ showCatchup: false }) },

  onCatchupHabitChange(e) {
    const idx = e.detail.value
    const habits = this.data.catchupHabits
    const sel = habits[idx]
    this.setData({ catchupSelectedName: sel ? sel.name : '' })
    this.updateCatchup()
  },

  updateCatchup() {
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
    this.refreshAll()
    this.updateCatchup()
    wx.showToast({ title: '✅ 已补打', icon: 'none' })
  },
END_OF_TEMP_FILE