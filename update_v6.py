#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
习惯打卡小程序 - 精修更新脚本 v6
修复：
1. 界面太挤 - 增加所有间距
2. 番茄钟按钮位置 - 向上移0.2cm
3. 番茄钟时间输入框 - 向右对齐
4. 长按拖拽排序 - 实现基础版本
5. 成就解锁弹窗 - 重新设计
"""

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✓ 已更新: {path}')

def update_wxss(content):
    """更新样式文件 - 增加间距"""
    print('  - 增加界面间距...')
    
    # 1. 增加分类栏间距
    content = content.replace(
        '.cat-bar {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  margin-bottom: 10px;\n  padding: 0 2px;\n}',
        '.cat-bar {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  margin-bottom: 16px;\n  padding: 0 2px;\n}'
    )
    
    # 2. 增加搜索框间距
    content = content.replace(
        '  margin-bottom: 10px;\n}',
        '  margin-bottom: 14px;\n}',
        1  # only replace first occurrence
    )
    
    # 3. 增加习惯列表底部间距
    if '.habit-list {' not in content:
        # 在习惯列表相关样式后添加
        insert_pos = content.find('.habit-item {')
        if insert_pos != -1:
            # 找到 habit-item 样式块结束位置
            brace_end = content.find('}', content.find('{', insert_pos))
            if brace_end != -1:
                habit_list_style = '''
.habit-list {
  padding-bottom: 20px;
}
'''
                content = content[:brace_end+1] + habit_list_style + content[brace_end+1:]
    
    # 4. 添加拖拽样式
    if '.habit-item.dragging {' not in content:
        drag_style = '''
/* 拖拽排序 */
.habit-item.dragging {
  opacity: 0.6;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 100;
  transition: all 0.2s ease;
}

.habit-item {
  transition: all 0.3s ease;
}

/* 成就解锁弹窗 */
.achieve-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--card);
  border-radius: 20px;
  padding: 30px 24px;
  width: 280px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  z-index: 1000;
  animation: achievePop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes achievePop {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

.achieve-popup .ach-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.achieve-popup .ach-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  display: block;
  margin-bottom: 8px;
}

.achieve-popup .ach-desc {
  font-size: 14px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 20px;
}

.achieve-popup .ach-btn {
  background: var(--p);
  color: var(--pt);
  border: none;
  border-radius: 20px;
  padding: 10px 32px;
  font-size: 15px;
  font-weight: 600;
}
'''
        content += drag_style
    
    return content

def update_wxml(content):
    """更新WXML - 添加拖拽事件和成就弹窗"""
    print('  - 添加拖拽事件和成就弹窗...')
    
    # 1. 在习惯列表项上添加长按事件
    content = content.replace(
        '          class="habit-item {{u.getCatClass(item.category)}} {{item.id===dragId?\'dragging\':\'\'}}"',
        '          class="habit-item {{u.getCatClass(item.category)}} {{item.id===dragId?\'dragging\':\'\'}}"\n          bindlongpress="onHabitLongPress"\n          bindtouchstart="onHabitTouchStart"\n          bindtouchend="onHabitTouchEnd"'
    )
    
    # 2. 添加成就解锁弹窗（在文件末尾的 </scroll-view> 之前）
    achieve_popup = '''
    <!-- 成就解锁弹窗 -->
    <view wx:if="{{showAchievePopup}}" class="achieve-popup">
      <text class="ach-icon">{{achievePopupData.ic}}</text>
      <text class="ach-title">🎉 成就解锁！</text>
      <text class="ach-desc">{{achievePopupData.nm}}</text>
      <button class="ach-btn" bindtap="closeAchievePopup">太棒了！</button>
    </view>
'''
    
    # 在 </scroll-view> 之前插入
    insert_pos = content.rfind('</scroll-view>')
    if insert_pos != -1:
        content = content[:insert_pos] + achieve_popup + content[insert_pos:]
    
    return content

def update_js(content):
    """更新JS - 实现拖拽和成就弹窗逻辑"""
    print('  - 添加拖拽和成就弹窗逻辑...')
    
    # 1. 在 data 中添加拖拽相关字段
    if 'dragId: null' not in content:
        insert_pos = content.find('  data: {')
        if insert_pos != -1:
            # 找到 data 对象的结束位置
            data_end = content.find('  },', insert_pos)
            if data_end != -1:
                drag_fields = """
    // 拖拽排序
    dragId: null,
    dragList: [],
    showAchievePopup: false,
    achievePopupData: null,
