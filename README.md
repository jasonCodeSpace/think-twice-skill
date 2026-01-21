# Think-Twice

> 基于 920+ 失败创业案例数据库，用批判性思维分析你的创业想法

Think-Twice 是一个 Claude Code skill，通过分析历史上的失败创业案例，为你的创业想法提供可行性评分、风险警示和改进建议。

## 功能

- 📊 **可行性评分** (0-100) - 基于相似失败案例的数据驱动评分
- ⚠️ **相似失败案例** - 找到历史上最相似的失败案例
- 🎯 **问题分析** - 每个案例要解决的问题、解决方案、失败路径、现状
- 💰 **融资建议** - 基于历史数据的 25/50/75 分位融资建议
- 🧠 **批判性思维** - 5 个必须质疑的硬核问题

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/think-twice.git
cd think-twice
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 下载模型（首次运行自动下载）

首次运行会自动下载 `all-MiniLM-L6-v2` 模型 (~80MB)

### 4. 安装到 Claude Code

```bash
# 方式1: 复制到全局技能目录
cp -r skill/ ~/.claude/skills/Think-twice

# 方式2: 复制到项目技能目录
cp -r skill/ .claude/skills/Think-twice
```

## 使用

在 Claude Code 中输入：

```
/Think-twice
```

然后描述你的创业想法：

```
我想做一个 AI 驱动的 HR SaaS 平台，帮助企业自动化招聘流程...
```

## 示例输出

```
## 📊 可行性评分: 46/100
  - 难度: 3.2/4 → -32分
  - 可扩展性: 2.3/4 → -13分
  - 融资压力: $22,132,000 → -9分

## 💰 融资建议（基于10个相似案例）
  - 25分位: $2,000,000
  - 中位数: $5,000,000
  - 75分位: $27,800,000

## 🏭 主要行业: HR Tech

## ⚠️ 相似失败案例详细分析

### 1. Jobr (43.9%)
**行业**: HR Tech | **融资**: $2,000,000 | **失败**: 2019

🎯 要解决的问题:
  Jobr was an on-demand job marketplace that...

💡 解决方案:
  aimed to revolutionize the recruitment process...

❌ 失败原因:
  依赖网络效应，双边市场难以启动...

💀 现状:
  已于2019年倒闭，烧掉$2.0M融资后无疾而终
```

## 数据来源

基于 [Loot Drop](https://www.loot-drop.io/) 的 920+ 失败创业案例数据库。

## 行业分类

20 个一级分类：
- SaaS, E-commerce, Fintech, HealthTech, EdTech
- Media & Entertainment, Consumer, Real Estate
- Logistics & Supply Chain, Transportation, Hardware & IoT
- CleanTech & Energy, Food & Beverage, Cybersecurity
- Developer Tools, HR Tech, Marketing & AdTech
- Communication & Collaboration, Data & Analytics, AI & Machine Learning

## 批判性思维检查清单

1. ❓ 伪需求 vs 真实痛点？
2. ❓ 付费意愿验证了吗？
3. ❓ 双边市场冷启动？
4. ❓ 竞争对手可复制性？
5. ❓ Final Boss 是谁？

## 许可证

MIT License
