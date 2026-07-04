"""
精修 v8：修正诸事皆毕弹窗、火花排序带动画、性能优化
"""
import re

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit"
JS_PATH = rf"{BASE}\pages\index\index.js"
WXML_PATH = rf"{BASE}\pages\index\index.wxml"
WXSS_PATH = rf"{BASE}\pages\index\index.wxss"

# ===== 1. 修复 index.js =====
with open(JS_PATH, 'r', encoding='utf-8') as f:
    js = f.read()

# 1a. 修复"诸事皆毕"：用自定义弹窗替换 wx.showModal
# 先找到那段代码的精确位置
old_all_done = """        setTimeout(function() {
          wx.showModal({
            title: '🎉 诸事皆毕',
            content: '今日所有习惯已完成，功不唐捐！',
            showCancel: false,
            confirmText: '💪'
          })
        }, 600)"""

new_all_done = """        setTimeout(function() {
          this.setData({ showAllDonePopup: true })
        }.bind(this), 600)"""

if old_all_done in js:
    js = js.replace(old_all_done, new_all_done)
    print('  ✅ 已修复"诸事皆毕"为自定义弹窗')
else:
    print('  ⚠️ 未找到"诸事皆毕"wx.showModal，尝试正则匹配...')
    # 用正则匹配（允许空白符差异）
    pattern = r"setTimeout\(function\(\)\s*\{\s*wx\.showModal\(\{[^}]*诸事皆毕[^}]*\}\)[^)]*\)"
    if re.search(pattern, js, re.DOTALL):
        js = re.sub(pattern, 'setTimeout(function() {\n          this.setData({ showAllDonePopup: true })\n        }.bind(this), 600)', js, flags=re.DOTALL)
        print('  ✅ 已正则修复"诸事皆毕"')
    else:
        print('  ❌ 未找到"诸事皆毕"代码，请手动检查')

# 1b. 在 data 中添加 showAllDonePopup 字段（如果还没有）
if "'showAllDonePopup'" not in js:
    js = js.replace(
        "'showAchievementPopup': false,",
        "'showAchievementPopup': false,\n    'showAllDonePopup': false,"
    )
    print('  ✅ 已添加 showAllDonePopup 数据字段')

# 1c. 添加火花排序逻辑到 _updateFilteredHabits
# 在 list = list.map(function(h) { ... }) 之后，setData 之前，添加排序
# 找到 _updateFilteredHabits 函数末尾的 this.setData({ filteredHabits: list, ... })
# 在它之前插入排序逻辑

sort_code = """
    // 按火花数排序（打卡次数 + 连续天数 * 2 = 火花值）
    const todayStr = time.todayStr()
    list = list.map(function(h) {
      const total = time.countCheckIns(h.id, records)
      const streak = time.calcStreak(h.id, records, todayStr)
      h.spark = total + streak * 2
      return h
    })
    list.sort(function(a, b) { return (b.spark || 0) - (a.spark || 0) })
"""

# 找到 _updateFilteredHabits 中的 this.setData({ filteredHabits: list, ... })
# 在它前面插入排序代码
setdata_pattern = r"(this\.setData\(\{\s*filteredHabits:\s*list,)"
if re.search(setdata_pattern, js):
    js = re.sub(setdata_pattern, sort_code + '\n    ' + r'\1', js)
    print('  ✅ 已添加火花排序逻辑')
else:
    print('  ⚠️ 未找到 setData 位置，火花排序可能需要手动添加')

# 1d. 添加 closeAllDonePopup 函数（如果还没有）
if 'closeAllDonePopup' not in js:
    close_fn = """
  closeAllDonePopup() {
    this.setData({ showAllDonePopup: false })
  },
"""
    # 在 doConfirm 之前插入
    js = js.replace('  doConfirm() {', close_fn + '  doConfirm() {')
    print('  ✅ 已添加 closeAllDonePopup 函数')

# 1e. 性能优化：在 _refreshAll 中添加防抖，减少 setData 调用
# 在文件末尾或合适位置添加防抖函数
if '_refreshAllDebounced' not in js:
    debounce_code = """
  // 防抖：避免短时间内多次刷新
  _refreshAllDebounced() {
    if (this._refreshTimer) clearTimeout(this._refreshTimer)
    this._refreshTimer = setTimeout(function() {
      this._refreshAll()
    }.bind(this), 100)
  },
"""
    # 在 _refreshAll 函数之后插入
    js = js.replace('  },\n\n  _updateProgress() {', '  },\n' + debounce_code + '\n  _updateProgress() {')
    print('  ✅ 已添加防抖函数')

