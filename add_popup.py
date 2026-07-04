#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加成就弹窗到WXML（处理Windows换行符）"""
import re

base = r'C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit'
wxml_path = f'{base}\pages\index\index.wxml'

# 读取文件（保留原始换行符）
with open(wxml_path, 'rb') as f:
    content = f.read()

# 将 \r\n 转换为 \n 以便处理
content = content.replace(b'\r\n', b'\n')

# 在番茄钟弹窗前添加成就弹窗
achievement_popup = b'''
<!-- ===== 成就解锁弹窗 ===== -->
<view wx:if="{{showAchievementPopup}}" class="achievement-popup">
  <view class="achievement-popup-content">
    <text class="achievement-icon">{{achievementPopupData.ic}}</text>
    <text class="achievement-title">🎉 成就解锁！</text>
    <text class="achievement-desc">{{achievementPopupData.nm}}</text>
    <button class="achievement-btn" bindtap="closeAchievementPopup">太棒了！</button>
  </view>
</view>
'''

# 在番茄钟弹窗前插入
marker = b'<!-- ===== 番茄钟弹窗 ===== -->'
if marker in content and b'achievement-popup' not in content:
    content = content.replace(marker, achievement_popup + marker)
    print('  ✓ 已添加成就弹窗')
else:
    print('  - 成就弹窗已存在或找不到插入位置')

# 写回文件（使用 \n 换行）
with open(wxml_path, 'wb') as f:
    f.write(content)

print('\n=== 完成 ===')
print('成就弹窗已添加到WXML')
print('请重新编译测试')
