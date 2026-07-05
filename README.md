# 🔥  - 微信小程序

<div align="center">

**一款优雅、高效的习惯养成工具**

[![WeChat Mini Program](https://img.shields.io/badge/微信小程序-00C853?style=flat&logo=wechat&logoColor=white)](https://mp.weixin.qq.com/)
[![Version](https://img.shields.io/badge/版本-1.0.0-blue?style=flat)](https://github.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/habit-tracker?style=flat)](https://github.com/yourusername/habit-tracker)

[功能特性](#-功能特性) • [技术栈](#-技术栈) • [安装部署](#-安装部署) • [使用指南](#-使用指南) • [项目结构](#-项目结构) • [贡献指南](#-贡献指南)

</div>

---

## 📖 项目简介

**火花习惯** 是一款基于微信小程序平台的习惯养成工具，通过游戏化的设计理念，帮助用户轻松培养良好习惯，见证每天的进步与成长。

### 🎯 设计理念

> "让每一次坚持都有回馈，让每一个习惯都成为火花"

- **简约而不简单**：去除复杂操作，专注核心体验
- **激励驱动**：火花值、成就系统、连续打卡，让进步可视化
- **个性化定制**：分类管理、难度设置、周目标，打造专属习惯体系
- **数据本地化**：所有数据存储在用户手机，隐私安全有保障

### 🌟 适合人群

- ✅ 想要培养良好习惯的学生、上班族
- ✅ 需要自我管理能力提升的人群
- ✅ 喜欢数据可视化、成就激励的用户
- ✅ 追求简约高效工具的功能控

---

## ✨ 功能特性

### 1️⃣ 习惯打卡 - 简单高效

<table>
<tr>
<td width="50%">

**核心功能**
- 📝 自定义习惯名称
- 🏷️ 分类管理（支持多分类）
- ⭐ 难度星级设置（1-5星）
- ✅ 一键打卡，支持撤销
- 📊 习惯归档与恢复

</td>
<td width="50%">

**智能排序**
- 🔥 火花值自动计算
- 📈 按打卡次数 + 连续天数 × 2 排序
- 🎯 高火花习惯自动置顶
- 📱 支持实时重新排序

</td>
</tr>
</table>

#### 火花值系统

火花值 = 总打卡次数 + 连续天数 × 2

这个公式的设计理念：
- **打卡次数**：体现长期积累
- **连续天数**：奖励坚持，连续越多奖励越大
- **动态排序**：高火花习惯自动排在前面，形成正向激励

---

### 2️⃣ 连续打卡 - 见证坚持

- 🔥 **连续天数统计**：自动计算当前连续打卡天数
- 🏆 **历史最佳**：记录每个习惯的最长连续记录
- 📊 **可视化展示**：火焰图标 + 数字，直观展示坚持成果
- 🎁 **成就解锁**：连续7天、14天、21天、66天分别解锁成就

**连续打卡的心理机制**：
- 可视化进步 → 增强成就感
- 火焰图标 → 形成情感连接
- 断签提醒 → 激发挽回动力

---

### 3️⃣ 周目标 - 合理规划

<table>
<tr>
<td width="33%">

**设定目标**
- 🎯 支持 3/5/7 次每周目标
- 📅 按自然周统计（周一至周日）
- 🔄 随时修改目标

</td>
<td width="33%">

**进度追踪**
- ✅ 本周已完成次数
- 📊 目标完成百分比
- ⚠️ 即将未完成的预警

</td>
<td width="33%">

**激励反馈**
- 🎉 完成目标弹出庆祝
- 💪 未完成显示加油文案
- 📈 周报自动生成

</td>
</tr>
</table>

---

### 4️⃣ 成就系统 - 20项成就

<table>
<tr>
<th>类别</th>
<th>成就名称</th>
<th>解锁条件</th>
<th>图标</th>
</tr>
<tr>
<td rowspan="4">连续打卡</td>
<td>初出茅庐</td>
<td>连续打卡7天</td>
<td>🔥</td>
</tr>
<tr>
<td>半月之功</td>
<td>连续打卡14天</td>
<td>🌙</td>
</tr>
<tr>
<td>廿一日功</td>
<td>连续打卡21天</td>
<td>⭐</td>
</tr>
<tr>
<td>两月功成</td>
<td>连续打卡66天</td>
<td>🏆</td>
</tr>
<tr>
<td rowspan="3">总打卡</td>
<td>百次功成</td>
<td>总打卡100次</td>
<td>💯</td>
</tr>
<tr>
<td>五百之约</td>
<td>总打卡500次</td>
<td>🎖</td>
</tr>
<tr>
<td>千次达成</td>
<td>总打卡1000次</td>
<td>🏅</td>
</tr>
<tr>
<td rowspan="2">全勤</td>
<td>一周全勤</td>
<td>一周全部完成</td>
<td>📆</td>
</tr>
<tr>
<td>月度全勤</td>
<td>全月全部完成</td>
<td>🗓</td>
</tr>
<tr>
<td rowspan="2">专注</td>
<td>专注新手</td>
<td>完成10个番茄</td>
<td>🍅</td>
</tr>
<tr>
<td>专注达人</td>
<td>完成50个番茄</td>
<td>🍅</td>
</tr>
<tr>
<td>分类</td>
<td>多才多艺</td>
<td>使用5个分类</td>
<td>🎨</td>
</tr>
</table>

**成就系统的设计价值**：
- 🎮 **游戏化激励**：让习惯养成像玩游戏一样有趣
- 🏆 **里程碑记录**：见证每一步成长
- 💪 **挫折挽回**：即使断签，其他成就仍可继续解锁
- 📊 **数据可视化**：成就面板直观展示成长轨迹

---

### 5️⃣ 番茄钟 - 专注计时

- ⏱️ **自定义时长**：默认25分钟，支持1-60分钟调节
- ▶️ **一键开始**：简约操作，专注当下
- ⏸️ **暂停继续**：灵活控制，适应真实场景
- 🔔 **时间到提醒**：震动 + 弹窗，及时反馈
- 📊 **数据统计**：完成番茄自动记录，成就系统联动

**番茄工作法原理**：
- 25分钟专注 → 大脑进入心流状态
- 短休息 → 恢复注意力
- 4个番茄后长休息 → 避免疲劳

---

### 6️⃣ 分类管理 - 有序组织

<table>
<tr>
<td width="50%">

**分类功能**
- 📁 支持添加多个分类
- 🏷️ 每个习惯可设置分类
- 🔍 按分类快速筛选
- 🗑️ 支持删除分类（不影响习惯）

</td>
<td width="50%">

**预设分类**
- 💼 工作
- 📚 学习
- 💪 健康
- 🎨 兴趣
- ➕ 自定义分类

</td>
</tr>
</table>

---

### 7️⃣ 数据可视化 - 见证成长

#### 近7日打卡日历

- 📅 直观展示过去7天的打卡情况
- ✅ 已打卡日期高亮显示
- 📊 打卡率自动计算
- 🎨 颜色渐变，美观易懂

#### 周报生成

- 📊 本周打卡次数统计
- 🔥 连续天数展示
- 🎯 周目标完成情况
- 📈 与上周数据对比
- 💾 支持保存到手机

---

### 8️⃣ 个性化设置

<table>
<tr>
<td width="33%">

**外观设置**
- 🎨 浅色/深色模式
- 🔠 字体大小调节
- 🎨 主题色切换

</td>
<td width="33%">

**音效设置**
- 🔔 打卡音效开关
- 🎵 多种音效选择
- 🔕 免打扰时段设置

</td>
<td width="33%">

**提醒设置**
- ⏰ 每日提醒开关
- 🕐 提醒时间设定
- 📅 提醒日期选择

</td>
</tr>
</table>

---

## 🛠️ 技术栈

### 前端技术

<table>
<tr>
<th>技术</th>
<th>说明</th>
<th>版本</th>
</tr>
<tr>
<td>微信小程序</td>
<td>原生开发框架</td>
<td>Base Library 2.25.4+</td>
</tr>
<tr>
<td>WXML</td>
<td>微信小程序标记语言</td>
<td>-</td>
</tr>
<tr>
<td>WXSS</td>
<td>微信小程序样式语言（增强CSS）</td>
<td>-</td>
</tr>
<tr>
<td>JavaScript</td>
<td>业务逻辑实现</td>
<td>ES6+</td>
</tr>
<tr>
<td>WXS</td>
<td>微信小程序脚本（视图层脚本）</td>
<td>-</td>
</tr>
</table>

### 核心技术点

#### 1. 数据存储

```javascript
// 使用 wx.setStorageSync 本地存储
// 数据格式
{
  habits: [/* 习惯列表 */],
  records: {/* 打卡记录 */},
  goals: {/* 周目标 */},
  cats: [/* 分类列表 */],
  s: {/* 成就解锁状态 */},
  pomo: {/* 番茄钟数据 */}
}
```

**优势**：
- 🚀 无需服务器，打开即用
- 🔒 数据完全本地，隐私安全
- ⚡ 读写速度快，体验流畅
- 📱 跨设备需手动导出导入（后续版本支持云端同步）

#### 2. 火花值排序算法

```javascript
// 火花值 = 总打卡次数 + 连续天数 × 2
const spark = totalCheckIns + streak * 2

// 实时排序
list.sort((a, b) => b.spark - a.spark)
```

**排序触发时机**：
- 打卡/撤销打卡后
- 打开小程序时
- 切换筛选条件时

#### 3. 连续天数计算

```javascript
// 从今天往前数，遇到断签即停止
let streak = 0
let date = today
while (records[date] && records[date][habitId]) {
  streak++
  date = yesterday(date)
}
```

#### 4. 成就判定系统

```javascript
// 20项成就，每项有独立的判定函数
const ACHIEVEMENTS = [
  {
    id: 'a1',
    name: '初出茅庐',
    desc: '连续打卡7天',
    icon: '🔥',
    check(data) {
      return calcMaxStreak(data) >= 7
    }
  },
  // ... 共20项
]
```

**判定时机**：
- 打卡成功后
- 打开成就面板时
- 数据导入后

---

### 性能优化

#### 1. setData 优化

```javascript
// ❌ 错误：频繁调用 setData
this.setData({ habit1: newData1 })
this.setData({ habit2: newData2 })

// ✅ 正确：合并为一次调用
this.setData({
  habit1: newData1,
  habit2: newData2
})
```

#### 2. 数据字段精简

```javascript
// 只传递视图层需要的数据
this.setData({
  'filteredHabits[0]._checked': true,  // 精准更新
})
```

#### 3. 列表渲染优化

- 使用 `wx:key` 提升列表渲染性能
- 虚拟列表技术（超长列表场景）
- 分页加载（后续版本）

---

## 📦 安装部署

### 环境准备

1. **安装微信开发者工具**
   - 下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
   - 支持 Windows / macOS / Linux

2. **注册微信小程序账号**
   - 前往 https://mp.weixin.qq.com/
   - 完成实名认证
   - 获取 AppID（测试号可使用测试AppID）

### 部署步骤

#### 方法一：直接导入（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/habit-tracker.git

# 2. 打开微信开发者工具
# 选择"导入项目"
# 项目目录：选择克隆的 habit-tracker 文件夹
# AppID：输入你的小程序AppID（或使用测试号）
# 项目名称：火花习惯
```

#### 方法二：手动创建

```bash
# 1. 在微信开发者工具中创建新项目
# 2. 将本项目的文件复制到新项目目录
# 3. 编译运行
```

### 目录结构

```
habit-tracker/
├── app.js                      # 全局逻辑
├── app.json                    # 全局配置
├── app.wxss                    # 全局样式
├── project.config.json          # 项目配置
├── sitemap.json                # 搜索配置
├── utils/                      # 工具函数
│   ├── time.js                # 时间工具（日期计算、格式化）
│   └── achievements.js        # 成就系统（判定、解锁）
├── pages/                      # 页面
│   └── index/                # 首页（唯一页面，单页应用）
│       ├── index.js           # 页面逻辑
│       ├── index.json         # 页面配置
│       ├── index.wxml         # 页面结构
│       └── index.wxss        # 页面样式
└── README.md                  # 项目说明
```

---

## 📱 使用指南

### 快速上手

#### 第一步：添加习惯

1. 点击首页右上角 **"+"** 按钮
2. 输入习惯名称（如"晨跑"、"阅读"）
3. 选择分类（可选）
4. 设置难度星级（1-5星，可选）
5. 点击 **"添加"**

💡 **小贴士**：首次使用会提供习惯建议（如"晨跑"、"阅读30分钟"）

---

#### 第二步：每日打卡

1. 在首页找到要打卡的习惯
2. 点击习惯左侧的 **圆圈**
3. 圆圈变蓝 + 白色对勾 = 打卡成功 ✅
4. 再次点击可 **撤销打卡**

💡 **小贴士**：
- 打卡后火花值自动更新
- 高火花习惯会自动排在前面
- 撤销打卡会恢复之前的火花值

---

#### 第三步：设置周目标

1. 点击习惯卡片
2. 在弹出的详情面板中找到 **"周目标"**
3. 选择目标次数（3/5/7次）
4. 点击 **"保存"**

💡 **周目标规则**：
- 按自然周统计（周一至周日）
- 完成目标会弹出庆祝弹窗
- 未完成会显示加油文案

---

#### 第四步：查看成就

1. 点击首页右上角 **"🏆"** 按钮
2. 查看已解锁的成就
3. 点击成就可查看解锁条件
4. 继续努力解锁更多成就！

💡 **成就系统**：
- 共20项成就
- 成就解锁时会弹出庆祝弹窗
- 成就面板展示所有成就的解锁状态

---

### 高级功能

#### 分类管理

1. 点击首页右上角 **"⚙️"** 按钮
2. 选择 **"分类管理"**
3. 添加/删除分类
4. 返回首页，点击习惯卡片上的 **"🏷️"** 按钮快速设置分类

#### 番茄钟使用

1. 在首页顶部找到 **"番茄钟"** 组件
2. 设置专注时长（默认25分钟）
3. 点击 **"开始"**
4. 专注期间可暂停/继续
5. 时间到后会有提醒

#### 数据导出

1. 点击首页右上角 **"⚙️"** 按钮
2. 选择 **"导出数据"**
3. 数据会以JSON格式保存到手机
4. 可用于备份或迁移

---

## 🎨 UI设计

### 设计理念

**简约 · 优雅 · 高效**

- 🎨 **色彩体系**：蓝色主色调（#4A90D9），橙色火花色（#FF9800）
- 🔠 **字体系统**：系统字体，保证清晰度
- 📐 **间距规范**：8px基准网格，保证视觉节奏
- 🎭 **动画系统**：0.35s缓动动画，流畅不拖沓

### 界面预览

<table>
<tr>
<td width="25%">

**首页**
- 习惯列表
- 打卡操作
- 火花值展示

</td>
<td width="25%">

**详情面板**
- 习惯信息
- 周目标设定
- 难度调整

</td>
<td width="25%">

**成就面板**
- 成就列表
- 解锁状态
- 成就描述

</td>
<td width="25%">

**设置面板**
- 分类管理
- 外观设置
- 音效设置

</td>
</tr>
</table>

---

## 🔧 开发指南

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker

# 2. 打开微信开发者工具
# 导入项目目录

# 3. 编译运行
# 点击"编译"按钮

# 4. 真机调试
# 点击"预览"，用手机微信扫码
```

### 代码规范

#### JavaScript 规范

```javascript
// ✅ 使用驼峰命名
const habitName = '晨跑'

// ✅ 使用ES6+语法
const addHabit = (name) => {
  return { id: Date.now(), name }
}

// ✅ 异步操作使用Promise
const saveData = (data) => {
  return new Promise((resolve) => {
    wx.setStorageSync('data', data)
    resolve()
  })
}
```

#### WXML 规范

```xml
<!-- ✅ 使用双引号 -->
<view class="habit-item">

<!-- ✅ 属性按顺序：class > id > data- > bindtap -->
<view class="check" bindtap="toggleCheckin" data-id="{{item.id}}">

<!-- ✅ 使用 wx:if / wx:for 等指令 -->
<text wx:if="{{item._checked}}">✓</text>
```

#### WXSS 规范

```css
/* ✅ 使用类选择器 */
.habit-item {
  padding: 10px 14px;
}

/* ✅ 使用 rpx 适配不同屏幕 */
.check {
  width: 48rpx;
  height: 48rpx;
}

/* ✅ 使用 CSS 变量 */
:root {
  --primary: #4A90D9;
}
```

---

### 调试技巧

#### 1. 查看数据结构

```javascript
// 在控制台查看
console.log('当前数据：', app.globalData.data)
```

#### 2. 模拟打卡

```javascript
// 在控制台执行
app.globalData.data.records['2026-07-04']['habit1'] = true
```

#### 3. 重置数据

```javascript
// 在控制台执行
wx.clearStorageSync()
```

---

## 📊 项目结构详解

### 核心文件说明

#### `app.js` - 全局逻辑

```javascript
App({
  globalData: {
    data: {
      habits: [],    // 习惯列表
      records: {},    // 打卡记录
      goals: {},      // 周目标
      cats: [],       // 分类列表
      s: {},          // 成就解锁状态
      pomo: {},       // 番茄钟数据
      ap: {}          // 累计使用天数
    }
  },
  
  // 加载数据
  loadData() {
    this.globalData.data = wx.getStorageSync('habit-data') || defaultData
  },
  
  // 保存数据
  saveData(data) {
    wx.setStorageSync('habit-data', data)
  }
})
```

#### `utils/time.js` - 时间工具

**核心函数**：

| 函数名 | 功能 | 返回值 |
|--------|------|--------|
| `todayStr()` | 获取今天日期字符串 | `'2026-07-04'` |
| `dateStr(d)` | Date对象转字符串 | `'2026-07-04'` |
| `formatDate(d)` | 格式化日期 | `'7月4日（周六）'` |
| `getMonday(d)` | 获取本周一日期 | `Date对象` |
| `addDays(d, n)` | 日期加N天 | `Date对象` |
| `calcStreak()` | 计算连续天数 | `Number` |
| `countCheckIns()` | 统计打卡次数 | `Number` |

#### `utils/achievements.js` - 成就系统

**核心函数**：

| 函数名 | 功能 |
|--------|------|
| `checkAchievements(data)` | 检查并解锁成就 |
| `getAchievements(data)` | 获取所有成就列表 |

**成就判定示例**：

```javascript
// 连续打卡7天成就
{
  id: 'a1',
  nm: '初出茅庐',
  desc: '连续打卡7天',
  ic: '🔥',
  ck(data) {
    return calcMaxStreak(data) >= 7
  }
}
```

---

## 🤝 贡献指南

### 如何贡献

我们欢迎任何形式的贡献！

#### 1. 报告Bug

- 使用 GitHub Issues 报告Bug
- 详细描述复现步骤
- 附上截图/录屏（如有）

#### 2. 提出新功能

- 使用 GitHub Issues 提出功能建议
- 说明使用场景和价值
- 可提供设计草图（如有）

#### 3. 提交代码

```bash
# 1. Fork项目
# 2. 创建分支
git checkout -b feature/新功能名称

# 3. 提交代码
git commit -m "feat: 添加某某功能"

# 4. 推送分支
git push origin feature/新功能名称

# 5. 创建Pull Request
```

### 代码规范

- ✅ 使用 ESLint 检查代码
- ✅ 编写注释（复杂逻辑必须）
- ✅ 更新文档（功能变更必须）
- ✅ 测试通过（提交前必须）

---

## 📝 更新日志

### v1.0.0 (2026-07-04)

#### 新增功能
- ✅ 习惯添加、编辑、删除
- ✅ 一键打卡，支持撤销
- ✅ 火花值系统（自动计算 + 排序）
- ✅ 连续天数统计
- ✅ 周目标设定
- ✅ 成就系统（20项成就）
- ✅ 番茄钟专注计时
- ✅ 分类管理
- ✅ 难度星级设置
- ✅ 近7日打卡日历
- ✅ 周报生成
- ✅ 外观设置（浅色/深色）
- ✅ 音效设置
- ✅ 提醒设置

#### 优化
- ⚡ 提升页面渲染性能
- 🎨 优化UI细节
- 🐛 修复已知Bug

---

## 📄 开源协议

本项目采用 **MIT 协议** 开源。

```
MIT License

Copyright (c) 2026 火花习惯

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

---

## 🙏 致谢

### 开源项目

- 微信小程序官方文档
- Moment.js（时间处理思路参考）
- Apple Design Resources（UI设计参考）

### 灵感来源

- 《原子习惯》 - James Clear
- 《微习惯》 - Stephen Guise
- 番茄工作法 - Francesco Cirillo

---

## 📮 联系方式

- 💬 微信：your_wechat_id
- 📧 邮箱：your_email@example.com
- 🐛 问题反馈：https://github.com/yourusername/habit-tracker/issues

---

## ⭐ Star History

如果你觉得这个项目有用，请给我们一个Star！⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/habit-tracker&type=Date)](https://star-history.com/#yourusername/habit-tracker&Date)

---

<div align="center">

**🔥 让好习惯像火花一样绽放 🔥**

Made with ❤️ by [Your Name]

</div>
