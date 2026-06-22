"""
パンダ営業資料 PDF 生成パイプライン
実行: python panda_pipeline.py

ステップ:
  1. 地域候補地調査 (panda_local_research) → panda_sales_candidates.txt
  2. 提案書 Markdown 生成 (panda_proposal_generator) → panda_sales_proposal_YYYYMMDD.md
  3. PDF 変換 (panda_pdf) → panda_sales_proposal_YYYYMMDD.pdf
  4. 完了通知を LINE 送信

オプション:
  --skip-research   候補地調査をスキップ（既存の panda_sales_candidates.txt を使う）
  --skip-proposal   提案書生成もスキップ（既存の最新 .md を使う）
"""

import env_loader
import os, sys, json, urllib.request
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

from get_line_token import get_line_token
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

def send_line(message):
    token = get_line_token()
    data = json.dumps({
        'to': LINE_USER_ID,
        'messages': [{'type': 'text', 'text': message}]
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    )
    urllib.request.urlopen(req)

def step(label, fn):
    print(f'\n{"="*50}')
    print(f'▶ {label}')
    print('='*50)
    try:
        result = fn()
        print(f'✓ 完了')
        return result
    except Exception as e:
        print(f'✗ エラー: {e}')
        raise

def main():
    args = sys.argv[1:]
    skip_research = '--skip-research' in args or '--skip-proposal' in args
    skip_proposal = '--skip-proposal' in args

    today = datetime.now().strftime('%Y/%m/%d')
    print(f'パンダ🐼営業資料 PDF パイプライン開始 ({today})')

    # ── Step 1: 候補地調査 ──────────────────────────
    if not skip_research:
        import panda_local_research
        step('Step 1: 地域営業候補地調査（ウェブ検索）', panda_local_research.main)
    else:
        print('\n[Step 1 スキップ] 既存の候補地リストを使用します')

    # ── Step 2: 提案書 Markdown 生成 ─────────────────
    if not skip_proposal:
        import panda_proposal_generator
        md_path = step('Step 2: 提案書 Markdown 生成', panda_proposal_generator.main)
    else:
        import glob
        files = sorted(glob.glob(os.path.join(DIR, 'panda_sales_proposal_*.md')), reverse=True)
        if not files:
            print('エラー: 提案書 Markdown が見つかりません。--skip-proposal を外して実行してください。')
            sys.exit(1)
        md_path = files[0]
        print(f'\n[Step 2 スキップ] 既存の提案書を使用: {os.path.basename(md_path)}')

    # ── Step 3: PDF 変換 ──────────────────────────────
    import panda_pdf
    pdf_path = step('Step 3: PDF 変換', lambda: panda_pdf.main(md_path))

    # ── 完了 ──────────────────────────────────────────
    print(f'\n{"="*50}')
    print(f'🐼 完了！')
    print(f'   Markdown : {md_path}')
    print(f'   PDF      : {pdf_path}')
    print('='*50)

    try:
        line_msg = (
            f'🐼 パンダ営業資料PDFを生成しました\n'
            f'生成日時: {today}\n'
            f'ファイル: {os.path.basename(pdf_path)}\n'
            f'場所: {pdf_path}'
        )
        send_line(line_msg)
        print('LINE通知送信完了')
    except Exception as e:
        print(f'LINE通知スキップ（{e}）')

if __name__ == '__main__':
    main()
