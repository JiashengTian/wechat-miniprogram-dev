#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 index.wxss 和 index.js 的语法错误"""

import os

BASE = r"C:\Users\tjs88\WorkBuddy\2026-07-04-10-18-01\habit\pages\index"

# ===== 修复 WXSS =====
wxss_path = os.path.join(BASE, "index.wxss")
with open(wxss_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到第53行附近的问题：第52行是 min-height: 80px;，第53-55行有垃圾代码
# 正确第50-55行应该是：
# .topbar {
#   padding: 18px 90px 20px 14px;
#   min-height: 80px;
# }
print(f"WXSS 总行数: {len(lines)}")
print(f"第50-56行内容:")
for i in range(49, min(56, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")

# 第52行是 `min-height: 80px;`，第53行开始有垃圾
# 正确做法：第50行 `.topbar {`，第51行 `padding: ...`，第52行 `min-height: 80px;`，第53行 `}`
# 所以删除第53-55行（索引52, 53, 54）
if len(lines) >= 55:
    # 检查第52行（0-indexed=51）是否是 min-height: 80px;
    if 'min-height: 80px' in lines[51] and 'min-height: 80px' in lines[52]:
        # 有重复，删除第53-55行（0-indexed: 52, 53, 54）
        del lines[52:55]
        print("✅ 已删除 WXSS 第53-55行垃圾代码")
        
        # 确保第50-53行是正确的
        # .topbar {  (索引49)
        #   padding: ... (索引50)
        #   min-height: 80px; (索引51)
        # } (索引52)
        if lines[52].strip() != '}':
            lines.insert(52, '}\n')
            print("✅ 已添加缺失的 }")

with open(wxss_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("✅ WXSS 修复完成")

# ===== 修复 JS =====
js_path = os.path.join(BASE, "index.js")
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到问题区域：deleteCategory 函数结尾被破坏
# 正确结构：
#   deleteCategory(e) { ... wx.showModal({ ... success: function(res) { ... }.bind(this) }) },
#   closeAllDonePopup() { ... },

# 当前错误代码：
#   },,,)
#       }, 2000)
#     }
#   },
#
#   // ===== 成就弹窗 =====)
#   },

# 修复方法：删除垃圾代码，重新写入正确代码
old_bad = """  },,,)
      }, 2000)
    }
  },

  // ===== 成就弹窗 =====)
  },"""

new_fixed = """  }),

  // ===== 成就弹窗 =====
  closeAllDonePopup() {
    this.setData({ showAllDonePopup: false })
  },"""

if old_bad in content:
    content = content.replace(old_bad, new_fixed)
    print("✅ 已修复 JS deleteCategory 结尾 + 添加 closeAllDonePopup")
else:
    # 尝试模糊匹配
    import re
    # 匹配 },,,) 后面的垃圾代码
    pattern = r'\s*\}\s*,,,\)\s*\},?\s*\d+\s*\)\s*\}\s*\},?\s*//.*===== 成就弹窗 =====\)\s*\},?'
    match = re.search(pattern, content)
    if match:
        content = content[:match.start()] + '\n  }),\n\n  // ===== 成就弹窗 =====\n  closeAllDonePopup() {\n    this.setData({ showAllDonePopup: false })\n  },'
        print("✅ 已用正则修复 JS")
    else:
        print("⚠️ 无法匹配垃圾代码，手动修复...")
        # 找到 deleteCategory 函数的正确结尾
        # 在第1127行是 })
        # 我们需要删除第1128-1134行
        lines = content.split('\n')
        # 找到包含 },,,) 的行
        for i, line in enumerate(lines):
            if '},,,)' in line:
                print(f"  找到垃圾代码在第 {i+1} 行: {line.strip()}")
                # 删除这一行和后面6行
                del lines[i:i+7]
                # 在第i行插入正确的结尾
                lines.insert(i, '  }),')
                lines.insert(i+1, '')
                lines.insert(i+2, '  // ===== 成就弹窗 =====')
                lines.insert(i+3, '  closeAllDonePopup() {')
                lines.insert(i+4, '    this.setData({ showAllDonePopup: false })')
                lines.insert(i+5, '  },')
                content = '\n'.join(lines)
                print("✅ 已手动修复 JS")
                break

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证修复
print("\n" + "="*50)
print("验证修复结果:")

# 检查JS语法
with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()
    
# 检查是否有 },,,) 
if '},,,)' in js_content:
    print("❌ JS 仍有 },,,)")
else:
    print("✅ JS 无 },,,)")
    
# 检查 closeAllDonePopup 是否存在
if 'closeAllDonePopup' in js_content:
    print("✅ closeAllDonePopup 函数存在")
    
# 检查 WXSS
with open(wxss_path, 'r', encoding='utf-8') as f:
    wxss_content = f.read()
    
# 检查是否有重复的 min-height
import re
matches = re.findall(r'min-height:\s*80px', wxss_content)
if len(matches) > 1:
    print(f"⚠️  WXSS 有 {len(matches)} 个 min-height: 80px")
else:
    print("✅ WXSS min-height 正常")

print("\n🎉 修复完成！请重新编译。")
