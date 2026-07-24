"""
panda_chokubaisho_map.py
直売所営業候補 分布地図（A4 1枚PDF・住所ベース正確座標）
"""
import os
from weasyprint import HTML

DIR = os.path.dirname(os.path.abspath(__file__))

# 座標系：実住所に基づき正確に配置
W, H = 220, 240
LON_MIN, LON_MAX = 139.84, 140.26   # 経度範囲（0.42°）
LAT_MIN, LAT_MAX = 36.78, 37.12    # 緯度範囲（0.34°）

def x(lon): return round((lon - LON_MIN) / (LON_MAX - LON_MIN) * W, 1)
def y(lat): return round((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H, 1)

# 施設座標（実住所ジオコード）
M = {
    1: (x(140.018), y(36.960)),  # なすのマルシェ　那須塩原市下厚崎 (93.0, 113.0)
    2: (x(140.012), y(36.893)),  # そすいの郷　那須塩原市三区町     (90.0, 159.8)
    3: (x(140.005), y(36.929)),  # 高林産直会　那須塩原市木綿畑     (86.4, 134.3)
    4: (x(140.051), y(36.992)),  # 那須の駅　那須塩原市鍋掛         (110.5, 90.4)
    5: (x(139.972), y(36.977)),  # アグリパル塩原　那須塩原市関谷   (69.5, 101.2)
    6: (x(140.016), y(36.871)),  # あさか直売所　大田原市浅香       (92.1, 175.4)
    7: (x(140.096), y(36.908)),  # きらり佐久山　大田原市佐久山     (133.7, 149.4)
    8: (x(140.057), y(37.031)),  # 友愛の森　那須町高久乙            (113.7, 62.8)
    9: (x(140.163), y(37.038)),  # 東山道伊王野　那須町伊王野        (169.0, 57.9)
}

# 地理参照点
KUR  = (x(140.043), y(36.967))   # JR黒磯駅      (106.1, 108.0)
NISI = (x(140.024), y(36.888))   # JR西那須野駅  (95.8, 162.4)
OTA  = (x(140.017), y(36.872))   # 大田原市中心  (92.4, 174.2)
NASUIC = (x(140.047), y(37.019)) # 那須IC        (108.5, 70.1)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<style>
@font-face {{ font-family: 'JP'; src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'); }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'JP', sans-serif; color: #1a1a1a; width: 210mm; }}
.hdr {{ background: #2d5a1b; padding: 10px 20px; }}
.hdr h1 {{ font-size: 14pt; color: #fff; letter-spacing: 1px; }}
.hdr .sub {{ font-size: 8pt; color: #a5d6a7; margin-top: 2px; }}
.ftr {{ background: #2d5a1b; padding: 7px 20px; }}
</style>
</head>
<body>

<div class="hdr">
  <table style="width:100%; border-collapse:collapse;"><tbody><tr>
    <td>
      <h1>🐼 パンダベビーカステラ　直売所 分布マップ（新規営業候補）</h1>
      <div class="sub">那須塩原市・大田原市・那須町 ／ 現在の取引先を除く新規候補9施設　※取引中：道の駅明治の森・那須の与一の郷・トコトコ大田原 を除く</div>
    </td>
    <td style="text-align:right; color:#c8e6c9; font-size:7.5pt; vertical-align:bottom;">2026年7月</td>
  </tr></tbody></table>
</div>

<div style="padding: 5px 18px 0;">
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%; display:block; border:1.5px solid #b0c8a0; border-radius:4px;">

  <!-- ===== 背景・エリア色 ===== -->
  <rect width="{W}" height="{H}" fill="#f0f4f0"/>

  <!-- 那須塩原市エリア（薄緑） -->
  <polygon points="0,0 {W},0 {W},124 165,115 135,90 118,65 95,44 45,20 0,30"
           fill="#d4ead4" fill-opacity="0.7"/>

  <!-- 那須町エリア（薄黄） -->
  <polygon points="45,20 95,44 118,65 135,90 165,115 {W},124 {W},0 45,0"
           fill="#fffacc" fill-opacity="0.6"/>

  <!-- 大田原市エリア（薄水色） -->
  <polygon points="75,158 {W},128 {W},{H} 55,{H}"
           fill="#d8eef8" fill-opacity="0.7"/>

  <!-- エリア境界 -->
  <polyline points="0,30 45,20 95,44 118,65 135,90 165,115 {W},124"
            fill="none" stroke="#b8a820" stroke-width="0.8" stroke-dasharray="4,3"/>
  <polyline points="55,{H} 75,158 {W},128"
            fill="none" stroke="#1a6aaa" stroke-width="0.8" stroke-dasharray="4,3"/>

  <!-- ===== 那須連山・地形 ===== -->
  <polygon points="3,36 13,8 23,36"  fill="#bca898" stroke="#9a7a62" stroke-width="0.6"/>
  <polygon points="11,38 22,10 33,38" fill="#cbb8a8" stroke="#9a7a62" stroke-width="0.6"/>
  <polygon points="20,40 30,16 40,40" fill="#c2ac98" stroke="#9a7a62" stroke-width="0.6"/>
  <text x="3" y="48" font-size="6" fill="#6a5040" font-weight="bold">那須連山</text>

  <!-- 塩原方面 -->
  <polygon points="0,72 8,54 16,72"  fill="#c0afa0" stroke="#9a8070" stroke-width="0.5"/>
  <polygon points="7,74 14,60 21,74" fill="#cabaa8" stroke="#9a8070" stroke-width="0.5"/>
  <text x="0" y="83" font-size="5.5" fill="#7a6858">塩原温泉→</text>

  <!-- ===== 道路 ===== -->
  <!-- 東北自動車道 -->
  <path d="M 120,0 L 126,{H}" stroke="#d0c080" stroke-width="2.5" stroke-dasharray="6,3" fill="none"/>
  <text x="114" y="11" font-size="5.5" fill="#b0a060" transform="rotate(87,114,11)">東北自動車道</text>

  <!-- 那須IC -->
  <rect x="{NASUIC[0]-5}" y="{NASUIC[1]-4}" width="22" height="8" rx="1.5" fill="#e8d840" fill-opacity="0.9" stroke="#b8a000" stroke-width="0.6"/>
  <text x="{NASUIC[0]+6}" y="{NASUIC[1]+2}" font-size="5.5" fill="#5a4a00" text-anchor="middle">那須IC</text>

  <!-- 国道4号 -->
  <path d="M 100,0 L 107,108 L 93,166 L 89,{H}"
        stroke="#aaa" stroke-width="3" fill="none" stroke-linecap="round"/>
  <rect x="73" y="210" width="24" height="8" rx="1.5" fill="#fff" fill-opacity="0.8"/>
  <text x="85" y="216" font-size="5.5" fill="#777" text-anchor="middle">国道4号</text>

  <!-- 国道400号（黒磯→塩原） -->
  <path d="M 107,108 Q 88,104 70,102" stroke="#ccc" stroke-width="1.8" fill="none"/>
  <text x="82" y="98" font-size="5" fill="#aaa">R400</text>

  <!-- 国道294号（黒磯→大田原） -->
  <path d="M 96,142 L 140,158" stroke="#ccc" stroke-width="1.8" fill="none"/>
  <text x="110" y="144" font-size="5" fill="#aaa">R294</text>

  <!-- 国道400号（西那須野→那須） -->
  <path d="M 95,160 L 108,108 L 113,63" stroke="#ccc" stroke-width="1.5" fill="none" stroke-dasharray="3,2"/>

  <!-- 那珂川 -->
  <path d="M 0,202 Q 50,194 93,199 Q 140,204 {W},190"
        stroke="#70b8dc" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <text x="8" y="208" font-size="6" fill="#5a9dc0">那珂川</text>

  <!-- JR東北本線 -->
  <path d="M 103,105 L 90,145 L 83,170"
        stroke="#555" stroke-width="1.3" fill="none" stroke-dasharray="5,3"/>

  <!-- ===== 地理参照点 ===== -->

  <!-- JR黒磯駅 -->
  <circle cx="{KUR[0]}" cy="{KUR[1]}" r="3.5" fill="#333" stroke="#fff" stroke-width="0.8"/>
  <rect x="{KUR[0]+4}" y="{KUR[1]-6}" width="34" height="10" rx="2" fill="#fff" fill-opacity="0.9" stroke="#bbb" stroke-width="0.6"/>
  <text x="{KUR[0]+21}" y="{KUR[1]+1}" font-size="6.5" fill="#222" text-anchor="middle">JR 黒磯駅</text>

  <!-- JR西那須野駅 -->
  <circle cx="{NISI[0]}" cy="{NISI[1]}" r="3" fill="#333" stroke="#fff" stroke-width="0.8"/>
  <rect x="{NISI[0]+4}" y="{NISI[1]-5}" width="36" height="9" rx="2" fill="#fff" fill-opacity="0.9" stroke="#bbb" stroke-width="0.6"/>
  <text x="{NISI[0]+22}" y="{NISI[1]+1}" font-size="5.5" fill="#333" text-anchor="middle">JR 西那須野駅</text>

  <!-- ===== エリア名 透かし ===== -->
  <text x="10" y="145" font-size="18" fill="#2d7a2d" font-weight="bold" opacity="0.10">那須塩原市</text>
  <text x="135" y="230" font-size="16" fill="#1a55aa" font-weight="bold" opacity="0.10">大田原市</text>
  <text x="138" y="38" font-size="15" fill="#a08000" font-weight="bold" opacity="0.14">那須町</text>

  <!-- ===== 施設マーカー（r=7、重なり回避済み） ===== -->

  <!-- ───── 那須塩原市 ①〜⑤（緑） ───── -->

  <!-- ① なすのマルシェ：那須塩原市下厚崎／黒磯駅西南 → ラベル左上 -->
  <line x1="{M[1][0]-5}" y1="{M[1][1]-5}" x2="77" y2="95"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[1][0]}" cy="{M[1][1]}" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[1][0]}" y="{M[1][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">1</text>
  <text x="75" y="87" font-size="6.5" fill="#1a3a0a" font-weight="bold" text-anchor="end">なすのマルシェ</text>
  <text x="75" y="95" font-size="5.5" fill="#555" text-anchor="end">☎ 0287-74-3715</text>
  <text x="75" y="102" font-size="5" fill="#777" text-anchor="end">8:30〜16:00（火休）</text>

  <!-- ② そすいの郷：那須塩原市三区町／西那須野地区 → ラベル右 -->
  <line x1="{M[2][0]+7}" y1="{M[2][1]}" x2="{M[2][0]+18}" y2="{M[2][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[2][0]}" cy="{M[2][1]}" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[2][0]}" y="{M[2][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">2</text>
  <text x="{M[2][0]+20}" y="{M[2][1]-8}" font-size="6.5" fill="#1a3a0a" font-weight="bold">そすいの郷 直売センター</text>
  <text x="{M[2][0]+20}" y="{M[2][1]}" font-size="5.5" fill="#555">☎ 0287-37-7768</text>
  <text x="{M[2][0]+20}" y="{M[2][1]+8}" font-size="5" fill="#777">9:00〜16:00（元旦のみ休）</text>

  <!-- ③ 高林産直会：那須塩原市木綿畑 → ラベル左 -->
  <line x1="{M[3][0]-7}" y1="{M[3][1]}" x2="{M[3][0]-18}" y2="{M[3][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[3][0]}" cy="{M[3][1]}" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[3][0]}" y="{M[3][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">3</text>
  <text x="{M[3][0]-20}" y="{M[3][1]-8}" font-size="6.5" fill="#1a3a0a" font-weight="bold" text-anchor="end">高林産直会</text>
  <text x="{M[3][0]-20}" y="{M[3][1]}" font-size="5.5" fill="#555" text-anchor="end">☎ 0287-68-1092</text>
  <text x="{M[3][0]-20}" y="{M[3][1]+8}" font-size="5" fill="#777" text-anchor="end">9:00〜16:00（木休）</text>

  <!-- ④ 那須の駅：那須塩原市鍋掛／黒田原方面 → ラベル右 -->
  <line x1="{M[4][0]+7}" y1="{M[4][1]}" x2="{M[4][0]+18}" y2="{M[4][1]-5}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[4][0]}" cy="{M[4][1]}" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[4][0]}" y="{M[4][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">4</text>
  <text x="{M[4][0]+20}" y="{M[4][1]-8}" font-size="6.5" fill="#1a3a0a" font-weight="bold">那須の駅 農産物直売所</text>
  <text x="{M[4][0]+20}" y="{M[4][1]}" font-size="5.5" fill="#555">☎ 0287-62-0034</text>

  <!-- ⑤ アグリパル塩原：那須塩原市関谷／R400沿い → ラベル左下 -->
  <line x1="{M[5][0]-7}" y1="{M[5][1]}" x2="{M[5][0]-16}" y2="{M[5][1]+10}"
        stroke="#2d5a1b" stroke-width="0.9"/>
  <circle cx="{M[5][0]}" cy="{M[5][1]}" r="7" fill="#2d5a1b" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[5][0]}" y="{M[5][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">5</text>
  <text x="{M[5][0]-18}" y="{M[5][1]+18}" font-size="6.5" fill="#1a3a0a" font-weight="bold" text-anchor="end">アグリパル塩原</text>
  <text x="{M[5][0]-18}" y="{M[5][1]+26}" font-size="5.5" fill="#555" text-anchor="end">☎ 0287-35-4401</text>
  <text x="{M[5][0]-18}" y="{M[5][1]+34}" font-size="5.5" fill="#c44000" font-weight="bold" text-anchor="end">★ 申込書提出中</text>

  <!-- ───── 大田原市 ⑥⑦（青） ───── -->

  <!-- ⑥ あさか直売所：大田原市浅香／大田原市街地 → ラベル左 -->
  <line x1="{M[6][0]-7}" y1="{M[6][1]}" x2="{M[6][0]-18}" y2="{M[6][1]-5}"
        stroke="#1565c0" stroke-width="0.9"/>
  <circle cx="{M[6][0]}" cy="{M[6][1]}" r="7" fill="#1565c0" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[6][0]}" y="{M[6][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">6</text>
  <text x="{M[6][0]-20}" y="{M[6][1]-8}" font-size="6.5" fill="#0a2060" font-weight="bold" text-anchor="end">あさか直売所</text>
  <text x="{M[6][0]-20}" y="{M[6][1]}" font-size="5.5" fill="#555" text-anchor="end">☎ 0287-22-4621</text>
  <text x="{M[6][0]-20}" y="{M[6][1]+8}" font-size="5" fill="#777" text-anchor="end">9:00〜17:30（無休）</text>

  <!-- ⑦ きらり佐久山：大田原市佐久山／大田原市北部 → ラベル上 -->
  <line x1="{M[7][0]}" y1="{M[7][1]-7}" x2="{M[7][0]}" y2="{M[7][1]-20}"
        stroke="#1565c0" stroke-width="0.9"/>
  <circle cx="{M[7][0]}" cy="{M[7][1]}" r="7" fill="#1565c0" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[7][0]}" y="{M[7][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">7</text>
  <text x="{M[7][0]}" y="{M[7][1]-24}" font-size="6.5" fill="#0a2060" font-weight="bold" text-anchor="middle">きらり佐久山農産物直売所</text>
  <text x="{M[7][0]}" y="{M[7][1]-16}" font-size="5.5" fill="#555" text-anchor="middle">☎ 0287-28-1290</text>

  <!-- ───── 那須町 ⑧⑨（オレンジ） ───── -->

  <!-- ⑧ 友愛の森：那須町高久乙／那須IC近く → ラベル左 -->
  <line x1="{M[8][0]-7}" y1="{M[8][1]}" x2="{M[8][0]-20}" y2="{M[8][1]}"
        stroke="#e65100" stroke-width="0.9"/>
  <circle cx="{M[8][0]}" cy="{M[8][1]}" r="7" fill="#e65100" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[8][0]}" y="{M[8][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">8</text>
  <text x="{M[8][0]-22}" y="{M[8][1]-8}" font-size="6.5" fill="#7a2000" font-weight="bold" text-anchor="end">道の駅 那須高原</text>
  <text x="{M[8][0]-22}" y="{M[8][1]}" font-size="6.5" fill="#7a2000" font-weight="bold" text-anchor="end">友愛の森</text>
  <text x="{M[8][0]-22}" y="{M[8][1]+8}" font-size="5.5" fill="#555" text-anchor="end">☎ 0287-78-0233</text>
  <text x="{M[8][0]-22}" y="{M[8][1]+16}" font-size="5" fill="#777" text-anchor="end">9:00〜17:00</text>

  <!-- ⑨ 東山道伊王野：那須町伊王野／那須町東部 → ラベル上 -->
  <line x1="{M[9][0]}" y1="{M[9][1]-7}" x2="{M[9][0]}" y2="24"
        stroke="#e65100" stroke-width="0.9"/>
  <circle cx="{M[9][0]}" cy="{M[9][1]}" r="7" fill="#e65100" stroke="#fff" stroke-width="1.5"/>
  <text x="{M[9][0]}" y="{M[9][1]+3}" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">9</text>
  <text x="{M[9][0]}" y="15" font-size="6.5" fill="#7a2000" font-weight="bold" text-anchor="middle">道の駅 東山道伊王野</text>
  <text x="{M[9][0]}" y="23" font-size="5.5" fill="#555" text-anchor="middle">☎ 0287-75-0577</text>
  <text x="{M[9][0]}" y="31" font-size="5" fill="#777" text-anchor="middle">8:30〜17:00</text>

  <!-- ===== 凡例 ===== -->
  <rect x="2" y="{H-30}" width="88" height="28" rx="3" fill="#fff" fill-opacity="0.88" stroke="#ccd8cc" stroke-width="0.8"/>
  <circle cx="10" cy="{H-22}" r="5" fill="#2d5a1b"/>
  <text x="18" y="{H-18}" font-size="6.5" fill="#2d5a1b" font-weight="bold">那須塩原市　①〜⑤</text>
  <circle cx="10" cy="{H-11}" r="5" fill="#1565c0"/>
  <text x="18" y="{H-7}" font-size="6.5" fill="#1565c0" font-weight="bold">大田原市　⑥⑦</text>
  <circle cx="54" cy="{H-11}" r="5" fill="#e65100"/>
  <text x="62" y="{H-7}" font-size="6.5" fill="#e65100" font-weight="bold">那須町　⑧⑨</text>

  <!-- 北向き矢印 -->
  <polygon points="{W-6},{H-28} {W-10},{H-18} {W-6},{H-21} {W-2},{H-18}" fill="#555"/>
  <text x="{W-6}" y="{H-30}" font-size="7" fill="#555" text-anchor="middle">N</text>

  <!-- スケールバー（約5km） -->
  <line x1="{W-58}" y1="{H-7}" x2="{W-22}" y2="{H-7}" stroke="#666" stroke-width="1.2"/>
  <line x1="{W-58}" y1="{H-10}" x2="{W-58}" y2="{H-4}" stroke="#666" stroke-width="1.2"/>
  <line x1="{W-22}" y1="{H-10}" x2="{W-22}" y2="{H-4}" stroke="#666" stroke-width="1.2"/>
  <text x="{W-40}" y="{H-1}" font-size="5.5" fill="#666" text-anchor="middle">約5km</text>

  <!-- 注記 -->
  <text x="{W}" y="{H-1}" font-size="5" fill="#aaa" text-anchor="end">※概略図。取引中の施設（明治の森・与一の郷・トコトコ大田原）は除く</text>

</svg>
</div>

<div class="ftr" style="margin-top:5px;">
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
