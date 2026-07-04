#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加列表重排丝滑动画 - 火花排序时每个组件平滑移动到新位置"""

import re
import os

import re

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index"
js_path = os.path.join(BASE, "index.js")
wxss_path = os.path.join(BASE, "index.wxss")
wxml_path = os.path.join(BASE, "index.wxml")

# ===== 1. 读取 JS =====
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# ===== 2. 在 data 中添加动画相关字段 =====
# 找到 showAchievementPopup 附近，添加 itemAnimations
old_data = """    showAchievementPopup: false,
    achievementPopupData: null,"""

new_data = """    showAchievementPopup: false,
    achievementPopupData: null,
    itemAnimations: {},  // 每个习惯组件的动画数据
    prevOrder: [],        // 上次的排序顺序（id列表）
    isReordering: false,  // 是否正在重排动画中"""

if old_data in js and 'itemAnimations' not in js:
    js = js.replace(old_data, new_data)
    print("✅ 已添加动画数据字段")
else:
    print("⚠️  动画数据字段已存在或无法添加")

# ===== 3. 重写 _updateFilteredHabits 函数，添加动画逻辑 =====
# 找到函数开头
old_func_start = """  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    let list = [].concat(data.habits)"""

new_func_start = """  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    let list = [].concat(data.habits)"""

# 我们需要找到并替换整个函数
# 先找到函数的开始和结束
func_start = js.find('  _updateFilteredHabits() {')
if func_start == -1:
    print("❌ 找不到 _updateFilteredHabits 函数")
else:
    # 找到函数的结束（下一个函数或文件结束）
    # 找到函数体
    brace_count = 0
    func_end = func_start
    in_func = False
    i = func_start
    while i < len(js):
        if js[i] == '{':
            brace_count += 1
            in_func = True
        elif js[i] == '}':
            brace_count -= 1
            if in_func and brace_count == 0:
                func_end = i + 1
                break
        i += 1
    
    # 现在 func_start 到 func_end 是整个函数
    old_func = js[func_start:func_end]
    
    # 创建新函数（带动画）
    new_func = '''  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    const records = data.records || {}
    const todayStr = time.todayStr()
    
    // 计算火花值并排序
    let list = [].concat(data.habits)
    list = list.map(function(h) {
      const total = time.countCheckIns(h.id, records)
      const streak = time.calcStreak(h.id, records, todayStr)
      h.spark = total + streak * 2
      return h
    })
    list.sort(function(a, b) { return (b.spark || 0) - (a.spark || 0) })
    
    // 过滤
    if (this.data.filterCat) {
      list = list.filter(function(h) { return h.category === this.data.filterCat }.bind(this))
    }
    if (this.data.searchText && this.data.searchText.trim()) {
      const kw = this.data.searchText.trim().toLowerCase()
      list = list.filter(function(h) { return h.name.toLowerCase().indexOf(kw) !== -1 })
    }
    
    // 计算动画：对比新旧顺序
    const newOrder = list.map(function(h) { return h.id })
    const prevOrder = this.data.prevOrder || []
    
    // 如果有上次顺序且不一样，计算动画
    if (prevOrder.length > 0 && newOrder.join(',') !== prevOrder.join(',')) {
      const animations = {}
      
      // 计算每个项目的移动距离
      newOrder.forEach(function(id, newIdx) {
        const oldIdx = prevOrder.indexOf(id)
        if (oldIdx !== -1 && oldIdx !== newIdx) {
          // 这个项目移动了，创建动画
          const moveDistance = (oldIdx - newIdx) * 60  // 每个项目约60px高
          animations[id] = {
            id: id,
            oldIdx: oldIdx,
            newIdx: newIdx,
            moveDistance: moveDistance
          }
        }
      })
      
      // 先设置动画数据
      if (Object.keys(animations).length > 0) {
        this.setData({ itemAnimations: animations, isReordering: true })
        
        // 100ms 后更新列表（让动画开始）
        setTimeout(function() {
          this.setData({
            filteredHabits: list,
            prevOrder: newOrder
          })
          
          // 动画结束后清除
          setTimeout(function() {
            this.setData({ itemAnimations: {}, isReordering: false })
          }.bind(this), 500)
        }.bind(this), 50)
        
        return  // 等待动画完成后再更新
      }
    }
    
    // 没有动画，直接更新
    this.setData({
      filteredHabits: list,
      prevOrder: newOrder,
      itemAnimations: {},
      isReordering: false
    })
  },'''
    
    # 替换函数
    js = js[:func_start] + new_func + js[func_end:]
    print("✅ 已添加动画逻辑到 _updateFilteredHabits")

