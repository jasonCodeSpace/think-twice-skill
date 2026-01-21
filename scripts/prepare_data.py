#!/usr/bin/env python3
"""
Think-Twice 数据准备脚本

从 Loot Drop 或其他来源获取失败创业案例数据，并生成:
1. startups_classified.json - 带分类标注的创业公司数据
2. startups_vectors.json - 用于语义搜索的向量嵌入

数据来源: https://www.loot-drop.io/
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    sys.exit(1)


# ========================================================================
# 配置
# ========================================================================

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
CLASSIFIED_FILE = DATA_DIR / "startups_classified.json"
VECTORS_FILE = DATA_DIR / "startups_vectors.json"
MODEL_NAME = 'all-MiniLM-L6-v2'


# ========================================================================
# 数据分类函数
# ========================================================================

def classify_difficulty(startup: Dict[str, Any]) -> int:
    """
    根据公司描述和融资情况评估难度 (1-4)
    1 = 简单, 4 = 极难
    """
    desc = startup.get('description', '').lower()
    funding = startup.get('total_funding', 0)

    # 高难度指标
    hard_keywords = ['marketplace', 'platform', 'network', 'two-sided',
                     'social network', 'peer-to-peer', 'gig economy',
                     'vertical integration', 'infrastructure']
    # 中等难度
    medium_keywords = ['saas', 'subscription', 'enterprise', 'b2b']

    score = 2  # 默认中等难度

    for kw in hard_keywords:
        if kw in desc:
            score = 4
            break

    if score < 3:
        for kw in medium_keywords:
            if kw in desc:
                score = 3
                break

    # 融资超过 100M 的项目通常更复杂
    if funding > 100_000_000 and score < 4:
        score = min(score + 1, 4)

    return score


def classify_scalability(startup: Dict[str, Any]) -> int:
    """
    评估可扩展性 (1-4)
    1 = 难扩展, 4 = 易扩展
    """
    desc = startup.get('description', '').lower()

    # 高可扩展性
    scalable_keywords = ['saas', 'software', 'platform', 'digital',
                        'online', 'subscription', 'api', 'cloud']
    # 低可扩展性
    not_scalable_keywords = ['hardware', 'manufacturing', 'physical',
                            'logistics', 'delivery', 'on-demand',
                            'services', 'consulting']

    score = 2  # 默认

    for kw in scalable_keywords:
        if kw in desc:
            score += 1

    for kw in not_scalable_keywords:
        if kw in desc:
            score -= 1

    # 同时出现高扩展和低扩展关键词，取中间值
    if 'software' in desc and 'hardware' in desc:
        score = 2

    return max(1, min(4, score))


def classify_market_potential(startup: Dict[str, Any]) -> str:
    """
    评估市场潜力: high, medium, low
    """
    desc = startup.get('description', '').lower()

    # 高潜力市场
    high_markets = ['enterprise', 'developer', 'fintech', 'healthcare',
                   'education', 'logistics']
    # 低潜力/饱和市场
    low_markets = ['social network', 'messaging', 'dating',
                  'productivity app', 'consumer app']

    for market in low_markets:
        if market in desc:
            return 'low'

    for market in high_markets:
        if market in desc:
            return 'high'

    return 'medium'


def classify_industry(startup: Dict[str, Any]) -> str:
    """
    分类主要行业
    """
    desc = startup.get('description', '').lower()
    sector = startup.get('sector', '').lower()

    industry_map = {
        'saas': 'SaaS',
        'ecommerce': 'E-commerce',
        'fintech': 'Fintech',
        'healthtech': 'HealthTech',
        'edtech': 'EdTech',
        'consumer': 'Consumer',
        'real estate': 'Real Estate',
        'logistics': 'Logistics & Supply Chain',
        'transportation': 'Transportation',
        'hardware': 'Hardware & IoT',
        'cleantech': 'CleanTech & Energy',
        'food': 'Food & Beverage',
        'cybersecurity': 'Cybersecurity',
        'developer tools': 'Developer Tools',
        'hr tech': 'HR Tech',
        'marketing': 'Marketing & AdTech',
        'communication': 'Communication & Collaboration',
        'data': 'Data & Analytics',
        'media': 'Media & Entertainment',
    }

    for key, value in industry_map.items():
        if key in desc or key in sector:
            return value

    return 'Other'


def enrich_startup(startup: Dict[str, Any]) -> Dict[str, Any]:
    """添加分类字段到创业公司数据"""
    difficulty = classify_difficulty(startup)
    scalability = classify_scalability(startup)

    startup['difficulty'] = difficulty
    startup['scalability'] = scalability
    startup['market_potential'] = classify_market_potential(startup)
    startup['primary_industry'] = classify_industry(startup)

    # 添加原因说明
    startup['difficulty_reason'] = generate_reason(startup, 'difficulty')
    startup['scalability_reason'] = generate_reason(startup, 'scalability')
    startup['market_potential_reason'] = generate_reason(startup, 'market')

    return startup


def generate_reason(startup: Dict[str, Any], field: str) -> str:
    """生成分类原因说明"""
    desc = startup.get('description', '')
    funding = startup.get('total_funding', 0)
    sector = startup.get('sector', '')

    if field == 'difficulty':
        if startup['difficulty'] >= 4:
            return f"High complexity due to {sector} model requiring significant coordination and capital. Raised ${funding:,.0f} indicating execution challenges."
        elif startup['difficulty'] <= 2:
            return f"Moderate complexity with clear value proposition in {sector}."
        else:
            return f"Medium complexity with standard challenges in {sector} sector."

    elif field == 'scalability':
        if startup['scalability'] >= 4:
            return "Highly scalable software/model with low marginal costs and strong network effects potential."
        elif startup['scalability'] <= 2:
            return "Limited by physical operations, high marginal costs, or operational complexity."
        else:
            return "Moderate scalability with some operational constraints."

    else:  # market
        if startup['market_potential'] == 'high':
            return f"Large addressable market in {startup['primary_industry']} with clear pain points."
        elif startup['market_potential'] == 'low':
            return "Crowded market with dominant players or niche appeal."
        else:
            return f"Moderate market opportunity in {startup['primary_industry']}."


# ========================================================================
# 向量生成
# ========================================================================

def generate_embeddings(startups: List[Dict[str, Any]],
                       model_name: str = MODEL_NAME) -> List[Dict[str, Any]]:
    """
    为创业公司生成向量嵌入

    Returns:
        List of {'id': int, 'name': str, 'embedding': List[float]}
    """
    print(f"📦 加载模型: {model_name}")
    model = SentenceTransformer(model_name)

    print(f"🔄 生成 {len(startups)} 个向量嵌入...")

    # 组合公司名称和描述作为文本源
    texts = []
    for s in startups:
        name = s.get('name', '')
        desc = s.get('description', '')[:500]  # 限制长度
        sector = s.get('sector', '')
        texts.append(f"{name}. {desc}. Sector: {sector}")

    embeddings = model.encode(texts, show_progress_bar=True)

    vectors = []
    for s, emb in zip(startups, embeddings):
        vectors.append({
            'id': s['id'],
            'name': s['name'],
            'embedding': emb.tolist()  # 转为列表以便 JSON 序列化
        })

    return vectors


# ========================================================================
# 主函数
# ========================================================================

def load_raw_data(filepath: Path) -> List[Dict[str, Any]]:
    """加载原始数据文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(startups: List[Dict[str, Any]],
              vectors: List[Dict[str, Any]]):
    """保存处理后的数据"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"💾 保存分类数据到: {CLASSIFIED_FILE}")
    with open(CLASSIFIED_FILE, 'w', encoding='utf-8') as f:
        json.dump(startups, f, ensure_ascii=False, indent=2)

    print(f"💾 保存向量数据到: {VECTORS_FILE}")
    with open(VECTORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(vectors, f, ensure_ascii=False, indent=2)


def process_from_classified():
    """
    从已有的 classified 文件重新生成向量
    当只更新向量模型时使用
    """
    print("📂 加载已有分类数据...")
    startups = load_raw_data(CLASSIFIED_FILE)
    print(f"   找到 {len(startups)} 条记录")

    vectors = generate_embeddings(startups)
    save_data(startups, vectors)

    print(f"✅ 完成!")
    print(f"   - 分类数据: {len(startups)} 条")
    print(f"   - 向量数据: {len(vectors)} 条")
    print(f"   - 向量维度: {len(vectors[0]['embedding'])}")


def process_from_raw(raw_filepath: Path):
    """
    从原始 Loot Drop 数据处理
    原始数据格式需要包含: id, name, description, sector, end_year, total_funding
    """
    print("📂 加载原始数据...")
    raw_startups = load_raw_data(raw_filepath)
    print(f"   找到 {len(raw_startups)} 条记录")

    print("🔄 分类处理...")
    startups = [enrich_startup(s) for s in raw_startups]

    print("🔄 生成向量嵌入...")
    vectors = generate_embeddings(startups)

    save_data(startups, vectors)

    print(f"✅ 完成!")
    print(f"   - 分类数据: {len(startups)} 条")
    print(f"   - 向量数据: {len(vectors)} 条")


# ========================================================================
# 命令行接口
# ========================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='准备 Think-Twice 数据文件')
    parser.add_argument('--raw', type=str,
                       help='原始 JSON 数据文件路径 (Loot Drop 导出)')
    parser.add_argument('--regenerate-vectors', action='store_true',
                       help='从已有 classified 文件重新生成向量')

    args = parser.parse_args()

    if args.regenerate_vectors:
        process_from_classified()
    elif args.raw:
        process_from_raw(Path(args.raw))
    else:
        print("使用方法:")
        print("  1. 从原始数据生成:")
        print("     python scripts/prepare_data.py --raw path/to/raw_data.json")
        print()
        print("  2. 重新生成向量 (使用已有 classified 文件):")
        print("     python scripts/prepare_data.py --regenerate-vectors")
        print()
        print("数据来源: https://www.loot-drop.io/")
        print()
        print("原始数据格式要求:")
        print("  [")
        print("    {")
        print('      "id": 1,')
        print('      "name": "Company Name",')
        print('      "description": "What the company did...",')
        print('      "sector": "saas",')
        print('      "end_year": 2023,')
        print('      "total_funding": 1000000')
        print("    },")
        print("    ...")
        print("  ]")


if __name__ == "__main__":
    main()
