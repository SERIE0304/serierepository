"""
panda_onepager_noresult.py
出店実績・現在の取引先を伏せたバージョンの商品紹介シートを生成する。
"""
import os
import sys
import importlib.util

DIR = os.path.dirname(os.path.abspath(__file__))

REMOVE_BLOCKS = [
    # 出店実績
    (
        '    <div style="margin-top:10px;">\n'
        '      <div class="sec">📍 出店実績</div>\n'
        '      <div class="tag-area">\n'
        '        <span class="tag tg">宇都宮東武百貨店</span>\n'
        '        <span class="tag tg">東京ソラマチ</span><span class="tag tg">渋谷キャストガーデン</span>\n'
        '        <span class="tag tg">東京江東区民祭り</span><span class="tag tg">高輪ゲートウェイ</span>\n'
        '      </div>\n'
        '    </div>\n'
    ),
    # 現在の取引先
    (
        '    <div>\n'
        '      <div class="sec">🤝 現在の取引先</div>\n'
        '      <div class="tag-area">\n'
        '        <span class="tag tb">トコトコ大田原</span>\n'
        '        <span class="tag tb">道の駅・那須の与一の郷</span>\n'
        '        <span class="tag tb">道の駅・明治の森黒磯</span>\n'
        '        <span class="tag tb">大田原東武百貨店</span>\n'
        '        <span class="tag tb">千本松牧場</span>\n'
        '        <span class="tag tb">栃木県内各マルシェ</span>\n'
        '      </div>\n'
        '    </div>\n'
    ),
]


def main():
    # 元モジュールを動的にロード（base64画像定数を再利用）
    spec = importlib.util.spec_from_file_location(
        "panda_onepager", os.path.join(DIR, "panda_onepager.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from weasyprint import HTML

    html = (mod.HTML_CONTENT
            .replace('{IMG0}', mod.IMG0)
            .replace('{IMG1}', mod.IMG1)
            .replace('{IMG6}', mod.IMG6))

    for block in REMOVE_BLOCKS:
        html = html.replace(block, '')

    # 出店実績・取引先を除いた分の余白を素材カードで均等に埋める
    extra_css = (
        '<style>'
        '.ing { background: #fff8e1; border: 1px solid #ffe082;'
        ' padding: 22px 12px; margin-bottom: 14px; }'
        '</style>'
    )
    html = html.replace('</style>', '</style>' + extra_css, 1)

    out_path = os.path.join(DIR, 'panda_onepager_noresult.pdf')
    print('1ページPDF（実績・取引先なし）生成中...')
    HTML(string=html).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