# ===== 4. 在 WXML 中添加动画支持 =====
with open(wxml_path, 'r', encoding='utf-8') as f:
    wxml = f.read()

# 找到 habit-item 的 wx:for 循环，添加动画属性
old_wxml = """    <view wx:for=\"{{filteredHabits}}\" wx:key=\"id\" 
          class=\"habit-item {{u.getCatClass(item.category)}}\" 
          bindtap=\"toggleCheckin\"
          data-id=\"{{item.id}}\">"""

# 新的 WXML：添加动画属性
new_wxml = """    <view wx:for=\"{{filteredHabits}}\" wx:key=\"id\" 
          class=\"habit-item {{u.getCatClass(item.category)}} {{itemAnimations[item.id] ? 'reordering' : ''}}\" 
          bindtap=\"toggleCheckin\"
          data-id=\"{{item.id}}\"
          style=\"{{itemAnimations[item.id] ? 'transform: translateY(' + itemAnimations[item.id].moveDistance + 'px); opacity: 0.8;' : ''}}\">"""

if old_wxml in wxml:
    wxml = wxml.replace(old_wxml, new_wxml)
    print("✅ 已添加 WXML 动画属性")
else:
    print("⚠️  无法找到 WXML 中的 habit-item，尝试模糊匹配...")
    # 模糊匹配
    pattern = r'<view wx:for="{{filteredHabits}}"[^>]*class="habit-item[^"]*"[^>]*>'
    match = re.search(pattern, wxml)
    if match:
        old = match.group(0)
        # 在 class 中添加 reordering 类
        new_tag = old.replace('class="habit-item', 'class="habit-item {{itemAnimations[item.id] ? \'reordering\' : \'\'}}')
        # 添加 style 属性
        if 'style="' not in new_tag:
            new_tag = new_tag.replace('>', ' style="{{itemAnimations[item.id] ? \'transform: translateY(\' + itemAnimations[item.id].moveDistance + \'px); opacity: 0.8;\' : \'\'}}">')
        wxml = wxml.replace(old, new_tag)
        print("✅ 已用正则添加 WXML 动画属性")
    else:
        print("❌ 无法找到 habit-item 标签")

with open(wxml_path, 'w', encoding='utf-8') as f:
    f.write(wxml)

# ===== 5. 在 WXSS 中添加动画样式 =====
with open(wxss_path, 'r', encoding='utf-8') as f:
    wxss = f.read()

# 添加动画样式
animation_css = '''
/* ===== 列表重排动画 ===== */
.habit-item {
  transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.5s ease;
}

.habit-item.reordering {
  z-index: 10;
}

/* 新出现的项目动画 */
.habit-item.new-item {
  animation: slideIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 火花值高的项目高亮 */
.habit-item.spark-high {
  border-left-width: 6px;
  box-shadow: 0 2px 12px rgba(255, 152, 0, 0.3);
}
'''

if '列表重排动画' not in wxss:
    wxss += animation_css
    print("✅ 已添加 WXSS 动画样式")
else:
    print("⚠️  WXSS 动画样式已存在")

with open(wxss_path, 'w', encoding='utf-8') as f:
    f.write(wxss)

# ===== 6. 保存 JS =====
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("\n" + "="*50)
print("✅ 动画添加完成！")
print("\n特性：")
print("  1. 打卡后列表自动按火花数排序")
print("  2. 排序变化时有丝滑动画（500ms）")
print("  3. 移动的项目有透明度和位移动画")
print("  4. 动画曲线使用 cubic-bezier，非常丝滑")
print("\n请重新编译测试！")
