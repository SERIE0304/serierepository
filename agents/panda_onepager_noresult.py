"""
panda_onepager_noresult.py
出店実績・現在の取引先を含まない、新規営業先向け商品紹介シート（A4 1枚）。
"""
import os
import importlib.util

DIR = os.path.dirname(os.path.abspath(__file__))

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<style>
@font-face { font-family: 'JP'; src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'); }
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'JP', sans-serif; font-size: 11pt; color: #1a1a1a; width: 210mm; }

/* ヘッダー */
.hdr { background: #2d5a1b; width: 100%; }
.hdr table { width: 100%; border-collapse: collapse; }
.hdr td { border: none; background: none; padding: 0; vertical-align: middle; }
.hdr-logo { padding: 14px 10px 14px 20px; width: 78px; }
.hdr-logo img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid #a5d6a7; background: #fff; }
.hdr-text { padding: 14px 10px 14px 8px; }
.hdr-text h1 { font-size: 22pt; color: #fff; letter-spacing: 1px; line-height: 1.15; }
.hdr-text .sub { font-size: 9.5pt; color: #a5d6a7; margin-top: 4px; letter-spacing: 0.5px; }
.hdr-badge { padding: 14px 20px 14px 0; text-align: right; width: 138px; }
.hdr-badge .badge { background: #4a8f2a; border-radius: 5px; padding: 8px 12px; display: inline-block; }
.hdr-badge .badge-num { font-size: 8pt; color: #c8e6c9; }
.hdr-badge .badge-name { font-size: 10pt; color: #fff; font-weight: bold; }

/* ブランドストーリー */
.story { background: #f0f7e6; border-left: 6px solid #4a8f2a; padding: 16px 20px; font-size: 10.5pt; line-height: 2.0; color: #2e3b1e; }
.story strong { color: #2d5a1b; }

/* セクションタイトル */
.sec { font-size: 10.5pt; font-weight: bold; color: #fff; background: #2d5a1b; padding: 6px 12px; margin-bottom: 8px; letter-spacing: 0.5px; }

/* 商品の特徴 */
.feat { background: #f1f8e9; border: 1px solid #c8e6c9; margin-bottom: 8px; padding: 10px 12px; font-size: 10.5pt; line-height: 1.6; }
.feat strong { color: #2d5a1b; display: block; font-size: 10pt; font-weight: bold; margin-bottom: 3px; }

/* 写真エリア */
.photo-img { width: 100%; height: 185px; object-fit: contain; border-radius: 5px; border: 1px solid #c8e6c9; display: block; background: #f9f9f9; }

/* 素材カード */
.ing { background: #fff8e1; border: 1px solid #ffe082; padding: 14px 14px; }
.ing-label { font-size: 8.5pt; color: #e65100; font-weight: bold; }
.ing-name { font-size: 11.5pt; font-weight: bold; color: #1a1a1a; margin: 3px 0; }
.ing-note { font-size: 9.5pt; color: #555; line-height: 1.5; }

/* 出店条件 */
.spec-area { padding: 14px 20px 14px; }
.spec-wrap { display: table; width: 100%; font-size: 0; }
.spec-item { display: inline-block; width: 25%; padding: 3px 3px; font-size: 9pt; vertical-align: top; }
.spec-inner { border: 1px solid #c8e6c9; border-radius: 4px; overflow: hidden; }
.spec-lbl { background: #2d5a1b; color: #fff; padding: 5px 9px; font-size: 8.5pt; font-weight: bold; }
.spec-val { background: #f9fbe7; padding: 7px 9px; line-height: 1.6; }

/* フッター */
.ftr { background: #2d5a1b; padding: 13px 20px; width: 100%; }
.ftr table { width: 100%; border-collapse: collapse; }
.ftr td { border: none; background: none; padding: 0; vertical-align: middle; }
.ftr .co { color: #c8e6c9; font-size: 9pt; line-height: 1.8; }
.ftr .co strong { color: #fff; font-size: 10.5pt; }
.ftr .ct { text-align: right; color: #c8e6c9; font-size: 9pt; line-height: 1.9; }
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="hdr">
  <table><tbody><tr>
    <td class="hdr-logo"><img src="{IMG6}" alt="なんだパンダ ロゴ"></td>
    <td class="hdr-text">
      <h1>なんだパンダベビーカステラ</h1>
      <div class="sub">栃木県那須塩原市発 ／ 地産地消素材 ／ キッチンカー・物産展出店</div>
    </td>
    <td class="hdr-badge">
      <div class="badge">
        <div class="badge-num">大田原ブランド認定</div>
        <div class="badge-name">第 25 号</div>
      </div>
    </td>
  </tr></tbody></table>
</div>

<!-- ブランドストーリー -->
<div class="story">
  2018年、東京（妻：上野稲荷町 / 夫：門前仲町）から栃木県大田原市へ移住。
  妻が子供たちと通い続けた<strong>上野動物園のパンダ</strong>への思い出と、
  <strong>那須地方への恩返し</strong>の気持ちから、このパンダ型ベビーカステラは生まれました。
  那須産素材だけで作る焼きたての味を、「ここでしか食べられない体験」としてお届けします。
</div>

<!-- 商品の特徴：2列グリッド -->
<div style="padding: 16px 20px 0;">
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

<!-- 写真：2枚横並び -->
<div style="padding: 12px 20px 12px;">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td style="width:50%; padding-right:5px;"><img class="photo-img" src="{IMG1}" alt="パンダカステラ"></td>
    <td style="width:50%; padding-left:5px;"><img class="photo-img" src="{IMG0}" alt="キッチンカー"></td>
  </tr></tbody></table>
</div>

<!-- 素材：3カラム -->
<div style="padding: 0 20px 14px;">
  <div class="sec">🌿 使用素材（すべて那須・栃木産）</div>
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td style="width:33.3%; padding-right:6px; vertical-align:top;">
      <div class="ing">
        <div class="ing-label">🥚 卵</div>
        <div class="ing-name">那須御養卵</div>
        <div class="ing-note">那須高原で大切に育てられた鶏の卵。コクと甘みが豊か。</div>
      </div>
    </td>
    <td style="width:33.3%; padding:0 3px; vertical-align:top;">
      <div class="ing">
        <div class="ing-label">🥛 牛乳</div>
        <div class="ing-name">千本松牧場の牛乳</div>
        <div class="ing-note">那須塩原の老舗牧場。濃厚でまろやかな味わい。</div>
      </div>
    </td>
    <td style="width:33.3%; padding-left:6px; vertical-align:top;">
      <div class="ing">
        <div class="ing-label">🌾 米粉</div>
        <div class="ing-name">栃木産米粉（100%）</div>
        <div class="ing-note">地元栃木のお米のみ使用。小麦粉不使用。</div>
      </div>
    </td>
  </tr></tbody></table>
</div>

<!-- 出店・納品について -->
<div class="spec-area">
  <div class="sec">🚐 出店・納品について</div>
  <div style="font-size:9pt; color:#555; margin-bottom:8px;">キッチンカーでの出店のほか、施設・店舗への納品（卸）にも対応しています。お気軽にご相談ください。</div>
  <div class="spec-wrap">
    <div class="spec-item"><div class="spec-inner">
      <div class="spec-lbl">スペース</div><div class="spec-val">約1.5m × 3.4m（1台分）</div>
    </div></div>
    <div class="spec-item"><div class="spec-inner">
      <div class="spec-lbl">電源</div><div class="spec-val">100V・1,200W<br>延長コード持参可</div>
    </div></div>
    <div class="spec-item"><div class="spec-inner">
      <div class="spec-lbl">水道</div><div class="spec-val">タンク持参で対応可</div>
    </div></div>
    <div class="spec-item"><div class="spec-inner">
      <div class="spec-lbl">許認可</div><div class="spec-val">菓子製造業許可<br>食品衛生責任者</div>
    </div></div>
  </div>
</div>

<!-- フッター -->
<div class="ftr">
  <table><tbody><tr>
    <td class="co">
      <strong>株式会社 芹江コンチェルト</strong><br>
      所在地：栃木県大田原市山の手1丁目7-7
    </td>
    <td class="ct">
      TEL：0287-33-9217<br>
      MAIL：masaaki.serie@serieconcerto.co.jp<br>
      担当：芹江匡晋
    </td>
  </tr></tbody></table>
</div>

</body>
</html>"""


def main():
    spec = importlib.util.spec_from_file_location(
        "panda_onepager", os.path.join(DIR, "panda_onepager.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from weasyprint import HTML

    html = (HTML_CONTENT
            .replace('{IMG0}', mod.IMG0)
            .replace('{IMG1}', mod.IMG1)
            .replace('{IMG6}', mod.IMG6))

    out_path = os.path.join(DIR, 'panda_onepager_noresult.pdf')
    print('1ページPDF（実績・取引先なし）生成中...')
    HTML(string=html).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
