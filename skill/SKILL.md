---
name: Think-twice
description: 基于920+失败创业案例数据库，分析创业想法的可行性，提供评分、失败案例参考和批判性建议
---

# Think-Twice - 创业想法批判性分析

基于 920+ 个真实失败创业案例，用批判性思维分析创业想法的可行性。

## 工作流程

### 1. 收集创业想法
如果用户未提供完整信息，询问：
- 产品/服务描述（解决什么问题？）
- 目标市场（B2B/B2C？）
- 商业模式（如何盈利？）

### 2. 运行分析（静默）

将用户想法翻译成英文，然后静默运行分析：

```bash
# 自动检测项目目录（SKILL.md 所在位置的父目录）
PROJECT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${0}")")/.." && pwd)"
cd "$PROJECT_DIR" && source venv/bin/activate && python -c "
import json
from enhanced_analyzer import comprehensive_analysis
idea = '''{用户想法英文}'''
result = comprehensive_analysis(idea, top_k=10)
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

获取 JSON 结果后，用自然语言呈现给用户。

### 3. 结果呈现格式

用自然语言报告以下内容：

**📊 可行性评分**: X/100
- 难度分析：XX/4，扣XX分
- 可扩展性：XX/4，扣XX分
- 融资压力：XX百万，扣XX分

**💰 融资建议**（基于X个相似案例）
- 建议范围：$X - $X

**🏭 行业分析**
- 主要行业：XXX

**⚠️ 相似失败案例**

1. **[公司名]** (相似度XX%)
   - 行业：XXX | 融资：$X | 失败年份：XXXX
   - 要解决的问题：XXX
   - 解决方案：XXX
   - 失败原因：XXX
   - 可扩展性问题：XXX
   - 最终结果：XXX

[列出3-5个最相似的案例]

### 4. 批判性追问

基于分析结果，提出5个关键问题：
1. ❓ 这个问题真实存在吗？还是伪需求？
2. ❓ 用户愿意为此付费吗？有什么验证？
3. ❓ 是否有冷启动问题？（尤其是双边市场）
4. ❓ 大厂可以轻易复制吗？护城河在哪？
5. ❓ 谁是你的Final Boss？你会怎么被碾压？