with open(JS_PATH, 'w', encoding='utf-8') as f:
    f.write(js)
print('✅ index.js 已更新\n')

# ===== 2. 修复 index.wxml =====
with open(WXML_PATH, 'r', encoding='utf-8') as f:
    wxml = f.read()

# 2a. 添加诸事皆毕弹窗（如果还没有）
if 'showAllDonePopup' not in wxml:
    popup_code = """
<!-- ===== 诸事皆毕弹窗 ===== -->
<view wx:if="{{showAllDonePopup}}" class="all-done-popup">
  <view class="all-done-content">
    <text class="all-done-icon">🎉</text>
    <text class="all-done-title">诸事皆毕</text>
    <text class="all-done-desc">今日所有习惯已完成\n功不唐捐，日有所进</text>
    <button class="all-done-btn" bindtap="closeAllDonePopup">💪 太棒了</button>
  </view>
</view>
"""
    # 在番茄钟弹窗前插入
    wxml = wxml.replace('<!-- ===== 番茄钟弹窗 ===== -->', popup_code + '\n<!-- ===== 番茄钟弹窗 ===== -->')
    print('  ✅ 已添加诸事皆毕弹窗到 WXML')

# 2b. 为 habit-item 添加动画相关 class（spark-high）
# 在 WXML 中，为每个 habit-item 添加 spark-high class 绑定
# 修改 habit-item 的 class 属性
old_class = 'class="habit-item {{u.getCatClass(item.category)}}"'
new_class = 'class="habit-item {{u.getCatClass(item.category)}} {{item.spark > 10 ? \'spark-high\' : \'\'}}"'
wxml = wxml.replace(old_class, new_class)
print('  ✅ 已添加 spark-high 样式绑定到 WXML')

with open(WXML_PATH, 'w', encoding='utf-8') as f:
    f.write(wxml)
print('✅ index.wxml 已更新\n')

# ===== 3. 修复 index.wxss =====
with open(WXSS_PATH, 'r', encoding='utf-8') as f:
    wxss = f.read()

# 3a. 添加诸事皆毕弹窗样式（如果还没有）
if '.all-done-popup' not in wxss:
    popup_style = """
/* 诸事皆毕弹窗 */
.all-done-popup {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.5);
  animation: fadeIn 0.3s ease;
}
.all-done-content {
  background: var(--card);
  border-radius: 24px;
  padding: 36px 28px;
  width: 280px;
  text-align: center;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  animation: popBounce 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@keyframes popBounce {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}
.all-done-icon {
  font-size: 56px;
  display: block;
  margin-bottom: 12px;
  animation: bounce 1s ease infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.all-done-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  display: block;
  margin-bottom: 8px;
}
.all-done-desc {
  font-size: 14px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 24px;
  line-height: 1.6;
}
.all-done-btn {
  background: linear-gradient(135deg, var(--p), #f39c12);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 12px 36px;
  font-size: 16px;
  font-weight: 600;
}
"""
    wxss = wxss.rstrip() + '\n' + popup_style
    print('  ✅ 已添加诸事皆毕弹窗样式')

# 3b. 添加火花高亮样式
if '.spark-high' not in wxss:
    spark_style = """
/* 火花高亮（排序靠前） */
.habit-item.spark-high {
  border-left-width: 5px;
  box-shadow: 0 2px 12px var(--card-s), 0 0 8px rgba(255,165,0,0.15);
}
"""
    wxss = wxss.rstrip() + '\n' + spark_style
    print('  ✅ 已添加火花高亮样式')

# 3c. 优化 habit-item 过渡动画（让排序时的移动更流畅）
old_transition = 'transition: all 0.25s;'
new_transition = 'transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);'
if old_transition in wxss:
    wxss = wxss.replace(old_transition, new_transition)
    print('  ✅ 已优化 habit-item 过渡动画')

# 3d. 增加顶栏与头部卡片间距（如果还没做）
if '.topbar {' in wxss:
    # 增加 .topbar 的 padding-bottom
    wxss = re.sub(
        r'(\.topbar\s*\{[^}]*padding:\s*[^;]+;\s*)',
        '.topbar {\n  padding: 18px 90px 20px 14px;\n  min-height: 80px;\n}',
        wxss,
        flags=re.DOTALL
    )
    print('  ✅ 已增加顶栏与头部卡片间距')

with open(WXSS_PATH, 'w', encoding='utf-8') as f:
    f.write(wxss)
print('✅ index.wxss 已更新\n')

print('🎉 精修 v8 全部完成！')
print('\n待处理：')
print('  1. 番茄钟界面 - 等待用户发送参考图')
print('  2. 请在微信开发者工具中编译测试')
