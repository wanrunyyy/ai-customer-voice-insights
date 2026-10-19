"""Validate AI labels strictly, then merge with review evidence and create human audit sheet."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SENTIMENTS = {'正面', '负面', '中性/混合'}
TOPICS = {'尺码与版型', '面料与质量', '款式与外观', '价格与价值感', '物流与服务', '其他'}
CONFIDENCES = {'高', '中', '低'}
NEEDED = ['review_id', 'sentiment', 'topic', 'user_need', 'confidence']


def main():
    src = DATA/'ai_labels.csv'
    if not src.exists():
        raise SystemExit('请先把ChatGPT生成的 CSV 存为 data/ai_labels.csv。不要改动 review_id。')
    source = pd.read_csv(DATA/'analysis_base.csv', dtype={'review_id': str}).fillna('')
    ai = pd.read_csv(src, dtype=str).fillna('')
    ai.columns = ai.columns.str.strip()
    if not set(NEEDED).issubset(ai.columns):
        raise SystemExit(f'AI CSV 必须有列：{NEEDED}；当前：{list(ai.columns)}')
    ai = ai[NEEDED].copy()
    for col in NEEDED:
        ai[col] = ai[col].astype(str).str.strip()
    if ai['review_id'].duplicated().any():
        raise SystemExit('AI 输出包含重复 review_id：' + str(ai.loc[ai.review_id.duplicated(),'review_id'].tolist()[:5]))
    missing = sorted(set(source.review_id) - set(ai.review_id))
    extra = sorted(set(ai.review_id) - set(source.review_id))
    if missing or extra:
        raise SystemExit(f'行数/ID 不匹配！缺失ID示例 {missing[:10]}；额外ID示例 {extra[:10]}。请重新补齐或修正。')
    for column, accepted in [('sentiment',SENTIMENTS),('topic',TOPICS),('confidence',CONFIDENCES)]:
        wrong = ai[~ai[column].isin(accepted)][['review_id',column]]
        if len(wrong):
            raise SystemExit(f'{column} 出现不合规范的值，前10条：\n{wrong.head(10).to_string(index=False)}\n允许：{sorted(accepted)}')
    if ai['user_need'].eq('').any():
        raise SystemExit('user_need 不能为空。')
    enriched = source.merge(ai, on='review_id', how='left', validate='one_to_one')
    enriched.to_csv(DATA/'enriched_reviews.csv', index=False, encoding='utf-8-sig')

    checks = DATA/'manual_check.csv'
    if not checks.exists():
        # Balanced human spot-check, sampled only AFTER AI labeling.
        samples = []
        for segment in ['负面', '正面', '中性/混合']:
            part = enriched[enriched['sentiment'] == segment]
            if len(part):
                samples.append(part.sample(n=min(10,len(part)), random_state=77))
        checked = pd.concat(samples, ignore_index=True) if samples else enriched.sample(n=min(30,len(enriched)),random_state=77)
        if len(checked) < min(30,len(enriched)):
            extras = enriched[~enriched.review_id.isin(checked.review_id)]
            checked = pd.concat([checked,extras.sample(n=min(30-len(checked),len(extras)),random_state=77)], ignore_index=True)
        checked = checked[['review_id','review_text','sentiment','topic']].rename(
            columns={'sentiment':'ai_sentiment','topic':'ai_topic'})
        checked['manual_sentiment'] = ''
        checked['manual_topic'] = ''
        checked.to_csv(checks, index=False, encoding='utf-8-sig')
        print('同时生成 data/manual_check.csv：请人工独立复核30条，将结果填在 manual_* 列。')
    print('通过验证：全部评论均匹配，标签合法。已生成 data/enriched_reviews.csv。')

if __name__ == '__main__':
    main()
