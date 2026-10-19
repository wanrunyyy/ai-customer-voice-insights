"""Prepare a balanced diagnostic review sample and full-dataset baseline stats.

Run from any directory: python scripts/prepare_data.py
Data source: Kaggle Women's E-Commerce Clothing Reviews (CC0).
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RAW = DATA / 'raw' / 'Womens Clothing E-Commerce Reviews.csv'
SEED = 20261019
PER_GROUP = 100


def main():
    if not RAW.exists():
        raise SystemExit(
            f'缺少原始数据: {RAW}\n请从 Kaggle 下载 Womens Clothing E-Commerce Reviews.csv 放入 data/raw/。'
        )
    source = pd.read_csv(RAW, encoding='utf-8-sig', low_memory=False)
    required = {'Review Text', 'Rating', 'Department Name'}
    absent = required - set(source.columns)
    if absent:
        raise SystemExit(f'文件列名不符合数据集预期，缺少：{sorted(absent)}')
    source = source.copy()
    source['Review Text'] = source['Review Text'].fillna('').astype(str).str.strip()
    source['Rating'] = pd.to_numeric(source['Rating'], errors='coerce')
    source = source[(source['Review Text'].str.len() >= 15) & source['Rating'].between(1, 5)]
    source = source.drop_duplicates(subset=['Review Text']).copy()
    source['Rating'] = source['Rating'].astype(int)
    source['Department Name'] = source['Department Name'].fillna('Unspecified').astype(str)
    lower = source[source['Rating'] <= 3]
    higher = source[source['Rating'] >= 4]
    if len(lower) < PER_GROUP or len(higher) < PER_GROUP:
        raise SystemExit(f'有效低评分 {len(lower)}，高评分 {len(higher)}，不足以各取{PER_GROUP}条。')

    # Diagnostic sample intentionally 50/50 to find both pain points and strengths.
    sample = pd.concat([
        lower.sample(n=PER_GROUP, random_state=SEED),
        higher.sample(n=PER_GROUP, random_state=SEED),
    ], ignore_index=True).sample(frac=1, random_state=SEED + 1).reset_index(drop=True)
    sample.insert(0, 'review_id', [f'R{i:04d}' for i in range(1, len(sample)+1)])
    column_map = {
        'Review Text': 'review_text',
        'Rating': 'rating',
        'Department Name': 'department_name',
        'Class Name': 'class_name',
        'Recommended IND': 'recommended_ind',
    }
    sample = sample.rename(columns=column_map)
    keep = ['review_id', 'rating', 'department_name', 'review_text']
    for extra in ['class_name', 'recommended_ind']:
        if extra in sample.columns:
            keep.insert(-1, extra)
    sample[keep].to_csv(DATA/'analysis_base.csv', index=False, encoding='utf-8-sig')
    sample[['review_id','rating','department_name','review_text']].to_csv(
        DATA/'ai_input.csv', index=False, encoding='utf-8-sig')

    mean_rating = float(source['Rating'].mean())
    n_lower = int((source['Rating'] <= 3).sum())
    dist = source['Rating'].value_counts().sort_index().to_dict()
    full_summary = {
        'source': 'Kaggle nicapotato/womens-ecommerce-clothing-reviews (CC0)',
        'n_original_rows': int(len(pd.read_csv(RAW, usecols=['Rating']))),
        'n_clean_unique_reviews': int(len(source)),
        'n_lower_rating': n_lower,
        'lower_rating_share': n_lower / len(source),
        'mean_rating': round(mean_rating, 4),
        'rating_distribution': {str(k): int(v) for k,v in dist.items()},
        'ai_diagnostic_sample_size': int(len(sample)),
        'sampling': '100 reviews rating<=3 and 100 reviews rating>=4 (not representative)',
        'seed': SEED,
    }
    (DATA/'full_summary.json').write_text(
        json.dumps(full_summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'准备完成：原始 {full_summary["n_original_rows"]} 行；清洗去重后 {len(source)} 条。')
    print(f'真实总体（清洗后）：平均 {mean_rating:.2f} 星，低评分占比 {n_lower/len(source):.1%}。')
    print('已生成 data/ai_input.csv（200条）与 data/analysis_base.csv。')
    print('下一步：按 prompts/01_ai_classification.md 使用 ChatGPT 生成 data/ai_labels.csv。')

if __name__ == '__main__':
    main()
