"""
panda_chokubaisho_map.py
直売所営業候補 分布地図（A4 1枚PDF）
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

.hdr { background: #2d5a1b; padding: 11px 20px; }
.hdr h1 { font-size: 15pt; color: #fff; letter-spacing: 1px; }
.hdr .sub { font-size: 8.5pt; color: #a5d6a7; margin-top: 3px; }

.legend-area { color: #fff; font-size: 8pt; font-weight: bold; display: inline-block;
               padding: 2px 7px; border-radius: 3px; margin-bottom: 4px; }

.leg-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; }
.leg-table td { padding: 3px 5px; border-bottom: 1px solid #e8f5e9; vertical-align: top; line-height: 1.4; }
.leg-table .num-cell { text-align: center; width: 20px; font-weight: bold; color: #fff;
                        border-radius: 50%; width: 16px; height: 16px; line-height: 16px;
                        display: inline-block; font-size: 8pt; }
.leg-table .nm { font-weight: bold; font-size: 8pt; }
.leg-table .info { font-size: 7.5pt; color: #555; }

.ftr { background: #2d5a1b; padding: 7px 20px; }
.ftr-co { color: #c8e6c9; font-size: 8pt; }
.ftr-co strong { color: #fff; font-size: 9pt; }
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="hdr">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td>
      <h1>🐼 パンダベビーカステラ　直売所分布マップ</h1>
      <div class="sub">那須塩原市・大田原市・那須町 ／ 現在の取引先を除く新規営業候補9施設</div>
    </td>
    <td style="text-align:right; color:#c8e6c9; font-size:8pt; vertical-align:bottom;">2026年7月23日作成</td>
  </tr></tbody></table>
</div>

<!-- 地図 + 凡例 -->
<div style="padding: 8px 20px 0;">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>

    <!-- 地図エリア -->
    <td style="width:62%; vertical-align:top; padding-right:8px;">
      <div style="font-size:6.5pt; color:#888; text-align:center; margin-bottom:3px;">
        ※地図は概略図です（↑北）　道路は主要道のみ表示
      </div>
      <svg viewBox="0 0 170 220" xmlns="http://www.w3.org/2000/svg"
           style="width:100%; display:block; border:1.5px solid #b0c8a0; border-radius:4px;">

        <!-- 背景 -->
        <rect width="170" height="220" fill="#e8f5e9"/>

        <!-- 那須町エリア（黄色帯） -->
        <polygon points="40,0 170,0 170,95 100,95 80,70 52,42 40,0"
                 fill="#fff9c4" fill-opacity="0.55"/>

        <!-- 大田原市エリア（水色帯） -->
        <polygon points="58,125 170,110 170,220 55,220"
                 fill="#e3f2fd" fill-opacity="0.55"/>

        <!-- 那須塩原市ラベル -->
        <text x="8" y="100" font-size="8.5" fill="#2d5a1b" font-weight="bold" opacity="0.6">那須</text>
        <text x="8" y="110" font-size="8.5" fill="#2d5a1b" font-weight="bold" opacity="0.6">塩原市</text>

        <!-- 大田原市ラベル -->
        <text x="118" y="190" font-size="8.5" fill="#1565c0" font-weight="bold" opacity="0.6">大田原市</text>

        <!-- 那須町ラベル -->
        <text x="120" y="30" font-size="8.5" fill="#c47a00" font-weight="bold" opacity="0.6">那須町</text>

        <!-- 那須連山（山岳シンボル） -->
        <polygon points="4,40 14,12 24,40"  fill="#b8a898" stroke="#9a8878" stroke-width="0.5"/>
        <polygon points="15,42 26,16 37,42" fill="#c8b8a8" stroke="#9a8878" stroke-width="0.5"/>
        <polygon points="0,44 9,26 18,44"   fill="#aca090" stroke="#9a8878" stroke-width="0.5"/>
        <text x="5" y="52" font-size="5.5" fill="#7a6a5a">那須連山</text>

        <!-- 塩原温泉方向の山 -->
        <polygon points="0,72 9,55 18,72" fill="#c0b0a0" stroke="#9a8878" stroke-width="0.5"/>
        <text x="1" y="80" font-size="5" fill="#7a6a5a">塩原</text>

        <!-- 東北自動車道（薄い点線） -->
        <line x1="88" y1="0" x2="95" y2="220"
              stroke="#bbb" stroke-width="1.2" stroke-dasharray="4,3"/>
        <text x="96" y="15" font-size="5" fill="#999" transform="rotate(88 96 15)">東北道</text>

        <!-- 国道4号（N-S 主要道） -->
        <path d="M 72,0 L 75,82 L 68,140 L 65,220"
              stroke="#aaa" stroke-width="1.8" fill="none"/>
        <text x="60" y="175" font-size="5.5" fill="#888">国道4号</text>

        <!-- 国道400号（西へ 黒磯→塩原） -->
        <path d="M 75,82 Q 60,78 45,76"
              stroke="#c8c8c8" stroke-width="1" fill="none"/>

        <!-- 国道294号（東へ 那須塩原→大田原北部） -->
        <path d="M 68,110 L 115,122"
              stroke="#c8c8c8" stroke-width="1" fill="none"/>

        <!-- 那珂川（川） -->
        <path d="M 0,170 Q 45,163 80,168 Q 120,173 170,160"
              stroke="#82b4d4" stroke-width="1.8" fill="none" stroke-linecap="round"/>
        <text x="5" y="178" font-size="5.5" fill="#82b4d4">那珂川</text>

        <!-- JR東北本線（黒磯→那須塩原→西那須野） -->
        <path d="M 75,78 L 65,111 L 62,134"
              stroke="#555" stroke-width="1" fill="none" stroke-dasharray="3,2"/>

        <!-- 参照ポイント：駅 -->
        <circle cx="75" cy="82" r="2.5" fill="#555"/>
        <text x="78" y="80" font-size="5.5" fill="#444">JR黒磯駅</text>

        <circle cx="65" cy="111" r="2.5" fill="#555"/>
        <text x="42" y="109" font-size="5.5" fill="#444">JR那須塩原駅</text>

        <circle cx="62" cy="134" r="2.5" fill="#555"/>
        <text x="39" y="132" font-size="5.5" fill="#444">JR西那須野駅</text>

        <!-- 那須IC -->
        <text x="96" y="32" font-size="5" fill="#888">那須IC▲</text>

        <!-- ===== 施設マーカー ===== -->

        <!-- 那須塩原市（緑 #2d5a1b）-->
        <!-- 1 なすのマルシェ (70, 95) -->
        <circle cx="70" cy="95" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.2"/>
        <text x="70" y="99" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">1</text>
        <line x1="77" y1="95" x2="87" y2="88" stroke="#2d5a1b" stroke-width="0.7"/>
        <text x="88" y="87" font-size="6" fill="#1a3a0a">なすのマルシェ</text>

        <!-- 2 そすいの郷 (63, 137) -->
        <circle cx="63" cy="137" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.2"/>
        <text x="63" y="141" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">2</text>
        <line x1="70" y1="137" x2="80" y2="135" stroke="#2d5a1b" stroke-width="0.7"/>
        <text x="81" y="134" font-size="6" fill="#1a3a0a">そすいの郷</text>

        <!-- 3 高林産直会 (57, 115) -->
        <circle cx="57" cy="115" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.2"/>
        <text x="57" y="119" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">3</text>
        <line x1="50" y1="115" x2="30" y2="120" stroke="#2d5a1b" stroke-width="0.7"/>
        <text x="1" y="119" font-size="6" fill="#1a3a0a">高林産直会</text>

        <!-- 4 那須の駅 (91, 63) -->
        <circle cx="91" cy="63" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.2"/>
        <text x="91" y="67" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">4</text>
        <line x1="84" y1="63" x2="74" y2="58" stroke="#2d5a1b" stroke-width="0.7"/>
        <text x="1" y="59" font-size="6" fill="#1a3a0a">那須の駅直売所</text>

        <!-- 5 アグリパル塩原 (44, 78) -->
        <circle cx="44" cy="78" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.2"/>
        <text x="44" y="82" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">5</text>
        <line x1="44" y1="85" x2="44" y2="93" stroke="#2d5a1b" stroke-width="0.7"/>
        <text x="26" y="101" font-size="6" fill="#1a3a0a">アグリパル塩原</text>
        <text x="29" y="108" font-size="5.5" fill="#888">（申込書提出中）</text>

        <!-- 大田原市（青 #1565c0）-->
        <!-- 6 あさか直売所 (65, 155) -->
        <circle cx="65" cy="155" r="7" fill="#1565c0" stroke="#fff" stroke-width="1.2"/>
        <text x="65" y="159" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">6</text>
        <line x1="72" y1="155" x2="83" y2="153" stroke="#1565c0" stroke-width="0.7"/>
        <text x="84" y="152" font-size="6" fill="#0a2a60">あさか直売所</text>

        <!-- 7 きらり佐久山 (107, 126) -->
        <circle cx="107" cy="126" r="7" fill="#1565c0" stroke="#fff" stroke-width="1.2"/>
        <text x="107" y="130" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">7</text>
        <line x1="107" y1="119" x2="107" y2="112" stroke="#1565c0" stroke-width="0.7"/>
        <text x="96" y="110" font-size="6" fill="#0a2a60">きらり佐久山</text>

        <!-- 那須町（オレンジ #e65100）-->
        <!-- 8 道の駅 那須高原友愛の森 (87, 50) -->
        <circle cx="87" cy="50" r="7" fill="#e65100" stroke="#fff" stroke-width="1.2"/>
        <text x="87" y="54" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">8</text>
        <line x1="94" y1="50" x2="102" y2="50" stroke="#e65100" stroke-width="0.7"/>
        <text x="103" y="47" font-size="6" fill="#7a2400">那須高原友愛の森</text>

        <!-- 9 道の駅 東山道伊王野 (144, 35) -->
        <circle cx="144" cy="35" r="7" fill="#e65100" stroke="#fff" stroke-width="1.2"/>
        <text x="144" y="39" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">9</text>
        <line x1="144" y1="42" x2="144" y2="52" stroke="#e65100" stroke-width="0.7"/>
        <text x="126" y="60" font-size="6" fill="#7a2400">東山道伊王野</text>

        <!-- 北向き矢印 -->
        <polygon points="162,8 166,18 162,15 158,18" fill="#555"/>
        <text x="162" y="25" font-size="6" fill="#555" text-anchor="middle">N</text>

        <!-- スケールバー（約5km） -->
        <line x1="5" y1="212" x2="40" y2="212" stroke="#666" stroke-width="1.2"/>
        <line x1="5" y1="209" x2="5" y2="215" stroke="#666" stroke-width="1.2"/>
        <line x1="40" y1="209" x2="40" y2="215" stroke="#666" stroke-width="1.2"/>
        <text x="22" y="219" font-size="5.5" fill="#666" text-anchor="middle">約5km</text>

      </svg>
    </td>

    <!-- 凡例エリア -->
    <td style="width:38%; vertical-align:top; padding-left:8px;">

      <!-- カラー凡例 -->
      <div style="margin-bottom:8px;">
        <div style="font-size:8pt; font-weight:bold; color:#2d5a1b; border-bottom:2px solid #2d5a1b; padding-bottom:3px; margin-bottom:6px;">
          凡例
        </div>
        <table style="border-collapse:collapse; font-size:8pt; margin-bottom:6px;">
          <tr>
            <td><span style="display:inline-block; width:12px; height:12px; background:#2d5a1b; border-radius:50%; vertical-align:middle;"></span></td>
            <td style="padding-left:4px; color:#2d5a1b; font-weight:bold;">那須塩原市</td>
          </tr>
          <tr>
            <td><span style="display:inline-block; width:12px; height:12px; background:#1565c0; border-radius:50%; vertical-align:middle;"></span></td>
            <td style="padding-left:4px; color:#1565c0; font-weight:bold;">大田原市</td>
          </tr>
          <tr>
            <td><span style="display:inline-block; width:12px; height:12px; background:#e65100; border-radius:50%; vertical-align:middle;"></span></td>
            <td style="padding-left:4px; color:#e65100; font-weight:bold;">那須町</td>
          </tr>
        </table>
      </div>

      <!-- 施設一覧 -->
      <div style="font-size:8pt; font-weight:bold; color:#2d5a1b; border-bottom:2px solid #2d5a1b; padding-bottom:3px; margin-bottom:5px;">
        施設一覧
      </div>

      <!-- 那須塩原市 -->
      <div style="background:#e8f5e9; padding:3px 5px; font-size:7.5pt; font-weight:bold; color:#2d5a1b; margin-bottom:3px;">
        📍 那須塩原市
      </div>
      <table style="width:100%; border-collapse:collapse; margin-bottom:5px;">
        <tr>
          <td style="padding:2px 3px; vertical-align:top; width:18px;">
            <span style="display:inline-block; width:14px; height:14px; background:#2d5a1b; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">1</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">なすのマルシェ</div>
            <div style="font-size:7pt; color:#555;">下厚崎200-4-3　☎0287-74-3715<br>8:30〜16:00（火曜定休）</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#2d5a1b; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">2</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">そすいの郷 直売センター</div>
            <div style="font-size:7pt; color:#555;">三区町656-2　☎0287-37-7768<br>9:00〜16:00（元旦のみ休）</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#2d5a1b; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">3</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">高林産直会</div>
            <div style="font-size:7pt; color:#555;">木綿畑452-1　☎0287-68-1092<br>9:00〜16:00（木曜定休）</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#2d5a1b; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">4</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">那須の駅 農産物直売所</div>
            <div style="font-size:7pt; color:#555;">鍋掛1475-357　☎0287-62-0034</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#2d5a1b; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">5</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">アグリパル塩原</div>
            <div style="font-size:7pt; color:#555;">関谷442　☎0287-35-4401<br>8:30〜17:00</div>
            <div style="font-size:7pt; color:#e65100; font-weight:bold;">★申込書提出中</div>
          </td>
        </tr>
      </table>

      <!-- 大田原市 -->
      <div style="background:#e3f2fd; padding:3px 5px; font-size:7.5pt; font-weight:bold; color:#1565c0; margin-bottom:3px;">
        📍 大田原市
      </div>
      <table style="width:100%; border-collapse:collapse; margin-bottom:5px;">
        <tr>
          <td style="padding:2px 3px; vertical-align:top; width:18px;">
            <span style="display:inline-block; width:14px; height:14px; background:#1565c0; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">6</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">あさか直売所</div>
            <div style="font-size:7pt; color:#555;">浅香2丁目3389-53　☎0287-22-4621<br>9:00〜17:30（無休）</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#1565c0; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">7</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">きらり佐久山農産物直売所</div>
            <div style="font-size:7pt; color:#555;">佐久山2554-1　☎0287-28-1290<br>8:00〜18:00（4〜10月）</div>
          </td>
        </tr>
      </table>

      <!-- 那須町 -->
      <div style="background:#fff9c4; padding:3px 5px; font-size:7.5pt; font-weight:bold; color:#c47a00; margin-bottom:3px;">
        📍 那須町
      </div>
      <table style="width:100%; border-collapse:collapse;">
        <tr>
          <td style="padding:2px 3px; vertical-align:top; width:18px;">
            <span style="display:inline-block; width:14px; height:14px; background:#e65100; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">8</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">道の駅 那須高原友愛の森</div>
            <div style="font-size:7pt; color:#555;">大字高久乙593-8　☎0287-78-0233<br>9:00〜17:00</div>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 3px; vertical-align:top;">
            <span style="display:inline-block; width:14px; height:14px; background:#e65100; border-radius:50%; text-align:center; line-height:14px; color:#fff; font-size:7pt; font-weight:bold;">9</span>
          </td>
          <td style="padding:2px 3px; vertical-align:top;">
            <div style="font-size:8pt; font-weight:bold;">道の駅 東山道伊王野</div>
            <div style="font-size:7pt; color:#555;">大字伊王野459　☎0287-75-0577<br>8:30〜17:00</div>
          </td>
        </tr>
      </table>

    </td>
  </tr></tbody></table>
</div>

<!-- フッター -->
<div class="ftr" style="margin-top:8px;">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td class="ftr-co"><strong>株式会社 芹江コンチェルト</strong>　栃木県大田原市山の手1丁目7-7</td>
    <td style="text-align:right; color:#c8e6c9; font-size:7.5pt;">
      TEL：0287-33-9217　／　担当：芹江匡晋</td>
  </tr></tbody></table>
</div>

</body>
</html>"""


def main():
    out_path = os.path.join(DIR, 'panda_chokubaisho_map.pdf')
    print('直売所分布マップPDF生成中...')
    HTML(string=HTML_CONTENT).write_pdf(out_path)
    print(f'完了: {out_path}')
    return out_path


if __name__ == '__main__':
    main()
