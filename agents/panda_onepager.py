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
@font-face {
    font-family: 'JP';
    src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}
@page {
    size: A4;
    margin: 0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'JP', sans-serif;
    font-size: 9pt;
    color: #1a1a1a;
    width: 210mm;
}

/* ── ヘッダー ── */
.header {
    background: #2d5a1b;
    padding: 14px 20px 12px;
    width: 100%;
}
.header table { width: 100%; border-collapse: collapse; }
.header td { vertical-align: middle; border: none; background: none; padding: 0; }
.header-icon { font-size: 46px; line-height: 1; width: 60px; }
.header h1 { font-size: 22pt; color: #fff; letter-spacing: 1px; line-height: 1.2; }
.header .sub { font-size: 9pt; color: #c8e6c9; margin-top: 3px; }

/* ── 本文エリア ── */
.content {
    padding: 12px 20px 10px;
    width: 100%;
}

/* ── ブランドストーリー ── */
.story {
    background: #f9fbe7;
    border-left: 5px solid #4a8f2a;
    padding: 8px 12px;
    margin-bottom: 10px;
    font-size: 9pt;
    line-height: 1.75;
    color: #2e3b1e;
}
.story strong { color: #2d5a1b; }

/* ── セクションタイトル ── */
.sec-title {
    font-size: 9pt;
    font-weight: bold;
    color: #fff;
    background: #2d5a1b;
    padding: 3px 10px;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}

/* ── 2カラムテーブル ── */
.two-col {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
}
.two-col > tbody > tr > td {
    vertical-align: top;
    border: none;
    background: none;
    padding: 0;
    width: 50%;
}
.two-col > tbody > tr > td:first-child {
    padding-right: 8px;
}
.two-col > tbody > tr > td:last-child {
    padding-left: 8px;
}

/* ── 特徴アイテム ── */
.feat-table { width: 100%; border-collapse: collapse; margin-bottom: 4px; }
.feat-table td { border: none; background: none; padding: 0; vertical-align: top; }
.feat-row {
    background: #f1f8e9;
    border: 1px solid #c8e6c9;
    margin-bottom: 5px;
    padding: 6px 8px;
    font-size: 9pt;
    line-height: 1.5;
}
.feat-row strong { color: #2d5a1b; display: block; font-size: 8.5pt; }

/* ── 素材カード ── */
.ing-card {
    background: #fff8e1;
    border: 1px solid #ffe082;
    padding: 5px 8px;
    margin-bottom: 5px;
    font-size: 9pt;
    line-height: 1.5;
}
.ing-label { font-size: 7.5pt; color: #f57f17; font-weight: bold; }
.ing-name  { font-size: 9.5pt; font-weight: bold; }
.ing-note  { font-size: 8pt; color: #666; }

/* ── タグ ── */
.tag-area { margin-bottom: 8px; }
.tag {
    display: inline-block;
    border-radius: 20px;
    padding: 2px 9px;
    font-size: 8pt;
    margin: 2px 2px 2px 0;
}
.tag-green  { background: #e8f5e9; border: 1px solid #a5d6a7; color: #1b5e20; }
.tag-blue   { background: #e3f2fd; border: 1px solid #90caf9; color: #0d47a1; }

/* ── 出店条件 ── */
.spec-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin-bottom: 10px; }
.spec-table th {
    background: #2d5a1b;
    color: #fff;
    padding: 4px 8px;
    text-align: left;
    font-weight: bold;
    width: 28%;
}
.spec-table td {
    background: #f3e5f5;
    border: 1px solid #ce93d8;
    padding: 4px 8px;
    color: #1a1a1a;
}

/* ── フッター ── */
.footer {
    background: #2d5a1b;
    padding: 8px 20px;
    width: 100%;
}
.footer table { width: 100%; border-collapse: collapse; }
.footer td { border: none; background: none; padding: 0; vertical-align: middle; }
.footer .company { color: #c8e6c9; font-size: 8pt; line-height: 1.6; }
.footer .company strong { color: #fff; font-size: 9pt; }
.footer .contact { text-align: right; color: #c8e6c9; font-size: 8pt; line-height: 1.7; }
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="header">
  <table><tbody><tr>
    <td class="header-icon">🐼</td>
    <td>
      <h1>なんだパンダベビーカステラ</h1>
      <div class="sub">栃木県那須塩原市発 ／ 地産地消 ／ キッチンカー・物産展</div>
    </td>
  </tr></tbody></table>
</div>

<div class="content">

  <!-- ブランドストーリー -->
  <div class="story">
    2018年、私たち家族は東京から栃木県大田原市へ移住。妻は上野稲荷町、夫は門前仲町の出身。
    子供たちを連れて通った<strong>上野動物園のパンダ</strong>への思い出と、
    根を張り始めた<strong>那須地方への恩返し</strong>の気持ちから生まれたのがこのカステラです。
    パンダ型の愛らしさと、那須産素材だけで作る焼きたての味を、ここでしか食べられない体験としてお届けします。
  </div>

  <!-- 2カラム：特徴 ＋ 素材・実績 -->
  <table class="two-col"><tbody><tr>

    <!-- 左：商品の特徴 -->
    <td>
      <div class="sec-title">🎯 商品の特徴</div>
      <div class="feat-row"><strong>🐼 パンダ型</strong>見た目のかわいさでSNS映え抜群。子どもから大人まで思わず写真を撮りたくなる形。</div>
      <div class="feat-row"><strong>✨ モチっとしてカリっとする独特の食感</strong>100%米粉だからこそ生まれる、外はサクッ・中はもっちりの食感。</div>
      <div class="feat-row"><strong>🌾 栃木産米粉 100%使用</strong>小麦粉不使用。グルテンフリー対応で幅広い方に食べていただけます。</div>
      <div class="feat-row"><strong>🔥 賞味期限：当日限り</strong>保存料・添加物なし。焼きたてだからこその新鮮な味わい。「ここでしか食べられない」が最大の価値。</div>
    </td>

    <!-- 右：素材・実績・取引先 -->
    <td>
      <div class="sec-title">🌿 使用素材（すべて那須・栃木産）</div>
      <div class="ing-card">
        <div class="ing-label">🥚 卵</div>
        <div class="ing-name">那須御養卵</div>
        <div class="ing-note">那須高原で大切に育てられた鶏の卵。コクと甘みが豊か。</div>
      </div>
      <div class="ing-card">
        <div class="ing-label">🥛 牛乳</div>
        <div class="ing-name">千本松牧場の牛乳</div>
        <div class="ing-note">那須塩原の老舗牧場。濃厚でまろやかな味わい。</div>
      </div>
      <div class="ing-card">
        <div class="ing-label">🌾 米粉</div>
        <div class="ing-name">栃木産米粉（100%）</div>
        <div class="ing-note">地元栃木のお米から作った米粉のみ。小麦粉不使用。</div>
      </div>

      <div style="margin-top:8px;">
        <div class="sec-title">📍 出店実績</div>
        <div class="tag-area">
          <span class="tag tag-green">大田原東武百貨店</span>
          <span class="tag tag-green">宇都宮東武百貨店</span>
          <span class="tag tag-green">東京ソラマチ</span>
          <span class="tag tag-green">渋谷キャストガーデン</span>
          <span class="tag tag-green">東京江東区民祭り</span>
          <span class="tag tag-green">高輪ゲートウェイ</span>
        </div>
      </div>

      <div>
        <div class="sec-title">🤝 現在の取引先</div>
        <div class="tag-area">
          <span class="tag tag-blue">トコトコ大田原</span>
          <span class="tag tag-blue">道の駅・那須の与一の郷</span>
          <span class="tag tag-blue">道の駅・明治の森黒磯</span>
        </div>
      </div>
    </td>

  </tr></tbody></table>

  <!-- 出店条件 -->
  <div class="sec-title">🚐 出店条件（キッチンカー）</div>
  <table class="spec-table"><tbody>
    <tr>
      <th>スペース</th><td>約3m × 6m（キッチンカー1台分）</td>
      <th>電源</th><td>100V・15A以上（延長コード持参可）</td>
      <th>水道</th><td>タンク持参で対応可</td>
    </tr>
    <tr>
      <th>費用形態</th><td>売上歩合制 または 固定出店料（要相談）</td>
      <th>営業時間</th><td>10:00〜17:00（応相談）</td>
      <th>許認可</th><td>食品営業許可取得済み</td>
    </tr>
  </tbody></table>

</div>

<!-- フッター -->
<div class="footer">
  <table><tbody><tr>
    <td class="company">
      <strong>株式会社 芹江コンチェルト</strong><br>
      所在地：栃木県那須塩原市（JR黒磯駅近く）<br>
      事業：旅館業 Lodgers Bldg SERIE ／ Honey LaRva フィットネスボクシングジム（大田原市・那須塩原市）
    </td>
    <td class="contact">
      TEL：＿＿＿＿＿＿＿＿＿＿<br>
      MAIL：＿＿＿＿＿＿＿＿＿＿<br>
      担当：芹江匡晋
    </td>
  </tr></tbody></table>
</div>

</body>
</html>"""

def main():
    ensure_deps()
    from weasyprint import HTML

    out_path = os.path.join(DIR, 'panda_onepager.pdf')
    print('1ページPDF生成中...')
    HTML(string=HTML_CONTENT).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path

if __name__ == '__main__':
    main()
