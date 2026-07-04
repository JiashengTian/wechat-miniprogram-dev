#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 _updateFilteredHabits 函数的重复代码"""

import os
import subprocess

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index"
js_path = os.path.join(BASE, "index.js")

with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到问题区域：第272行是 }, （函数结束），第273行开始是重复代码
# 第273行：    const todayStr = time.todayStr()
# 第296行：  }, （重复的结束）
# 我们需要删除第273-296行

# 注意：行号是从1开始的，但列表索引是从0开始的
# 第273行 = 索引272
# 第296行 = 索引295

print(f"文件总行数: {len(lines)}")
print(f"\n第272-297行内容:")
for i in range(271, min(297, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")

# 删除第273-296行（索引272到295）
# 但先确认这些行确实是重复代码
duplicate_start = 272  # 第273行的索引
duplicate_end = 295    # 第296行的索引

# 检查是否确实是重复代码
if duplicate_start < len(lines) and 'const todayStr = time.todayStr()' in lines[duplicate_start]:
    print(f"\n✅ 找到重复代码在第 {duplicate_start+1} 行")
    print(f"✅ 将删除第 {duplicate_start+1} 到 {duplicate_end+1} 行")
    
    # 删除重复代码
    del lines[duplicate_start:duplicate_end+1]
    
    # 保存文件
    with open(js_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ 已删除重复代码")
else:
    print(f"❌ 未找到预期的重复代码")
    print(f"第 {duplicate_start+1} 行内容: {lines[duplicate_start].rstrip()}")

# 验证语法
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
    
    # 尝试找到并修复错误
    err_match = re.search(r'(\d+):(\d+)', result.stderr)
    if err_match:
        err_line = int(err_match.group(1))
        print(f"\n错误在第 {err_line} 行")
        if err_line <= len(lines):
            for i in range(max(0, err_line-3), min(len(lines), err_line+2)):
                marker = ">>>" if i == err_line-1 else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")

print("\n完成！请重新编译。")
