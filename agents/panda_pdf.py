"""
Markdown → スタイル付き HTML → PDF（weasyprint）
日本語フォント：WenQuanYi ZenHei（/usr/share/fonts/truetype/wqy/）
"""

import os, sys, subprocess, glob
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

CSS = """
@font-face {
    font-family: 'Japanese';
    src: url('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}
@page {
    size: A4;
    margin: 18mm 20mm 20mm 20mm;
    @bottom-right {
        content: counter(page) ' / ' counter(pages);
        font-family: 'Japanese', sans-serif;
        font-size: 9pt;
        color: #888;
    }
}
body {
    font-family: 'Japanese', 'IPAGothic', sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #1a1a1a;
}
h1 {
    font-size: 18pt;
    color: #2c5f2e;
    border-bottom: 3px solid #2c5f2e;
    padding-bottom: 6px;
    margin-top: 0;
}
h2 {
    font-size: 13pt;
    color: #2c5f2e;
    border-left: 5px solid #2c5f2e;
    padding-left: 10px;
    margin-top: 24px;
}
h3 {
    font-size: 11.5pt;
    color: #1a3d1b;
    border-bottom: 1px solid #c8e6c9;
    padding-bottom: 3px;
    margin-top: 18px;
}
h4 {
    font-size: 10.5pt;
    color: #388e3c;
    margin-top: 12px;
    margin-bottom: 4px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 9.5pt;
}
th {
    background-color: #2c5f2e;
    color: white;
    padding: 6px 10px;
    text-align: left;
}
td {
    border: 1px solid #c8e6c9;
    padding: 5px 10px;
}
tr:nth-child(even) td {
    background-color: #f1f8e9;
}
blockquote {
    background: #f9fbe7;
    border-left: 4px solid #aed581;
    margin: 10px 0;
    padding: 8px 14px;
    font-size: 10pt;
}
ul, ol {
    margin: 6px 0;
    padding-left: 20px;
}
li {
    margin-bottom: 3px;
}
hr {
    border: none;
    border-top: 1px solid #c8e6c9;
    margin: 16px 0;
}
code {
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9pt;
}
pre {
    background: #f5f5f5;
    padding: 10px;
    border-radius: 4px;
    font-size: 9pt;
    white-space: pre-wrap;
}
p { margin: 6px 0; }
"""

def ensure_deps():
    try:
        import weasyprint
        import markdown
    except ImportError:
        print('weasyprint / markdown をインストール中...')
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--quiet', 'weasyprint', 'markdown'],
            stdout=subprocess.DEVNULL
        )
        print('インストール完了')

def find_latest_proposal():
    files = sorted(glob.glob(os.path.join(DIR, 'panda_sales_proposal_*.md')), reverse=True)
    if not files:
        raise FileNotFoundError(
            '提案書 Markdown が見つかりません。\n'
            'まず panda_proposal_generator.py を実行してください。'
        )
    return files[0]

def md_to_pdf(md_path, pdf_path):
    import markdown as md_lib
    from weasyprint import HTML, CSS as WpCSS

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html_body = md_lib.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>なんだパンダベビーカステラ 営業提案資料</title>
</head>
<body>
{html_body}
</body>
</html>"""

    HTML(string=html).write_pdf(
        pdf_path,
        stylesheets=[WpCSS(string=CSS)]
    )

def main(md_path=None):
    ensure_deps()

    if md_path is None:
        md_path = find_latest_proposal()

    pdf_path = md_path.replace('.md', '.pdf')
    print(f'PDF 生成中: {os.path.basename(md_path)} → {os.path.basename(pdf_path)}')
    md_to_pdf(md_path, pdf_path)
    print(f'PDF 生成完了: {pdf_path}')
    return pdf_path

if __name__ == '__main__':
    md_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(md_arg)
