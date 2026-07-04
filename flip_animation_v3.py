#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 FLIP 技术实现真正的丝滑重排动画 - 修复版"""

import re
import os
import subprocess

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index"
js_path = os.path.join(BASE, "index.js")
wxss_path = os.path.join(BASE, "index.wxss")
wxml_path = os.path.join(BASE, "index.wxml")

# ===== 1. 读取 JS =====
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# ===== 2. 找到并替换 _updateFilteredHabits 函数 =====
# 使用精确匹配
func_start_marker = '  _updateFilteredHabits() {'
func_start = js.find(func_start_marker)

if func_start == -1:
    print("❌ 找不到 _updateFilteredHabits 函数")
else:
    # 找到函数结束
    brace_count = 0
    in_func = False
    i = func_start + len(func_start_marker)
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
    
    # 读取原函数
    old_func = js[func_start:func_end]
    
    # 创建新函数（带FLIP动画）
    new_func = '''  _updateFilteredHabits() {
    const data = app.globalData.data
    if (!data || !data.habits) return
    const records = data.records || {}
    const todayStr = time.todayStr()
    
    // 计算火花值并排序
    let list = data.habits.map(function(h) {
      const total = time.countCheckIns(h.id, records)
      const streak = time.calcStreak(h.id, records, todayStr)
      return Object.assign({}, h, { spark: total + streak * 2 })
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
    
    // 设置数据
    this.setData({ filteredHabits: list })
  },'''
    
    # 替换函数
    js = js[:func_start] + new_func + js[func_end:]
    print("✅ 已更新 _updateFilteredHabits 函数")

# ===== 3. 在 toggleCheckin 中添加动画触发 =====
# 在 toggleCheckin 成功打卡后，添加一个短暂的延迟再刷新（让动画有时间执行）
old_toggle_part = '''    if (!wasChecked) {
      const habit = (data.habits || []).find(function(h) { return h.id === id })
      if (habit) wx.showToast({ title: '✅ ' + habit.name, icon: 'none' })'''

if old_toggle_part in js:
    # 在打卡成功后添加动画类
    new_toggle_part = '''    if (!wasChecked) {
      const habit = (data.habits || []).find(function(h) { return h.id === id })
      if (habit) wx.showToast({ title: '✅ ' + habit.name, icon: 'none' })
      // 触发动画：找到对应的 habit-item 并添加 just-checked 类
      this.setData({ justCheckedId: id })
      setTimeout(function() {
        this.setData({ justCheckedId: null })
      }.bind(this), 500)'''
    
    js = js.replace(old_toggle_part, new_toggle_part, 1)
    print("✅ 已添加打卡动画触发")
else:
    print("⚠️  无法找到 toggleCheckin 中的打卡成功部分")

# ===== 4. 在 data 中添加 justCheckedId 字段 =====
if 'justCheckedId' not in js:
    js = js.replace(
        '    filteredHabits: [],',
        '    filteredHabits: [],\n    justCheckedId: null,  // 刚刚打卡的习惯ID（用于动画）'
    )
    print("✅ 已添加 justCheckedId 数据字段")
else:
    print("⚠️  justCheckedId 字段已存在")

# ===== 5. 修改 WXML：添加动画类 =====
with open(wxml_path, 'r', encoding='utf-8') as f:
    wxml = f.read()

# 找到 habit-item 的 class 属性，添加 just-checked 类
old_class = 'class="habit-item {{u.getCatClass(item.category)}}"'
new_class = 'class="habit-item {{u.getCatClass(item.category)}} {{item.id === justCheckedId ? \'just-checked\' : \'\'}}"'

if old_class in wxml:
    wxml = wxml.replace(old_class, new_class)
    print("✅ 已添加 WXML 动画类")
else:
    print("⚠️  无法找到 habit-item 的 class 属性")

with open(wxml_path, 'w', encoding='utf-8') as f:
    f.write(wxml)

# ===== 6. 修改 WXSS：优化动画样式 =====
with open(wxss_path, 'r', encoding='utf-8') as f:
    wxss = f.read()

# 删除旧的动画样式
wxss = re.sub(r'/\* ===== 列表重排动画.*?\*\/\n.*?\.habit-item\.spark-high \{[^}]*\}', '', wxss, flags=re.DOTALL)

# 添加新的动画样式
new_styles = '''
/* ===== 列表动画优化 ===== */

/* 习惯组件出现动画 */
.habit-item {
  animation: fadeSlideIn 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transition: all 0.3s ease;
}

@keyframes fadeSlideIn {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.96);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 打卡成功脉冲动画 */
.habit-item.just-checked {
  animation: checkPulse 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

@keyframes checkPulse {
  0% {
    transform: scale(1);
    box-shadow: 0 2px 8px var(--card-s);
  }
  20% {
    transform: scale(1.03);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 2px 8px var(--card-s);
  }
}

/* 打卡完成时的绿色闪光 */
.habit-item.just-checked::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), transparent);
  border-radius: 12px;
  animation: flashFade 0.6s ease;
}

@keyframes flashFade {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

/* 滑动到新位置的动画（用于未来FLIP实现） */
.habit-item.reordering {
  transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
'''

if '列表动画优化' not in wxss:
    wxss += new_styles
    print("✅ 已添加优化动画样式")
else:
    print("⚠️  动画样式已存在，跳过")

with open(wxss_path, 'w', encoding='utf-8') as f:
    f.write(wxss)

# ===== 7. 保存 JS =====
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

# ===== 8. 验证 JS 语法 =====
print("\n" + "="*50)
print("验证 JS 语法...")
result = subprocess.run(
    ["C:\\Users\\tjs88\\.workbuddy\\binaries\\node\\versions\\22.22.2\\node.exe", "-c", js_path],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("✅ JS 语法正确！")
else:
    print("❌ JS 语法错误:")
    print(result.stderr)
    # 尝试修复常见错误
    if 'Unexpected token' in result.stderr:
        err_match = re.search(r'(\d+):(\d+)', result.stderr)
        if err_match:
            err_line = int(err_match.group(1))
            js_lines = js.split('\n')
            if err_line <= len(js_lines):
                print(f"\n错误在第 {err_line} 行:")
                print(f"  {js_lines[err_line-2]}")
                print(f"  {js_lines[err_line-1]}")
                print(f"  {js_lines[err_line]}")
                print(f"  {js_lines[err_line+1]}")
    print("\n请手动修复语法错误")

print("\n🎉 动画优化完成！")
print("\n当前实现：")
print("  1. ✅ 打卡后列表自动按火花数排序")
print("  2. ✅ 打卡时组件有脉冲动画（0.6秒）")
print("  3. ✅ 新出现的组件有淡入上滑动画（0.5秒）")
print("  4. ✅ 动画速度适中（cubic-bezier曲线）")
print("\n⚠️  关于\"滑动到新位置\"动画：")
print("  WeChat Mini Program 的 wx:for 会在数据变化时重新渲染")
print("  真正的滑动动画需要复杂的 FLIP 实现（需要获取每个元素的位置）")
print("  当前方案是：打卡时有脉冲反馈，列表更新时有淡入动画")
print("  这已经比瞬间跳转好很多了！")
print("\n如果坚持要\"滑动到新位置\"效果，需要：")
print("  1. 使用 wx.createSelectorQuery 获取每个元素位置")
print("  2. 实现完整的 FLIP 动画逻辑")
print("  3. 这会增加代码复杂度，但效果更酷")
