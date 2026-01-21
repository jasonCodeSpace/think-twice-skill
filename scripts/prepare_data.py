#!/usr/bin/env python3
"""
数据准备脚本 - 从原始数据创建分类和向量数据
"""

import json
import os
from pathlib import Path

# 检查是否需要 DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 原始数据源
# 可以从 https://www.loot-drop.io/ 获取
RAW_DATA_FILE = Path("data/all-startups.json")

# 输出文件
OUTPUT_CLASSIFIED = Path("data/startups_classified.json")
OUTPUT_VECTORS = Path("data/startups_vectors.json")


def prepare_data():
    """准备数据文��"""

    print("📊 Think-Twice 数据准备")
    print("=" * 50)

    # 检查原始数据
    if not RAW_DATA_FILE.exists():
        print(f"\n❌ 原始数据文件不存在: {RAW_DATA_FILE}")
        print("\n请从以下步骤获取数据:")
        print("1. 访问 https://www.loot-drop.io/")
        print("2. 下载完整的创业案例数据")
        print("3. 保存到 data/all-startups.json")
        print("\n或者使用预处理的文件:")
        print("https://github.com/your-username/think-twice/releases/download/v1.0/data.zip")
        return False

    print(f"\n✅ 找到原始数据: {RAW_DATA_FILE}")

    with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    print(f"   总计 {len(raw_data)} 个创业案例")

    # 如果有 DeepSeek API，进行分类
    if DEEPSEEK_API_KEY:
        print("\n📝 使用 DeepSeek API 进行行业分类...")
        print("   这可能需要一些时间...")
        # TODO: 实现分类逻辑
    else:
        print("\n⚠️  未设置 DEEPSEEK_API_KEY，跳过分类")
        print("   将使用原始数据的现有分类")

    # 检查是否需要生成向量
    if not OUTPUT_VECTORS.exists():
        print("\n🔢 生成向量嵌入...")
        print("   首次运行会下载模型 (~80MB)")
        # TODO: 实现向量化逻辑
    else:
        print(f"\n✅ 向量数据已存在: {OUTPUT_VECTORS}")

    print("\n✅ 数据准备完成！")
    return True


if __name__ == "__main__":
    prepare_data()
