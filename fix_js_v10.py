#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整修复 index.js - 重写有问题的函数区域"""

import re
import os
import subprocess

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index"
js_path = os.path.join(BASE, "index.js")

with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 方法：找到 addCategory 和 deleteCategory 函数，重新正确写入
# 先删除旧的 addCategory 和 deleteCategory 函数

old_addCategory = """  addCategory() {
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
  },"""

new_addCategory = """  addCategory() {
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
  },"""

if old_addCategory in content:
    content = content.replace(old_addCategory, new_addCategory)
    print("✅ 已修复 addCategory 函数格式")
else:
    print("⚠️  addCategory 函数格式已不同，跳过")

# 修复 deleteCategory 函数
old_deleteCategory = """  deleteCategory(e) {
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
  }),"""

new_deleteCategory = """  deleteCategory(e) {
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
  },"""

if old_deleteCategory in content:
    content = content.replace(old_deleteCategory, new_deleteCategory)
    print("✅ 已修复 deleteCategory 函数格式")
else:
    # 模糊匹配：找到 deleteCategory 函数并替换
    pattern = r'  deleteCategory\(e\) \{[^}]*wx\.showModal\([^}]*\}[^}]*\}\)\s*\}\),'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_deleteCategory + content[match.end():]
        print("✅ 已用正则修复 deleteCategory 函数")
    else:
        print("⚠️  无法匹配 deleteCategory 函数，手动修复...")
        # 找到 deleteCategory 函数的开始和结束
        start = content.find('  deleteCategory(e) {')
        if start != -1:
            # 找到匹配的结尾
            # 从 start 开始，找到第一个 }, 后面跟着 // ===== 成就弹窗 ===== 或另一个函数
            temp = content[start:]
            # 简单的括号匹配
            brace_count = 0
            i = 0
            in_string = False
            escape_next = False
            while i < len(temp):
                c = temp[i]
                if escape_next:
                    escape_next = False
                    i += 1
                    continue
                if c == '\\':
                    escape_next = True
                    i += 1
                    continue
                if c == '"' or c == "'":
                    in_string = not in_string
                elif not in_string:
                    if c == '{':
                        brace_count += 1
                    elif c == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # 找到了函数的结尾
                            end = start + i + 1
                            # 检查后面是否有逗号
                            if end < len(content) and content[end] == ',':
                                end += 1
                            content = content[:start] + new_deleteCategory + content[end:]
                            print("✅ 已手动修复 deleteCategory 函数")
                            break
                i += 1

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证：用 Node.js 检查语法
print("\n" + "="*50)
print("验证 JS 语法...")
import subprocess
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
    
# 也检查 WXSS
wxss_path = os.path.join(BASE, "index.wxss")
with open(wxss_path, 'r', encoding='utf-8') as f:
    wxss_content = f.read()
    
# 检查 .topbar 是否只有一行 min-height
lines = wxss_content.split('\n')
in_topbar = False
topbar_count = 0
for i, line in enumerate(lines):
    if '.topbar {' in line:
        in_topbar = True
        topbar_start = i
    if in_topbar:
        if 'min-height:' in line:
            topbar_count += 1
        if line.strip() == '}' and i > topbar_start:
            in_topbar = False
            
if topbar_count > 1:
    print(f"⚠️  .topbar 中有 {topbar_count} 个 min-height，可能有重复")
else:
    print("✅ WXSS .topbar 样式正确")

print("\n🎉 修复完成！请重新编译。")
