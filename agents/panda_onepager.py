"""
なんだパンダベビーカステラ 商品紹介 1ページPDF生成
"""
import os, sys, subprocess

DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_deps():
    try:
        import weasyprint
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'weasyprint'],
                              stdout=subprocess.DEVNULL)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>なんだパンダベビーカステラ 商品紹介</title>
<style>
@font-face {{
    font-family: 'JP';
    src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}}
@page {{
    size: A4;
    margin: 0;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'JP', sans-serif;
    width: 210mm;
    height: 297mm;
    overflow: hidden;
    background: #fff;
    color: #1a1a1a;
}}

/* ── ヘッダー ── */
.header {{
    background: linear-gradient(135deg, #2d5a1b 0%, #4a8f2a 100%);
    padding: 18px 28px 14px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
.header-icon {{
    font-size: 52px;
    line-height: 1;
}}
.header-text h1 {{
    font-size: 24pt;
    color: #fff;
    letter-spacing: 2px;
    line-height: 1.2;
}}
.header-text .sub {{
    font-size: 10pt;
    color: #c8e6c9;
    margin-top: 3px;
    letter-spacing: 1px;
}}

/* ── メインコンテンツ ── */
.body {{
    padding: 16px 28px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}

/* ── ブランドストーリー ── */
.story {{
    background: #f9fbe7;
    border-left: 5px solid #4a8f2a;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 9.5pt;
    line-height: 1.8;
    color: #2e3b1e;
}}
.story strong {{ color: #2d5a1b; }}

/* ── 2カラムレイアウト ── */
.two-col {{
    display: flex;
    gap: 16px;
}}
.col {{ flex: 1; }}

/* ── 商品特徴 ── */
.section-title {{
    font-size: 10pt;
    font-weight: bold;
    color: #fff;
    background: #2d5a1b;
    padding: 4px 12px;
    border-radius: 4px;
    margin-bottom: 8px;
    letter-spacing: 1px;
}}
.features {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.feature-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: #f1f8e9;
    border: 1px solid #c8e6c9;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 9.5pt;
    line-height: 1.5;
}}
.feature-icon {{ font-size: 16px; flex-shrink: 0; margin-top: 1px; }}
.feature-text strong {{ color: #2d5a1b; display: block; font-size: 9pt; }}

/* ── 素材カード ── */
.ingredients {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.ing-card {{
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 9pt;
    line-height: 1.5;
}}
.ing-card .label {{
    font-size: 8pt;
    color: #f57f17;
    font-weight: bold;
    letter-spacing: 0.5px;
}}
.ing-card .name {{ font-size: 9.5pt; color: #1a1a1a; font-weight: bold; }}
.ing-card .note {{ font-size: 8.5pt; color: #666; }}

/* ── 実績・取引先 ── */
.record-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}}
.record-tag {{
    background: #e8f5e9;
    border: 1px solid #a5d6a7;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 8.5pt;
    color: #1b5e20;
    white-space: nowrap;
}}
.partner-tag {{
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 8.5pt;
    color: #0d47a1;
    white-space: nowrap;
}}

/* ── フッター ── */
.footer {{
    background: #2d5a1b;
    padding: 10px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
}}
.footer .company {{
    color: #c8e6c9;
    font-size: 8.5pt;
    line-height: 1.6;
}}
.footer .company strong {{
    color: #fff;
    font-size: 9.5pt;
}}
.footer .contact {{
    text-align: right;
    color: #c8e6c9;
    font-size: 8.5pt;
    line-height: 1.7;
}}
.divider {{
    height: 1px;
    background: #c8e6c9;
    margin: 0 28px;
    opacity: 0.4;
}}
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="header">
  <div class="header-icon">🐼</div>
  <div class="header-text">
    <h1>なんだパンダベビーカステラ</h1>
    <div class="sub">栃木県那須塩原市発 ／ 地産地消 ／ キッチンカー・物産展</div>
  </div>
</div>

<div class="body">

  <!-- ブランドストーリー -->
  <div class="story">
    2018年、私たち家族は東京から栃木県大田原市へ移住。妻は上野稲荷町、夫は門前仲町の出身。
    子供たちを連れて通った<strong>上野動物園のパンダ</strong>への思い出と、
    根を張り始めた<strong>那須地方への恩返し</strong>の気持ちから生まれたのがこのカステラです。
    パンダ型の愛らしさと、那須産素材だけで作る焼きたての味を、ここでしか食べられない体験としてお届けします。
  </div>

  <!-- 商品特徴 ＋ 素材 -->
  <div class="two-col">

    <!-- 左：商品の特徴 -->
    <div class="col">
      <div class="section-title">🎯 商品の特徴</div>
      <div class="features">
        <div class="feature-item">
          <div class="feature-icon">🐼</div>
          <div class="feature-text">
            <strong>パンダ型</strong>
            見た目のかわいさでSNS映え抜群。子どもから大人まで思わず写真を撮りたくなる形。
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">✨</div>
          <div class="feature-text">
            <strong>モチっとしてカリっとする独特の食感</strong>
            100%米粉だからこそ生まれる、外はサクッ・中はもっちりの食感。
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🌾</div>
          <div class="feature-text">
            <strong>栃木産米粉 100%使用</strong>
            小麦粉不使用。グルテンフリー対応で幅広い方に食べていただけます。
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔥</div>
          <div class="feature-text">
            <strong>賞味期限：当日限り</strong>
            保存料・添加物なし。焼きたてだからこその新鮮な味わい。「ここでしか食べられない」が最大の価値。
          </div>
        </div>
      </div>
    </div>

    <!-- 右：使用素材 -->
    <div class="col">
      <div class="section-title">🌿 使用素材（すべて那須・栃木産）</div>
      <div class="ingredients">
        <div class="ing-card">
          <div class="label">🥚 卵</div>
          <div class="name">那須御養卵</div>
          <div class="note">那須高原で大切に育てられた鶏の卵。コクと甘みが豊か。</div>
        </div>
        <div class="ing-card">
          <div class="label">🥛 牛乳</div>
          <div class="name">千本松牧場の牛乳</div>
          <div class="note">那須塩原の老舗牧場。濃厚でまろやかな味わい。</div>
        </div>
        <div class="ing-card">
          <div class="label">🌾 米粉</div>
          <div class="name">栃木産米粉（100%）</div>
          <div class="note">地元栃木のお米から作った米粉のみを使用。小麦粉不使用。</div>
        </div>
      </div>

      <div style="margin-top:10px;">
        <div class="section-title">📍 出店実績</div>
        <div class="record-grid" style="margin-top:2px;">
          <span class="record-tag">大田原東武百貨店</span>
          <span class="record-tag">宇都宮東武百貨店</span>
          <span class="record-tag">東京ソラマチ</span>
          <span class="record-tag">渋谷キャストガーデン</span>
          <span class="record-tag">東京江東区民祭り</span>
          <span class="record-tag">高輪ゲートウェイ</span>
        </div>
      </div>

      <div style="margin-top:10px;">
        <div class="section-title">🤝 現在の取引先</div>
        <div class="record-grid" style="margin-top:2px;">
          <span class="partner-tag">トコトコ大田原</span>
          <span class="partner-tag">道の駅・那須の与一の郷</span>
          <span class="partner-tag">道の駅・明治の森黒磯</span>
        </div>
      </div>
    </div>
  </div>

  <!-- 出店条件 -->
  <div>
    <div class="section-title">🚐 出店条件（キッチンカー）</div>
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:4px;">
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">スペース</span><br>約3m×6m（1台分）
      </div>
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">電源</span><br>100V・15A以上
      </div>
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">水道</span><br>タンク持参で対応可
      </div>
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">費用</span><br>売上歩合制 or 固定出店料
      </div>
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">営業時間</span><br>10:00〜17:00（応相談）
      </div>
      <div style="background:#f3e5f5;border:1px solid #ce93d8;border-radius:6px;padding:5px 12px;font-size:8.5pt;">
        <span style="color:#6a1b9a;font-weight:bold;">許認可</span><br>食品営業許可取得済み
      </div>
    </div>
  </div>

</div>

<!-- フッター -->
<div class="divider"></div>
<div class="footer">
  <div class="company">
    <strong>株式会社 芹江コンチェルト</strong><br>
    所在地：栃木県那須塩原市（JR黒磯駅近く）<br>
    事業：旅館業 Lodgers Bldg SERIE ／ Honey LaRva フィットネスボクシングジム
  </div>
  <div class="contact">
    TEL：＿＿＿＿＿＿＿＿＿＿<br>
    MAIL：＿＿＿＿＿＿＿＿＿＿<br>
    担当：小筆
  </div>
</div>

</body>
</html>"""

def main():
    ensure_deps()
    from weasyprint import HTML, CSS

    out_path = os.path.join(DIR, 'panda_onepager.pdf')
    print('1ページPDF生成中...')
    HTML(string=HTML_CONTENT).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path

if __name__ == '__main__':
    main()
