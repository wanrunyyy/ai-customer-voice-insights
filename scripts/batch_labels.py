"""Split 200 real reviews into five 40-review batches or combine AI results.

Usage:
  python scripts/batch_labels.py split
  python scripts/batch_labels.py combine
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data'
BATCH = DATA/'batches'
BATCH_SIZE = 40


def split():
    source = DATA/'ai_input.csv'
    if not source.exists():
        raise SystemExit('请先运行 scripts/prepare_data.py。')
    df = pd.read_csv(source, dtype={'review_id':str})
    BATCH.mkdir(parents=True,exist_ok=True)
    for i,start in enumerate(range(0,len(df),BATCH_SIZE),1):
        destination=BATCH/f'ai_input_{i:02d}.csv'
        df.iloc[start:start+BATCH_SIZE].to_csv(destination,index=False,encoding='utf-8-sig')
        print(f'{destination.name}: {len(df.iloc[start:start+BATCH_SIZE])} 条')
    print('把每个 ai_input_XX.csv 单独上传ChatGPT分类，并存为同文件夹 ai_labels_XX.csv。')


def combine():
    source=DATA/'ai_input.csv'
    expected=pd.read_csv(source,dtype={'review_id':str})
    if not BATCH.exists():
        raise SystemExit('data/batches不存在。请先运行 split。')
    files=sorted(BATCH.glob('ai_labels_*.csv'))
    expected_files=(len(expected)+BATCH_SIZE-1)//BATCH_SIZE
    if len(files)!=expected_files:
        raise SystemExit(f'应有{expected_files}个 ai_labels_XX.csv，实际找到{len(files)}个。')
    frames=[]
    for name in files:
        frame=pd.read_csv(name,dtype=str).fillna('')
        frame.columns=frame.columns.str.strip()
        frames.append(frame)
    combined=pd.concat(frames,ignore_index=True)
    if combined.review_id.duplicated().any():
        raise SystemExit('合并后review_id重复，请核对各批次输出。')
    missing=set(expected.review_id)-set(combined.review_id)
    extra=set(combined.review_id)-set(expected.review_id)
    if missing or extra:
        raise SystemExit(f'合并后ID不匹配，缺失{sorted(missing)[:10]}、多出{sorted(extra)[:10]}。请修正。')
    combined.to_csv(DATA/'ai_labels.csv',index=False,encoding='utf-8-sig')
    print('成功生成 data/ai_labels.csv。下一步运行 python scripts/validate_labels.py')

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('split','combine'):
        raise SystemExit('用法：python scripts/batch_labels.py split | combine')
    (split if sys.argv[1]=='split' else combine)()
