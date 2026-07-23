"""
panda_chokubaisho_list.py
パンダベビーカステラ 直売所営業候補リスト（A4 1枚PDF）
"""
import os
from weasyprint import HTML

DIR = os.path.dirname(os.path.abspath(__file__))

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<style>
@font-face { font-family: 'JP'; src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'); }
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'JP', sans-serif; font-size: 10pt; color: #1a1a1a; width: 210mm; }

/* ヘッダー */
.hdr { background: #2d5a1b; padding: 12px 20px; }
.hdr h1 { font-size: 16pt; color: #fff; letter-spacing: 1px; }
.hdr .sub { font-size: 9pt; color: #a5d6a7; margin-top: 3px; }
.hdr .date { font-size: 8.5pt; color: #c8e6c9; text-align: right; margin-top: 2px; }

/* エリアタイトル */
.area { font-size: 11pt; font-weight: bold; color: #fff; background: #2d5a1b;
        padding: 5px 12px; margin: 10px 20px 6px; letter-spacing: 0.5px; }

/* テーブル */
.tbl-wrap { padding: 0 20px; margin-bottom: 2px; }
table.list { width: 100%; border-collapse: collapse; font-size: 9pt; }
table.list th { background: #4a8f2a; color: #fff; padding: 5px 7px;
                text-align: left; font-weight: bold; font-size: 8.5pt; }
table.list td { padding: 5px 7px; border-bottom: 1px solid #e0e0e0;
                vertical-align: top; line-height: 1.5; }
table.list tr:nth-child(even) td { background: #f9fbe7; }
table.list tr:nth-child(odd) td { background: #fff; }
.num { width: 24px; text-align: center; color: #888; }
.name { font-weight: bold; color: #2d5a1b; }
.note { font-size: 8pt; color: #555; }

/* おすすめ枠 */
.priority { margin: 8px 20px 0; background: #fff8e1; border: 1px solid #ffe082;
            padding: 8px 12px; font-size: 8.5pt; line-height: 1.8; }
.priority strong { color: #e65100; }

/* フッター */
.ftr { background: #2d5a1b; padding: 8px 20px; margin-top: 10px; }
.ftr .co { color: #c8e6c9; font-size: 8.5pt; line-height: 1.7; }
.ftr .co strong { color: #fff; font-size: 9.5pt; }
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="hdr">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td><h1>🐼 なんだパンダベビーカステラ　直売所 営業候補リスト</h1>
        <div class="sub">那須塩原市・大田原市・那須町 ／ 現在の取引先を除く新規候補</div></td>
    <td style="text-align:right; vertical-align:bottom;">
        <div class="date">作成日：2026年7月23日</div></td>
  </tr></tbody></table>
</div>

<!-- 那須塩原市 -->
<div class="area">📍 那須塩原市</div>
<div class="tbl-wrap">
<table class="list">
  <thead><tr>
    <th class="num">#</th>
    <th style="width:26%">施設名</th>
    <th style="width:28%">住所</th>
    <th style="width:18%">TEL</th>
    <th style="width:13%">営業時間</th>
    <th>特徴・メモ</th>
  </tr></thead>
  <tbody>
    <tr>
      <td class="num">1</td>
      <td class="name">なすのマルシェ</td>
      <td>那須塩原市下厚崎200-4-3</td>
      <td>0287-74-3715</td>
      <td>8:30〜16:00<br><span class="note">火曜定休</span></td>
      <td>JAなすの運営。2023年開業で新しく清潔感あり。ファミリー層多数。</td>
    </tr>
    <tr>
      <td class="num">2</td>
      <td class="name">そすいの郷 直売センター</td>
      <td>那須塩原市三区町656-2</td>
      <td>0287-37-7768</td>
      <td>9:00〜16:00<br><span class="note">元旦のみ休</span></td>
      <td>西那須野地区。地元農家50名以上が出品。年中ほぼ無休で安定集客。</td>
    </tr>
    <tr>
      <td class="num">3</td>
      <td class="name">高林産直会</td>
      <td>那須塩原市木綿畑452-1</td>
      <td>0287-68-1092</td>
      <td>9:00〜16:00<br><span class="note">木曜定休</span></td>
      <td>地元農家自主運営の産直。地域密着型で常連客が多い。</td>
    </tr>
    <tr>
      <td class="num">4</td>
      <td class="name">那須の駅 農産物直売所</td>
      <td>那須塩原市鍋掛1475-357</td>
      <td>0287-62-0034</td>
      <td>要確認</td>
      <td>黒羽商工会エリア。黒羽・那珂川方面の来客が多い。</td>
    </tr>
    <tr>
      <td class="num">5</td>
      <td class="name">アグリパル塩原</td>
      <td>那須塩原市関谷442</td>
      <td>0287-35-4401</td>
      <td>8:30〜17:00</td>
      <td>道の駅・塩原温泉郷入口。<strong style="color:#2d5a1b;">委託販売申込書 記入済み・提出待ち。</strong></td>
    </tr>
  </tbody>
</table>
</div>

<!-- 大田原市 -->
<div class="area">📍 大田原市</div>
<div class="tbl-wrap">
<table class="list">
  <thead><tr>
    <th class="num">#</th>
    <th style="width:26%">施設名</th>
    <th style="width:28%">住所</th>
    <th style="width:18%">TEL</th>
    <th style="width:13%">営業時間</th>
    <th>特徴・メモ</th>
  </tr></thead>
  <tbody>
    <tr>
      <td class="num">1</td>
      <td class="name">あさか直売所</td>
      <td>大田原市浅香2丁目3389-53</td>
      <td>0287-22-4621</td>
      <td>9:00〜17:30<br><span class="note">無休</span></td>
      <td>市街地に近く年中無休。地元住民の利用が多く安定した来客数。</td>
    </tr>
    <tr>
      <td class="num">2</td>
      <td class="name">きらり佐久山<br>農産物直売所</td>
      <td>大田原市佐久山2554-1</td>
      <td>0287-28-1290</td>
      <td>8:00〜18:00<br><span class="note">（4〜10月）</span></td>
      <td>大田原市北部エリア。観光シーズンは集客あり。佐久山温泉に近い。</td>
    </tr>
  </tbody>
</table>
</div>

<!-- 那須町 -->
<div class="area">📍 那須町</div>
<div class="tbl-wrap">
<table class="list">
  <thead><tr>
    <th class="num">#</th>
    <th style="width:26%">施設名</th>
    <th style="width:28%">住所</th>
    <th style="width:18%">TEL</th>
    <th style="width:13%">営業時間</th>
    <th>特徴・メモ</th>
  </tr></thead>
  <tbody>
    <tr>
      <td class="num">1</td>
      <td class="name">道の駅 那須高原友愛の森<br>（那須ロイヤル高原マルシェ）</td>
      <td>那須郡那須町大字高久乙593-8</td>
      <td>0287-78-0233</td>
      <td>9:00〜17:00</td>
      <td>那須ブランド認定品と相性抜群。春〜秋の観光客は県内トップ級。マルシェ出店も可。</td>
    </tr>
    <tr>
      <td class="num">2</td>
      <td class="name">道の駅 東山道伊王野<br>（物産センター）</td>
      <td>那須郡那須町大字伊王野459</td>
      <td>0287-75-0577</td>
      <td>8:30〜17:00</td>
      <td>巨大水車で挽いた手打ちそばで有名。観光客が多く土産需要が高い。</td>
    </tr>
  </tbody>
</table>
</div>

<!-- 優先アクション -->
<div class="priority">
  <strong>★ 優先アクション（電話の順番）</strong>　①なすのマルシェ　②道の駅 那須高原友愛の森　③そすいの郷直売センター　④あさか直売所<br>
  ※アグリパル塩原は申込書提出を先に完了させること。「委託販売・またはイベント出店でご相談したい」と伝えて担当者を確認。
</div>

<!-- フッター -->
<div class="ftr">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td class="co"><strong>株式会社 芹江コンチェルト</strong>　栃木県大田原市山の手1丁目7-7</td>
    <td style="text-align:right; color:#c8e6c9; font-size:8.5pt; line-height:1.7;">
      TEL：0287-33-9217　／　担当：芹江匡晋</td>
  </tr></tbody></table>
</div>

</body>
</html>"""


def main():
    out_path = os.path.join(DIR, 'panda_chokubaisho_list.pdf')
    print('直売所リストPDF生成中...')
    HTML(string=HTML_CONTENT).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
