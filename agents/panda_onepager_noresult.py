"""
panda_onepager_noresult.py
出店実績・現在の取引先を伏せたバージョンの商品紹介シートを生成する。
"""
import os
import sys
import importlib.util

DIR = os.path.dirname(os.path.abspath(__file__))

# 2カラムテーブル全体を、フルwidth縦積みレイアウトに置き換える
OLD_COLS = (
    '<table class="cols"><tbody><tr>\n'
    '\n'
    '  <!-- 左：商品の特徴 -->\n'
    '  <td>\n'
    '    <div class="sec">🎯 商品の特徴</div>\n'
    '    <div class="feat"><strong>🐼 パンダ型</strong>見た目のかわいさでSNS映え抜群。子どもから大人まで思わず写真を撮りたくなる形。</div>\n'
    '    <div class="feat"><strong>✨ モチっとカリっとする独特の食感</strong>100%米粉だからこそ生まれる、外はサクッ・中はもっちりの食感。</div>\n'
    '    <div class="feat"><strong>🌾 栃木産米粉 100%使用</strong>小麦粉不使用。グルテンフリー対応で幅広い方にお召し上がりいただけます。</div>\n'
    '    <div class="feat"><strong>🔥 賞味期限：当日限り</strong>保存料・添加物なし。「ここでしか食べられない」が最大の価値です。</div>\n'
    '    <table class="feat-photos"><tbody><tr>\n'
    '      <td><img src="{IMG1}" alt="パンダカステラ"></td>\n'
    '      <td><img src="{IMG0}" alt="キッチンカー"></td>\n'
    '    </tr></tbody></table>\n'
    '  </td>\n'
    '\n'
    '  <!-- 右：素材・実績 -->\n'
    '  <td>\n'
    '    <div class="sec">🌿 使用素材（すべて那須・栃木産）</div>\n'
    '    <div class="ing">\n'
    '      <div class="ing-label">🥚 卵</div>\n'
    '      <div class="ing-name">那須御養卵</div>\n'
    '      <div class="ing-note">那須高原で大切に育てられた鶏の卵。コクと甘みが豊か。</div>\n'
    '    </div>\n'
    '    <div class="ing">\n'
    '      <div class="ing-label">🥛 牛乳</div>\n'
    '      <div class="ing-name">千本松牧場の牛乳</div>\n'
    '      <div class="ing-note">那須塩原の老舗牧場。濃厚でまろやかな味わい。</div>\n'
    '    </div>\n'
    '    <div class="ing">\n'
    '      <div class="ing-label">🌾 米粉</div>\n'
    '      <div class="ing-name">栃木産米粉（100%）</div>\n'
    '      <div class="ing-note">地元栃木のお米のみ使用。小麦粉不使用。</div>\n'
    '    </div>\n'
    '    <div style="margin-top:10px;">\n'
    '      <div class="sec">📍 出店実績</div>\n'
    '      <div class="tag-area">\n'
    '        <span class="tag tg">宇都宮東武百貨店</span>\n'
    '        <span class="tag tg">東京ソラマチ</span><span class="tag tg">渋谷キャストガーデン</span>\n'
    '        <span class="tag tg">東京江東区民祭り</span><span class="tag tg">高輪ゲートウェイ</span>\n'
    '      </div>\n'
    '    </div>\n'
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
    '  </td>\n'
    '\n'
    '</tr></tbody></table>'
)

NEW_COLS = '''<!-- 商品の特徴：フルwidth 2列グリッド -->
<div style="padding: 10px 20px 0;">
  <div class="sec">🎯 商品の特徴</div>
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td style="width:50%; vertical-align:top; padding-right:8px;">
      <div class="feat"><strong>🐼 パンダ型</strong>見た目のかわいさでSNS映え抜群。子どもから大人まで思わず写真を撮りたくなる形。</div>
      <div class="feat"><strong>🌾 栃木産米粉 100%使用</strong>小麦粉不使用。グルテンフリー対応で幅広い方にお召し上がりいただけます。</div>
    </td>
    <td style="width:50%; vertical-align:top; padding-left:8px;">
      <div class="feat"><strong>✨ モチっとカリっとする独特の食感</strong>100%米粉だからこそ生まれる、外はサクッ・中はもっちりの食感。</div>
      <div class="feat"><strong>🔥 賞味期限：当日限り</strong>保存料・添加物なし。「ここでしか食べられない」が最大の価値です。</div>
    </td>
  </tr></tbody></table>
</div>

<!-- 写真：フルwidth 2枚横並び -->
<div style="padding: 8px 20px 8px;">
  <table class="feat-photos"><tbody><tr>
    <td><img src="{IMG1}" alt="パンダカステラ"></td>
    <td><img src="{IMG0}" alt="キッチンカー"></td>
  </tr></tbody></table>
</div>

<!-- 素材：3カラム横並び -->
<div style="padding: 0 20px 10px;">
  <div class="sec">🌿 使用素材（すべて那須・栃木産）</div>
  <table style="width:100%; border-collapse:collapse; margin-top:6px;"><tbody><tr>
    <td style="width:33.3%; padding-right:6px; vertical-align:top;">
      <div class="ing"><div class="ing-label">🥚 卵</div><div class="ing-name">那須御養卵</div><div class="ing-note">那須高原で大切に育てられた鶏の卵。コクと甘みが豊か。</div></div>
    </td>
    <td style="width:33.3%; padding:0 3px; vertical-align:top;">
      <div class="ing"><div class="ing-label">🥛 牛乳</div><div class="ing-name">千本松牧場の牛乳</div><div class="ing-note">那須塩原の老舗牧場。濃厚でまろやかな味わい。</div></div>
    </td>
    <td style="width:33.3%; padding-left:6px; vertical-align:top;">
      <div class="ing"><div class="ing-label">🌾 米粉</div><div class="ing-name">栃木産米粉（100%）</div><div class="ing-note">地元栃木のお米のみ使用。小麦粉不使用。</div></div>
    </td>
  </tr></tbody></table>
</div>'''


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

    # 2カラムテーブルをフルwidth縦積みレイアウトに置き換え
    html = html.replace(OLD_COLS, NEW_COLS)

    out_path = os.path.join(DIR, 'panda_onepager_noresult.pdf')
    print('1ページPDF（実績・取引先なし）生成中...')
    HTML(string=html).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
