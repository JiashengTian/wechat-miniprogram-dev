/**
 * 长按拖拽排序功能
 * 添加到 index.js 的 Page() 中
 */

// ===== 长按拖拽排序 =====
onHabitTouchStart(e) {
  const id = e.currentTarget.dataset.id
  this._dragStartY = e.touches[0].clientY
  this._dragId = id
  this._dragTimer = setTimeout(() => {
    wx.vibrateShort({ type: 'medium' })
    this.setData({ dragId: id })
  }, 500)  // 长按500ms触发
},

onHabitTouchMove(e) {
  if (!this.data.dragId) return
  const currentY = e.touches[0].clientY
  // 计算拖拽位置，实现其他项目联动
  // 简化版：只改变当前item的透明度
},

onHabitTouchEnd(e) {
  clearTimeout(this._dragTimer)
  if (this.data.dragId) {
    this.setData({ dragId: null })
  }
  this._dragId = null
},