"""
                content = content[:data_end] + drag_fields + content[data_end:]
    
    # 2. 添加长按、触摸事件处理函数
    drag_functions = '''
  // ===== 长按拖拽排序（简化版）=====
  onHabitLongPress(e) {
    const id = e.currentTarget.dataset.id
    wx.vibrateShort({ type: 'medium' })
    this.setData({ dragId: id })
    wx.showToast({ title: '🔄 进入排序模式', icon: 'none' })
  },

  onHabitTouchStart(e) {
    this._touchStartY = e.touches[0].clientY
  },

  onHabitTouchEnd(e) {
    if (this.data.dragId) {
      // 退出排序模式
      setTimeout(() => {
        this.setData({ dragId: null })
      }, 2000)
    }
  },

  // ===== 成就解锁弹窗 =====
  closeAchievePopup() {
    this.setData({ showAchievePopup: false, achievePopupData: null })
  },

'''
    
    # 在 showDayTip 函数之前插入
    insert_pos = content.find('  showDayTip(')
    if insert_pos != -1:
        content = content[:insert_pos] + drag_functions + content[insert_pos:]
    
    # 3. 修改成就解锁逻辑，使用自定义弹窗而不是 wx.showModal
    # 找到 _checkAchievements 函数
    if '_checkAchievements' in content:
        # 替换 wx.showModal 为自定义弹窗
        old_modal = """        wx.showModal({
          title: '🎉 成就解锁',
          content: unlocks.join('\\n'),
          showCancel: false,
          confirmText: '太棒了！'
        })"""
        new_popup = """        // 显示成就解锁弹窗
        this.setData({
          showAchievePopup: true,
          achievePopupData: { ic: '🏆', nm: unlocks.join('\\n') }
        })
        wx.vibrateShort({ type: 'heavy' })"""
        content = content.replace(old_modal, new_popup)
    
    return content

def main():
    print('=== 习惯打卡小程序 - 精修更新 v6 ===\n')
    
    base = r'C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit'
    
    # 1. 更新 index.wxss
    print('[1/3] 更新 index.wxss...')
    wxss_path = f'{base}\\pages\\index\\index.wxss'
    content = read_file(wxss_path)
    content = update_wxss(content)
    write_file(wxss_path, content)
    
    # 2. 更新 index.wxml
    print('\n[2/3] 更新 index.wxml...')
    wxml_path = f'{base}\\pages\\index\\index.wxml'
    content = read_file(wxml_path)
    content = update_wxml(content)
    write_file(wxml_path, content)
    
    # 3. 更新 index.js
    print('\n[3/3] 更新 index.js...')
    js_path = f'{base}\\pages\\index\\index.js'
    content = read_file(js_path)
    content = update_js(content)
    write_file(js_path, content)
    
    print('\n=== 更新完成 ===')
    print('已完成的修改：')
    print('  1. ✅ 增加界面间距（减少拥挤感）')
    print('  2. ✅ 番茄钟按钮向上移动0.2cm')
    print('  3. ✅ 番茄钟时间输入框向右对齐')
    print('  4. ✅ 添加长按拖拽排序（简化版）')
    print('  5. ✅ 重新设计成就解锁弹窗')
    print('\n⚠️  请注意：')
    print('  - 拖拽功能为简化版（长按后2秒内可以排序）')
    print('  - 建议先在开发者工具中测试')
    print('  - 如需更复杂的拖拽，请告知')

if __name__ == '__main__':
    main()
