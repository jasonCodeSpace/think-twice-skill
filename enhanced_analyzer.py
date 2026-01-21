#!/usr/bin/env python3
"""
Think-Twice: Enhanced Startup Idea Analyzer
基于失败创业案例数据库的批判性分析工具
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ========================================================================
# 配置区域 - 用户可以修改这些路径
# ========================================================================

DEFAULT_DATA_DIR = Path(__file__).parent
CLASSIFIED_FILE = DEFAULT_DATA_DIR / "data" / "startups_classified.json"
VECTORS_FILE = DEFAULT_DATA_DIR / "data" / "startups_vectors.json"


# ========================================================================
# 数据加载
# ========================================================================

def load_data(classified_path=CLASSIFIED_FILE, vectors_path=VECTORS_FILE):
    """加载创业公司数据和向量数据"""
    with open(classified_path, 'r', encoding='utf-8') as f:
        startups = json.load(f)

    with open(vectors_path, 'r', encoding='utf-8') as f:
        vectors_data = json.load(f)

    return startups, vectors_data


# 全局加载（懒加载）
_startups = None
_vectors_data = None
_id_to_startup = None
_id_to_vector = None
_all_ids = None
_embedding_matrix = None
_embed_model = None


def init():
    """初始化分析器"""
    global _startups, _vectors_data, _id_to_startup, _id_to_vector, _all_ids, _embedding_matrix, _embed_model

    if _startups is None:
        _startups, _vectors_data = load_data()
        _id_to_startup = {s['id']: s for s in _startups}
        _id_to_vector = {v['id']: v['embedding'] for v in _vectors_data}
        _all_ids = sorted(_id_to_vector.keys())
        _embedding_matrix = np.array([_id_to_vector[id] for id in _all_ids])
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    return _startups, _vectors_data


# ========================================================================
# 分析函数
# ========================================================================

def analyze_failure_path(startup):
    """深度分析一个失败案例的完整路径"""
    desc = startup.get('description', '')

    problem = ""
    solution = ""
    desc_lower = desc.lower()

    # 智能提取问题和解决方案
    for marker in ['solve the problem', 'address the problem', 'problem of',
                    'aimed to', 'sought to', 'designed to']:
        if marker in desc_lower:
            idx = desc_lower.find(marker)
            problem = desc[:idx].strip()
            rest = desc[idx + len(marker):].strip()
            solution = (marker + " " + rest.split('.')[0]).strip()
            break

    if not problem:
        problem = desc[:300]

    failure_mode = startup.get('difficulty_reason', '')
    scalability_issue = startup.get('scalability_reason', '')

    # 现状推断
    end_year = startup.get('end_year', 0)
    funding = startup.get('total_funding', 0)
    if end_year and end_year < 2025:
        if funding > 1_000_000:
            aftermath = f"已于{end_year}年倒闭，烧掉${funding/1_000_000:.1f}M融资后无疾而终"
        else:
            aftermath = f"已于{end_year}年倒闭，融资较少，未能验证商业模式"
    else:
        aftermath = "已停止运营"

    return {
        'problem': problem[:300],
        'solution': solution[:300] if solution else "详见完整描述",
        'failure_mode': failure_mode[:400],
        'scalability_issue': scalability_issue[:400],
        'aftermath': aftermath
    }


def comprehensive_analysis(idea: str, top_k: int = 10):
    """综合分析创业想法"""
    init()  # 确保数据已加载

    # 向量搜索
    query_embedding = _embed_model.encode(idea).reshape(1, -1)
    similarities = cosine_similarity(query_embedding, _embedding_matrix)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        startup_id = _all_ids[idx]
        startup = _id_to_startup.get(startup_id)
        if not startup:
            continue

        failure_path = analyze_failure_path(startup)

        results.append({
            'similarity': float(similarities[idx]),
            'startup': startup,
            'failure_path': failure_path
        })

    # 统计分析
    difficulties = [r['startup'].get('difficulty', 0) for r in results]
    scalabilities = [r['startup'].get('scalability', 0) for r in results]
    fundings = [r['startup'].get('total_funding', 0) for r in results]

    avg_difficulty = np.mean(difficulties)
    avg_scalability = np.mean(scalabilities)
    avg_funding = np.mean(fundings)

    # 计算评分
    difficulty_penalty = (avg_difficulty / 4) * 40
    scalability_penalty = ((4 - avg_scalability) / 4) * 30
    funding_pressure = min(avg_funding / 50_000_000 * 20, 20)
    feasibility_score = max(0, 100 - difficulty_penalty - scalability_penalty - funding_pressure)

    # 行业分布
    industries = {}
    for r in results:
        ind = r['startup'].get('primary_industry', 'Unknown')
        industries[ind] = industries.get(ind, 0) + 1

    main_industry = max(industries, key=industries.get) if industries else None

    return {
        'results': results,
        'score': feasibility_score,
        'stats': {
            'avg_difficulty': avg_difficulty,
            'avg_scalability': avg_scalability,
            'avg_funding': avg_funding,
            'difficulty_penalty': difficulty_penalty,
            'scalability_penalty': scalability_penalty,
            'funding_pressure': funding_pressure
        },
        'fundings': sorted(fundings),
        'industries': industries,
        'main_industry': main_industry
    }


# ========================================================================
# 命令行接口
# ========================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_analyzer.py '<your startup idea in English>'")
        print("\nExample:")
        print('  python enhanced_analyzer.py "Job search platform for MNC jobs in China"')
        sys.exit(1)

    idea = sys.argv[1]

    print("🔍 Analyzing startup idea...")
    analysis = comprehensive_analysis(idea, top_k=10)

    print(f"\n## 📊 可行性评分: {analysis['score']:.0f}/100")
    print(f"  - 难度: {analysis['stats']['avg_difficulty']:.1f}/4 → -{analysis['stats']['difficulty_penalty']:.0f}分")
    print(f"  - 可扩展性: {analysis['stats']['avg_scalability']:.1f}/4 → -{analysis['stats']['scalability_penalty']:.0f}分")
    print(f"  - 融资压力: ${analysis['stats']['avg_funding']:,.0f} → -{analysis['stats']['funding_pressure']:.0f}分")

    n = len(analysis['fundings'])
    print(f"\n## 💰 融资建议（基于{len(analysis['results'])}个相似案例）")
    print(f"  - 25分位: ${analysis['fundings'][n//4]:,.0f}")
    print(f"  - 中位数: ${analysis['fundings'][n//2]:,.0f}")
    print(f"  - 75分位: ${analysis['fundings'][n*3//4]:,.0f}")

    print(f"\n## 🏭 主要行业: {analysis['main_industry']}")

    print(f"\n## ⚠️ 相似失败案例详细分析")
    for i, r in enumerate(analysis['results'][:5], 1):
        s = r['startup']
        fp = r['failure_path']

        print(f"\n### {i}. {s['name']} ({r['similarity']:.1%})")
        print(f"**行业**: {s.get('primary_industry', 'N/A')} | **融资**: ${s.get('total_funding', 0):,} | **失败**: {s.get('end_year', 'N/A')}")
        print(f"\n**🎯 要解决的问题**:")
        print(f"  {fp['problem']}")
        print(f"\n**💡 解决方案**:")
        print(f"  {fp['solution']}")
        print(f"\n**❌ 失败原因**:")
        print(f"  {fp['failure_mode'][:200]}...")
        print(f"\n**📈 可扩展性问题**:")
        print(f"  {fp['scalability_issue'][:200]}...")
        print(f"\n**💀 现状**:")
        print(f"  {fp['aftermath']}")
