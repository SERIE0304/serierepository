"""
panda_chokubaisho_map.py
直売所営業候補 分布地図（A4 1枚PDF・地図全幅）
"""
import os
from weasyprint import HTML

DIR = os.path.dirname(os.path.abspath(__file__))

# 地図座標計算
# lon: 139.86〜140.22 (span 0.36), lat: 36.80〜37.10 (span 0.30)
# viewBox 0 0 200 220
W, H = 200, 220
LON_MIN, LON_MAX = 139.86, 140.22
LAT_MIN, LAT_MAX = 36.80, 37.10

def x(lon): return round((lon - LON_MIN) / (LON_MAX - LON_MIN) * W, 1)
def y(lat): return round((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H, 1)

# 施設マーカー座標
M = {
    1:  (x(140.019), y(36.947)),   # なすのマルシェ       → (88, 119)
    2:  (x(140.013), y(36.895)),   # そすいの郷           → (85, 161)
    3:  (x(140.007), y(36.930)),   # 高林産直会           → (81, 132)  ← 微調整
    4:  (x(140.048), y(36.990)),   # 那須の駅             → (104, 88)
    5:  (x(139.970), y(36.975)),   # アグリパル塩原       → (61, 100)
    6:  (x(140.015), y(36.869)),   # あさか直売所         → (86, 181)
    7:  (x(140.094), y(36.909)),   # きらり佐久山         → (129, 149)
    8:  (x(140.057), y(37.030)),   # 友愛の森             → (109, 56)
    9:  (x(140.163), y(37.038)),   # 東山道伊王野         → (168, 50)
}

# 参照座標
KUR = (x(140.043), y(36.966))    # JR黒磯駅 (102, 107)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<style>
@font-face {{ font-family: 'JP'; src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'); }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'JP', sans-serif; font-size: 10pt; color: #1a1a1a; width: 210mm; }}
.hdr {{ background: #2d5a1b; padding: 10px 20px; }}
.hdr h1 {{ font-size: 14pt; color: #fff; letter-spacing: 1px; }}
.hdr .sub {{ font-size: 8pt; color: #a5d6a7; margin-top: 2px; }}
.ftr {{ background: #2d5a1b; padding: 7px 20px; }}
</style>
</head>
<body>

<!-- ヘッダー -->
<div class="hdr">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td>
      <h1>🐼 パンダベビーカステラ　直売所 分布マップ</h1>
      <div class="sub">那須塩原市・大田原市・那須町 ／ 現在の取引先を除く新規営業候補9施設</div>
    </td>
    <td style="text-align:right; color:#c8e6c9; font-size:7.5pt; vertical-align:bottom;">2026年7月23日</td>
  </tr></tbody></table>
</div>

<!-- 地図 -->
<div style="padding: 6px 20px 0;">
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%; display:block; border:1.5px solid #b0c8a0; border-radius:4px;">

  <!-- 背景（那須塩原市カラー） -->
  <rect width="{W}" height="{H}" fill="#e8f5e9"/>

  <!-- 那須町エリア（黄背景） -->
  <polygon points="38,0 {W},0 {W},108 172,100 140,85 118,46 38,0"
           fill="#fff8d6" fill-opacity="0.65"/>

  <!-- 大田原市エリア（水色背景） -->
  <polygon points="70,148 {W},118 {W},{H} 52,{H}"
           fill="#ddf0ff" fill-opacity="0.65"/>

  <!-- エリア境界線（点線） -->
  <polyline points="38,0 118,46 140,85 172,100 {W},108"
            fill="none" stroke="#c8a000" stroke-width="0.7" stroke-dasharray="3,3"/>
  <polyline points="70,148 {W},118"
            fill="none" stroke="#1565c0" stroke-width="0.7" stroke-dasharray="3,3"/>
  <polyline points="52,{H} 70,148"
            fill="none" stroke="#1565c0" stroke-width="0.7" stroke-dasharray="3,3"/>

  <!-- 那須連山（北西の山） -->
  <polygon points="2,40 14,10 26,40"  fill="#b4a494" stroke="#9a8272" stroke-width="0.6"/>
  <polygon points="14,42 27,13 40,42" fill="#c4b4a4" stroke="#9a8272" stroke-width="0.6"/>
  <polygon points="0,44 11,22 22,44"  fill="#aa9888" stroke="#9a8272" stroke-width="0.6"/>
  <text x="4" y="52" font-size="6.5" fill="#6a5a4a" font-weight="bold">那須連山</text>

  <!-- 塩原方面の山 -->
  <polygon points="0,72 9,56 18,72"  fill="#c0b0a0" stroke="#9a8272" stroke-width="0.5"/>
  <polygon points="7,75 15,61 23,75" fill="#ccc0b0" stroke="#9a8272" stroke-width="0.5"/>
  <text x="0" y="82" font-size="5.5" fill="#7a6a5a">塩原方面</text>

  <!-- 東北自動車道 -->
  <path d="M 112,0 L 118,{H}" stroke="#c8c8c8" stroke-width="2" stroke-dasharray="5,3" fill="none"/>
  <text x="106" y="10" font-size="5.5" fill="#aaa" transform="rotate(87,106,10)">東北自動車道</text>

  <!-- 国道4号（N-S 主幹線） -->
  <path d="M 90,0 L 100,107 L 88,165 L 84,{H}"
        stroke="#999" stroke-width="2.5" fill="none"/>
  <rect x="71" y="195" width="23" height="8" rx="1" fill="#fff" fill-opacity="0.7"/>
  <text x="82" y="201" font-size="5.5" fill="#777" text-anchor="middle">国道4号</text>

  <!-- 国道400号（西→塩原方面） -->
  <path d="M 100,107 Q 80,103 61,100" stroke="#bbb" stroke-width="1.5" fill="none"/>
  <text x="72" y="97" font-size="5" fill="#999">R400</text>

  <!-- 国道294号（南東→大田原） -->
  <path d="M 88,138 L 132,152" stroke="#bbb" stroke-width="1.5" fill="none"/>
  <text x="102" y="139" font-size="5" fill="#999">R294</text>

  <!-- 那珂川 -->
  <path d="M 0,194 Q 45,186 88,191 Q 135,196 {W},183"
        stroke="#6fb8dc" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <text x="6" y="202" font-size="6" fill="#5a9dc0">那珂川</text>

  <!-- JR東北本線 -->
  <path d="M 98,105 L 84,138 L 78,163"
        stroke="#444" stroke-width="1.2" fill="none" stroke-dasharray="4,2.5"/>

  <!-- JR黒磯駅 -->
  <circle cx="{KUR[0]}" cy="{KUR[1]}" r="3" fill="#444" stroke="#fff" stroke-width="0.8"/>
  <rect x="104" y="100" width="32" height="9" rx="1.5" fill="#fff" fill-opacity="0.85"/>
  <text x="120" y="107" font-size="6" fill="#333" text-anchor="middle">JR 黒磯駅</text>

  <!-- エリア名（薄い透かし） -->
  <text x="15" y="130" font-size="16" fill="#2d5a1b" font-weight="bold" opacity="0.12">那須塩原市</text>
  <text x="120" y="205" font-size="16" fill="#1565c0" font-weight="bold" opacity="0.12">大田原市</text>
  <text x="130" y="40" font-size="14" fill="#b08000" font-weight="bold" opacity="0.15">那須町</text>

  <!-- ==================== 施設マーカー ==================== -->

  <!-- ── 那須塩原市（緑） ── -->

  <!-- ① なすのマルシェ -->
  <line x1="{M[1][0]+9}" y1="{M[1][1]}" x2="{M[1][0]+22}" y2="{M[1][1]-6}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[1][0]}" cy="{M[1][1]}" r="9" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[1][0]}" y="{M[1][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">1</text>
  <text x="{M[1][0]+24}" y="{M[1][1]-9}" font-size="7" fill="#1a3a0a" font-weight="bold">なすのマルシェ</text>
  <text x="{M[1][0]+24}" y="{M[1][1]-1}" font-size="6" fill="#555">☎ 0287-74-3715</text>
  <text x="{M[1][0]+24}" y="{M[1][1]+7}" font-size="5.5" fill="#777">8:30〜16:00（火休）</text>

  <!-- ② そすいの郷 -->
  <line x1="{M[2][0]+9}" y1="{M[2][1]}" x2="{M[2][0]+22}" y2="{M[2][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[2][0]}" cy="{M[2][1]}" r="9" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[2][0]}" y="{M[2][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">2</text>
  <text x="{M[2][0]+24}" y="{M[2][1]-8}" font-size="7" fill="#1a3a0a" font-weight="bold">そすいの郷 直売センター</text>
  <text x="{M[2][0]+24}" y="{M[2][1]}" font-size="6" fill="#555">☎ 0287-37-7768</text>
  <text x="{M[2][0]+24}" y="{M[2][1]+8}" font-size="5.5" fill="#777">9:00〜16:00（元旦のみ休）</text>

  <!-- ③ 高林産直会 (ラベル左) -->
  <line x1="{M[3][0]-9}" y1="{M[3][1]}" x2="{M[3][0]-22}" y2="{M[3][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[3][0]}" cy="{M[3][1]}" r="9" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[3][0]}" y="{M[3][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">3</text>
  <text x="{M[3][0]-24}" y="{M[3][1]-8}" font-size="7" fill="#1a3a0a" font-weight="bold" text-anchor="end">高林産直会</text>
  <text x="{M[3][0]-24}" y="{M[3][1]}" font-size="6" fill="#555" text-anchor="end">☎ 0287-68-1092</text>
  <text x="{M[3][0]-24}" y="{M[3][1]+8}" font-size="5.5" fill="#777" text-anchor="end">9:00〜16:00（木休）</text>

  <!-- ④ 那須の駅 -->
  <line x1="{M[4][0]+9}" y1="{M[4][1]}" x2="{M[4][0]+22}" y2="{M[4][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[4][0]}" cy="{M[4][1]}" r="9" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[4][0]}" y="{M[4][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">4</text>
  <text x="{M[4][0]+24}" y="{M[4][1]-8}" font-size="7" fill="#1a3a0a" font-weight="bold">那須の駅 農産物直売所</text>
  <text x="{M[4][0]+24}" y="{M[4][1]}" font-size="6" fill="#555">☎ 0287-62-0034</text>

  <!-- ⑤ アグリパル塩原 (ラベル左) -->
  <line x1="{M[5][0]-9}" y1="{M[5][1]}" x2="{M[5][0]-18}" y2="{M[5][1]+10}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[5][0]}" cy="{M[5][1]}" r="9" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[5][0]}" y="{M[5][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">5</text>
  <text x="{M[5][0]-20}" y="{M[5][1]+18}" font-size="7" fill="#1a3a0a" font-weight="bold" text-anchor="end">アグリパル塩原</text>
  <text x="{M[5][0]-20}" y="{M[5][1]+26}" font-size="6" fill="#555" text-anchor="end">☎ 0287-35-4401</text>
  <text x="{M[5][0]-20}" y="{M[5][1]+34}" font-size="6" fill="#c44000" font-weight="bold" text-anchor="end">★ 申込書提出中</text>

  <!-- ── 大田原市（青） ── -->

  <!-- ⑥ あさか直売所 -->
  <line x1="{M[6][0]+9}" y1="{M[6][1]}" x2="{M[6][0]+22}" y2="{M[6][1]-5}"
        stroke="#1565c0" stroke-width="0.9"/>
  <circle cx="{M[6][0]}" cy="{M[6][1]}" r="9" fill="#1565c0" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[6][0]}" y="{M[6][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">6</text>
  <text x="{M[6][0]+24}" y="{M[6][1]-8}" font-size="7" fill="#0a2a60" font-weight="bold">あさか直売所</text>
  <text x="{M[6][0]+24}" y="{M[6][1]}" font-size="6" fill="#555">☎ 0287-22-4621</text>
  <text x="{M[6][0]+24}" y="{M[6][1]+8}" font-size="5.5" fill="#777">9:00〜17:30（無休）</text>

  <!-- ⑦ きらり佐久山 -->
  <line x1="{M[7][0]}" y1="{M[7][1]-9}" x2="{M[7][0]}" y2="{M[7][1]-22}"
        stroke="#1565c0" stroke-width="0.9"/>
  <circle cx="{M[7][0]}" cy="{M[7][1]}" r="9" fill="#1565c0" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[7][0]}" y="{M[7][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">7</text>
  <text x="{M[7][0]}" y="{M[7][1]-26}" font-size="7" fill="#0a2a60" font-weight="bold" text-anchor="middle">きらり佐久山農産物直売所</text>
  <text x="{M[7][0]}" y="{M[7][1]-18}" font-size="6" fill="#555" text-anchor="middle">☎ 0287-28-1290</text>

  <!-- ── 那須町（オレンジ） ── -->

  <!-- ⑧ 道の駅 那須高原友愛の森 -->
  <line x1="{M[8][0]}" y1="{M[8][1]+9}" x2="{M[8][0]}" y2="{M[8][1]+22}"
        stroke="#e65100" stroke-width="0.9"/>
  <circle cx="{M[8][0]}" cy="{M[8][1]}" r="9" fill="#e65100" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[8][0]}" y="{M[8][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">8</text>
  <text x="{M[8][0]}" y="{M[8][1]+31}" font-size="7" fill="#7a2400" font-weight="bold" text-anchor="middle">道の駅 那須高原</text>
  <text x="{M[8][0]}" y="{M[8][1]+39}" font-size="7" fill="#7a2400" font-weight="bold" text-anchor="middle">友愛の森</text>
  <text x="{M[8][0]}" y="{M[8][1]+47}" font-size="6" fill="#555" text-anchor="middle">☎ 0287-78-0233</text>

  <!-- ⑨ 道の駅 東山道伊王野 -->
  <line x1="{M[9][0]-9}" y1="{M[9][1]}" x2="{M[9][0]-22}" y2="{M[9][1]}"
        stroke="#e65100" stroke-width="0.9"/>
  <circle cx="{M[9][0]}" cy="{M[9][1]}" r="9" fill="#e65100" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[9][0]}" y="{M[9][1]+4}" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">9</text>
  <text x="{M[9][0]-24}" y="{M[9][1]-8}" font-size="7" fill="#7a2400" font-weight="bold" text-anchor="end">道の駅 東山道伊王野</text>
  <text x="{M[9][0]-24}" y="{M[9][1]}" font-size="6" fill="#555" text-anchor="end">☎ 0287-75-0577</text>
  <text x="{M[9][0]-24}" y="{M[9][1]+8}" font-size="5.5" fill="#777" text-anchor="end">8:30〜17:00</text>

  <!-- ==================== 凡例・補足 ==================== -->
  <rect x="2" y="{H-28}" width="82" height="26" rx="3" fill="#fff" fill-opacity="0.85" stroke="#c8e6c9" stroke-width="0.8"/>
  <circle cx="10" cy="{H-20}" r="5" fill="#2d5a1b"/>
  <text x="18" y="{H-16}" font-size="6.5" fill="#2d5a1b" font-weight="bold">那須塩原市　①〜⑤</text>
  <circle cx="10" cy="{H-10}" r="5" fill="#1565c0"/>
  <text x="18" y="{H-6}" font-size="6.5" fill="#1565c0" font-weight="bold">大田原市　⑥⑦</text>
  <circle cx="51" cy="{H-10}" r="5" fill="#e65100"/>
  <text x="59" y="{H-6}" font-size="6.5" fill="#e65100" font-weight="bold">那須町　⑧⑨</text>

  <!-- 北向き矢印 -->
  <polygon points="{W-6},{H-26} {W-10},{H-16} {W-6},{H-19} {W-2},{H-16}" fill="#555"/>
  <text x="{W-6}" y="{H-28}" font-size="7" fill="#555" text-anchor="middle">N</text>

  <!-- スケールバー（約5km） -->
  <line x1="{W-55}" y1="{H-6}" x2="{W-20}" y2="{H-6}" stroke="#666" stroke-width="1.2"/>
  <line x1="{W-55}" y1="{H-9}" x2="{W-55}" y2="{H-3}" stroke="#666" stroke-width="1.2"/>
  <line x1="{W-20}" y1="{H-9}" x2="{W-20}" y2="{H-3}" stroke="#666" stroke-width="1.2"/>
  <text x="{W-37}" y="{H-1}" font-size="5.5" fill="#666" text-anchor="middle">約5km</text>

  <!-- 注記 -->
  <text x="{W}" y="{H-1}" font-size="5" fill="#aaa" text-anchor="end">※概略図。境界・道路は簡略化</text>

</svg>
</div>

<!-- フッター -->
<div class="ftr" style="margin-top:6px;">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td style="color:#c8e6c9; font-size:8pt;"><strong style="color:#fff; font-size:9pt;">株式会社 芹江コンチェルト</strong>　栃木県大田原市山の手1丁目7-7</td>
    <td style="text-align:right; color:#c8e6c9; font-size:7.5pt;">TEL：0287-33-9217　／　担当：芹江匡晋</td>
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
