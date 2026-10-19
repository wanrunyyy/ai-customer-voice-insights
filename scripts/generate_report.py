"""Generate evidence-based summary and empirical human-audit agreement metrics."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data'
OUTPUT = ROOT/'outputs'

SUGGESTIONS = {
    '尺码与版型': ('产品：优化尺码指引并测试推荐尺码功能', '运营：上线换码指导/FAQ', '市场：补充真实试穿与版型说明'),
    '面料与质量': ('产品：归纳面料质量异常并建立质检清单', '运营：优化材质说明与售后话术', '市场：强调可核实的材质与洗护信息'),
    '款式与外观': ('产品：校验实物与商品展示的一致性', '运营：收集穿搭场景和图片反馈', '市场：测试场景化展示素材'),
    '价格与价值感': ('产品：明确目标价位与价值定位', '运营：梳理常见价格疑虑', '市场：测试价值卖点而非单纯促销'),
    '物流与服务': ('产品：定位售后流程可用性问题', '运营：检查配送通知与咨询流程', '市场：避免未经验证的时效承诺'),
    '其他': ('产品：手工复核样本并优化主题体系', '运营：建立新问题登记流程', '市场：暂不根据该类做宣传结论'),
}

def audit():
    check_path = DATA/'manual_check.csv'
    if not check_path.exists():
        return None
    a = pd.read_csv(check_path,dtype=str).fillna('')
    both = a[(a.manual_sentiment.str.strip()!='') & (a.manual_topic.str.strip()!='')]
    if both.empty:
        return None
    return {
        'n_human_checked': len(both),
        'sentiment_agreement': float((both.ai_sentiment.str.strip()==both.manual_sentiment.str.strip()).mean()),
        'topic_agreement': float((both.ai_topic.str.strip()==both.manual_topic.str.strip()).mean()),
        'note': 'simple agreement (accuracy) on human-checked diagnostic subset; not a population estimate'
    }

def main():
    path = DATA/'enriched_reviews.csv'
    if not path.exists():
        raise SystemExit('先运行 python scripts/validate_labels.py，生成 enriched_reviews.csv。')
    df = pd.read_csv(path).fillna('')
    stats = json.loads((DATA/'full_summary.json').read_text(encoding='utf-8'))
    OUTPUT.mkdir(exist_ok=True)
    issues = df[df.sentiment.isin(['负面','中性/混合'])].copy()
    topics = issues['topic'].value_counts().rename_axis('topic').reset_index(name='count_in_diagnostic_sample')
    topics.to_csv(OUTPUT/'topic_counts.csv',index=False,encoding='utf-8-sig')
    crosstab = pd.crosstab(issues.department_name,issues.topic)
    crosstab.to_csv(OUTPUT/'department_topics.csv',encoding='utf-8-sig')
    verified = audit()
    if verified is not None:
        (OUTPUT/'manual_audit_metrics.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2),encoding='utf-8')
    result = [
        '# AI 用户反馈洞察报告（自动生成初稿）',
        '',
        '> 数据集：Kaggle Women’s E-Commerce Clothing Reviews；历史匿名化服装电商评论，非腾讯或当前平台数据。',
        '> 分析说明：完整数据集计算评分基线；AI样本按低/高评分各100条定向抽样，样本主题比例和情绪比例不可代表总体。',
        '',
        '## 一、基础规模与评分（清洗去重后的完整数据）',
        f'- 原始数据行数：{stats["n_original_rows"]:,}',
        f'- 有效非重复评论：{stats["n_clean_unique_reviews"]:,}',
        f'- 平均星级：{stats["mean_rating"]:.2f}/5',
        f'- 低评分（1–3星）占比：{stats["lower_rating_share"]:.1%}',
        '',
        '## 二、AI定向样本洞察（不推断总体分布）',
        f'- AI分析样本：{len(df)}条',
        f'- AI判定为负面/中性混合：{len(issues)}条',
        '',
        '| 主题 | 负面/中性混合评论数 |',
        '|---|---:|',
    ]
    for row in topics.itertuples(index=False):
        result.append(f'| {row.topic} | {row.count_in_diagnostic_sample} |')
    result.extend(['', '## 三、建议验证的业务行动（假设，尚未产生业务收益）', ''])
    for topic in topics.head(3)['topic'].tolist():
        result.append(f'### {topic}')
        for proposal in SUGGESTIONS.get(topic, SUGGESTIONS['其他']):
            result.append(f'- {proposal}')
        evidence = issues[issues.topic==topic].head(2)
        for r in evidence.itertuples():
            excerpt = str(r.review_text).replace('\n',' ').strip()
            result.append(f'- 对应证据 {r.review_id}（{r.rating}星）：“{excerpt[:200]}”')
        result.append('')
    result.extend(['## 四、人工复核', ''])
    if verified:
        result.extend([
            f'- 有效人工复核：{verified["n_human_checked"]}条',
            f'- 情绪标签一致率：{verified["sentiment_agreement"]:.1%}',
            f'- 主题标签一致率：{verified["topic_agreement"]:.1%}',
            '- 这些指标仅衡量该人工复核样本中的一致率，不等于模型总体准确率。',
        ])
    else:
        result.append('- 尚未填写 data/manual_check.csv 的 manual_* 列。完成复核后重新运行本程序。')
    result.extend([
        '', '## 五、下一步小规模业务验证',
        '- 产品：针对最高频痛点提出一个具体改版假设，用可用性测试评估。',
        '- 运营：优化对应FAQ或售后流程，用咨询解决率、重复咨询率等指标检验。',
        '- 市场：围绕真实正面评价提炼2版素材，用小规模A/B测试评估点击/转化。',
        '- 当前项目为探索性分析，没有真实A/B实验、转化增长或效率提升的实测结果，不可写成已实现。',
        '', '## 六、方法局限',
        '- 数据为历史英文服装电商评论，不可直接代表中国互联网产品用户。',
        '- LLM对含糊或多主题评价会误判；单标签方案会丢失次要主题。',
        '- 评分基线经过非空文本和重复评论过滤，可能不同于原始全体记录。',
        '- 文本主题分析基于非随机定向样本，仅用于发现问题与形成假设。',
    ])
    (OUTPUT/'summary.md').write_text('\n'.join(result)+'\n',encoding='utf-8')
    print('已生成 outputs/summary.md, topic_counts.csv, department_topics.csv。')
    if verified:
        print('人工复核：',verified)

if __name__=='__main__':
    main()
