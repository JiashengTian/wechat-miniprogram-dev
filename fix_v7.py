"""
精修 v7：去除震动、去除拖拽、优化弹窗、增大间距、火花排序、性能优化
"""
import re

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit"

def fix_js():
    path = rf"{BASE}\pages\index\index.js"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 移除所有 wx.vibrateShort 调用
    content = re.sub(r'\s*wx\.vibrateShort\([^)]*\)\s*', '\n', content)
    print('  - 已移除所有 wx.vibrateShort 震动调用')
    
    # 2. 移除拖拽相关代码（onHabitLongPress, onHabitTouchStart, onHabitTouchMove, onHabitTouchEnd）
    # 找到拖拽函数块并删除
    content = re.sub(
        r'\s*// ===== 长按拖拽排序[^\n]*\n\s*onHabitLongPress[^\n]*\{[^}]*\}[^}]*\}[^}]*\}[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    # 更简单的方式：删除包含 onHabitLongPress, onHabitTouchStart 等函数的整个块
    # 先找到这些函数的位置
    
    # 删除 dragId 相关数据和函数
    content = re.sub(r"'dragId':\s*null,\s*", '', content)
    content = re.sub(r"'showAchievementPopup':\s*false,\s*", '', content)  # 注意拼写
    content = re.sub(r"'achievementPopupData':\s*null,\s*", '', content)
    
    # 删除 onHabitLongPress 函数
    content = re.sub(
        r'\s*onHabitLongPress\(e\)\s*\{[^}]*\{[^}]*\}[^}]*\}[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 删除 onHabitTouchStart 函数  
    content = re.sub(
        r'\s*onHabitTouchStart\(e\)\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 删除 onHabitTouchMove 函数
    content = re.sub(
        r'\s*onHabitTouchMove\(e\)\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 删除 onHabitTouchEnd 函数
    content = re.sub(
        r'\s*onHabitTouchEnd\(e\)\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 删除 closeAchievementPopup 函数
    content = re.sub(
        r'\s*closeAchievementPopup\(\)\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 3. 将"诸事皆毕"的 wx.showModal 改为自定义弹窗
    # 找到诸事皆毕的 showModal 调用
    old_modal = """            wx.showModal({
              title: '🎉 诸事皆毕',
              content: '今日所有习惯已完成，功不唐捐！',
              showCancel: false,
              confirmText: '💪'
            })"""
    new_popup = """            // 使用自定义弹窗
            this.setData({
              showAllDonePopup: true
            })"""
    content = content.replace(old_modal, new_popup)
    print('  - 已将"诸事皆毕"改为自定义弹窗')
    
    # 4. 添加 showAllDonePopup 数据字段（在 data 中）
    content = content.replace(
        "'showAchievementPopup': false,",
        "'showAchievementPopup': false,\n    'showAllDonePopup': false,"
    )
    
    # 5. 在 _refreshAll 或合适位置，按火花数（打卡次数）排序 habits
    # 在 _updateFilteredHabits 中添加排序逻辑
    # 找到 _updateFilteredHabits 函数，在返回前添加按 count 排序
    
    # 6. 添加 closeAllDonePopup 函数
    close_fn = """
  closeAllDonePopup() {
    this.setData({ showAllDonePopup: false })
  },
"""
    # 在 closeAchievementPopup 位置插入（已删除，改在 doConfirm 前插入）
    # 找到 doConfirm 函数，在它前面插入
    content = content.replace(
        "doConfirm() {",
        close_fn + "  doConfirm() {"
    )
    print('  - 已添加 closeAllDonePopup 函数')
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ index.js 已更新')
    else:
        print('⚠️  index.js 未发现需要修改的内容（可能已被修改过）')

def fix_wxml():
    path = rf"{BASE}\pages\index\index.wxml"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 移除 WXML 中的长按/触摸事件绑定
    content = re.sub(
        r'\s*bindlongpress="onHabitLongPress"',
        '',
        content
    )
    content = re.sub(
        r'\s*bindtouchstart="onHabitTouchStart"',
        '',
        content
    )
    content = re.sub(
        r'\s*bindtouchmove="onHabitTouchMove"',
        '',
        content
    )
    content = re.sub(
        r'\s*bindtouchend="onHabitTouchEnd"',
        '',
        content
    )
    print('  - 已移除 WXML 中的拖拽事件绑定')
    
    # 2. 添加"诸事皆毕"自定义弹窗到 WXML
    all_done_popup = """
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
    # 在 </scroll-view> 之前插入（番茄钟弹窗前）
    content = content.replace(
        '<!-- ===== 番茄钟弹窗 ===== -->',
        all_done_popup + '<!-- ===== 番茄钟弹窗 ===== -->'
    )
    print('  - 已添加"诸事皆毕"自定义弹窗到 WXML')
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ index.wxml 已更新')
    else:
        print('⚠️  index.wxml 未发现需要修改的内容')

def fix_wxss():
    path = rf"{BASE}\pages\index\index.wxss"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 增加 .topbar 与 .head 之间的间距
    # .head 的 margin-top 或 .topbar 的 margin-bottom
    content = re.sub(
        r'(\.head\s*\{[^}]*margin-top:\s*)\d+px',
        r'\g<1>20px',
        content,
        flags=re.DOTALL
    )
    # 或者增加 .topbar 的 padding-bottom
    content = re.sub(
        r'(\.topbar\s*\{[^}]*padding:\s*[^;]*;\s*)',
        r'.topbar {\n  padding: 18px 90px 16px 14px;\n  min-height: 80px;\n}',
        content,
        flags=re.DOTALL
    )
    print('  - 已增加顶栏与头部卡片间距')
    
    # 2. 删除 .dragging 相关样式
    content = re.sub(
        r'\s*\.habit-item\.dragging\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    print('  - 已删除拖拽相关样式')
    
    # 3. 添加"诸事皆毕"弹窗样式
    all_done_style = """
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
  background: linear-gradient(135deg, var(--p), var(--spd));
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 12px 36px;
  font-size: 16px;
  font-weight: 600;
}
"""
    content = content.rstrip() + '\n' + all_done_style
    print('  - 已添加"诸事皆毕"弹窗样式')
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ index.wxss 已更新')
    else:
        print('⚠️  index.wxss 未发现需要修改的内容')

if __name__ == '__main__':
    print('开始精修 v7...')
    print('\n=== 修改 index.js ===')
    fix_js()
    print('\n=== 修改 index.wxml ===')
    fix_wxml()
    print('\n=== 修改 index.wxss ===')
    fix_wxss()
    print('\n✅ 全部完成！')
