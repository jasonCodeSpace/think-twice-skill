---
name: Think-twice
description: 基于920+失败创业案例数据库，分析���业想法的可行性，提供评分、失败案例参考和批判性建议
---

# Think-Twice - Startup Idea Analyzer (Critical Thinking Edition)

基于 920+ 个失败创业案例数据库，为创业想法提供**批判性**可行性分析。

## 工作流程

### 1. 收集创业想法
如果用户未提供完整信息，询问：
- 产品/服务描述（解决什么问题？）
- 目标市场（B2B/B2C？）
- 商业模式（如何盈利？）

### 2. 增强版分析（使用 enhanced_analyzer.py）

用户想法翻译成英文后执行：

```python
from enhanced_analyzer import comprehensive_analysis

analysis = comprehensive_analysis(idea, top_k=10)

# 输出评分、融资建议、详细案例分析
```

### 3. 批判性分析

**必须质疑的问题**：
1. ❓ 真实问题 vs 伪需求？
2. ❓ 付费意愿验证了吗？
3. ❓ 双边市场冷启动？
4. ❓ 竞争对手可复制性？
5. ❓ Final Boss 是谁？
