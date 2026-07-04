#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加成就弹窗到WXML"""
import sys

wxml_path = r'C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index\index.wxml'

# 读取文件
with open(wxml_path, 'rb') as f:
    content = f.read()

# 转换为Unix换行符
content = content.replace(b'\r\n', b'\n')

# 检查是否已添加
if b'achievement-popup' in content:
    print('  - 成就弹窗已存在')
else:
    # 在番茄钟弹窗前插入成就弹窗
    marker = b'<!-- ===== 番茄钟弹窗 ===== -->'
    popup = b'''
<!-- ===== 成就解锁弹窗 ===== -->
<view wx:if="{{showAchievementPopup}}" class="achievement-popup">
  <view class="achievement-popup-content">
    <text class="achievement-icon">{{achievementPopupData.ic}}</text>
    <text class="achievement-title">\xf09c 成就解锁！</text>
    <text class="achievement-desc">{{achievementPopupData.nm}}</text>
    <button class="achievement-btn" bindtap="closeAchievementPopup">太棒了！</button>
  </view>
</view>
'''
    content = content.replace(marker, popup + marker)
    print('  ✓ 已添加成就弹窗')

# 写回文件
with open(wxml_path, 'wb') as f:
    f.write(content)

print('\n=== 完成 ===')
print('成就弹窗已添加到WXML')
print('请重新编译测试')
