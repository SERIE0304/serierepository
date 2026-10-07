#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
体重・体脂肪率の推移グラフを生成する（misaki_weight_chart_v5.html 準拠デザイン）

使い方（CLI）:
    python3 generate_weight_chart.py data.json output.png

呼び出し（モジュール）:
    from generate_weight_chart import render_weight_chart
    render_weight_chart(data_dict, "output.png")
"""
import json
import sys
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import MaxNLocator

_FONT_ENV = os.environ.get("JP_FONT_PATH")
_FONT_CANDIDATES = [p for p in [
    _FONT_ENV,
    os.path.join(os.path.dirname(__file__), "fonts", "NotoSansJP-Regular.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
] if p]
_BOLD_CANDIDATES = [p for p in [
    os.environ.get("JP_FONT_BOLD_PATH"),
    os.path.join(os.path.dirname(__file__), "fonts", "NotoSansJP-Bold.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
] if p]

def _first_existing(paths, fallback):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return fallback

JP_FONT_PATH = _first_existing(_FONT_CANDIDATES, _FONT_CANDIDATES[0])
JP_FONT_BOLD = _first_existing(_BOLD_CANDIDATES, _BOLD_CANDIDATES[0])
jp_font = fm.FontProperties(fname=JP_FONT_PATH)
jp_bold = fm.FontProperties(fname=JP_FONT_BOLD)

# ---- misaki_weight_chart_v5.html 準拠カラー ----
BLUE = "#3B82C4"        # 体重ライン
GREEN = "#2E9E5B"       # 体脂肪率ライン
RED = "#E74C3C"         # 目標ライン
LAVENDER = "#B9A8E0"    # メンテナンス期間の網かけ
CARD_BG = "#F7F7F9"
CARD_BORDER = "#E4E4EA"
CREAM = "#FFFFFF"
GRAY_TEXT = "#555555"
GRAY_LABEL = "#8A8A8A"


def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def draw_card(ax, x, w, label, value, sub, value_color):
    ax.add_patch(plt.Rectangle((x, 0), w, 1, facecolor=CARD_BG,
                                edgecolor=CARD_BORDER, linewidth=1.2,
                                transform=ax.transAxes, clip_on=False))
    ax.text(x + 0.02, 0.72, label, transform=ax.transAxes,
             fontproperties=jp_font, fontsize=10.5, color=GRAY_LABEL)
    ax.text(x + 0.02, 0.30, value, transform=ax.transAxes,
             fontproperties=jp_bold, fontsize=19, color=value_color)
    ax.text(x + 0.02, 0.08, sub, transform=ax.transAxes,
             fontproperties=jp_font, fontsize=9.5, color=GRAY_LABEL)


def render_weight_chart(data: dict, out_path: str) -> str:
    client_name = data.get("client_name", "")
    target = data.get("target_weight")
    records = [r for r in data.get("records", []) if r.get("weight") is not None]
    records.sort(key=lambda r: r["date"])

    if not records:
        raise ValueError("records が空です")

    dates = [parse_date(r["date"]) for r in records]
    weights = [r["weight"] for r in records]
    body_fats = [r.get("body_fat") for r in records]

    start_w, start_d = weights[0], records[0]["date"]
    max_w = max(weights)
    max_idx = weights.index(max_w)
    min_w = min(weights)
    min_idx = weights.index(min_w)
    latest_is_new_low = (min_idx == len(weights) - 1)
    remain = round(min_w - target, 1) if target else None

    fig = plt.figure(figsize=(11, 7.2), dpi=200)
    fig.patch.set_facecolor(CREAM)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 5.2], hspace=0.28)

    card_ax = fig.add_subplot(gs[0])
    card_ax.axis("off")
    card_ax.set_xlim(0, 1)
    card_ax.set_ylim(0, 1)
    gap = 0.02
    w = (1 - gap * 3) / 4
    xs = [i * (w + gap) for i in range(4)]

    def fmt_date(s):
        return f"{int(s[5:7])}/{int(s[8:10])}"

    draw_card(card_ax, xs[0], w, "スタート体重", f"{start_w} kg", fmt_date(start_d), "#222222")
    draw_card(card_ax, xs[1], w, "最高値", f"{max_w} kg", fmt_date(records[max_idx]["date"]), RED)
    min_sub = fmt_date(records[min_idx]["date"]) + (" NEW!" if latest_is_new_low else "")
    draw_card(card_ax, xs[2], w, "最軽量 ▼", f"{min_w} kg", min_sub, GREEN)
    if target:
        draw_card(card_ax, xs[3], w, "目標体重", f"{target} kg",
                   f"残り {remain} kg" if remain and remain > 0 else "達成🎉", "#C0392B")

    ax1 = fig.add_subplot(gs[1])
    ax1.set_facecolor(CREAM)

    for period in data.get("maintenance_periods", []):
        s = parse_date(period["start"])
        e = parse_date(period["end"])
        ax1.axvspan(s, e, color=LAVENDER, alpha=0.25, zorder=0)
        mid = s + (e - s) / 2
        ax1.text(mid, 1.01, period.get("label", ""), transform=ax1.get_xaxis_transform(),
                  ha="center", va="bottom", fontproperties=jp_font, fontsize=9, color="#8B7BB8")

    ax1.plot(dates, weights, color=BLUE, linewidth=2.2, marker="o",
              markersize=5, markerfacecolor=BLUE, markeredgecolor=BLUE, zorder=3)
    ax1.scatter([dates[max_idx]], [max_w], s=150, color=RED, zorder=5,
                edgecolor="white", linewidth=1.5)
    ax1.scatter([dates[min_idx]], [min_w], s=150, color=GREEN, zorder=5,
                edgecolor="white", linewidth=1.5)

    if target:
        ax1.axhline(target, color=RED, linestyle="--", linewidth=1.6, zorder=2)

    ax1.set_ylabel("体重（kg）", fontproperties=jp_font, fontsize=11, color=GRAY_TEXT)
    ax1.yaxis.set_major_locator(MaxNLocator(8))
    for label in ax1.get_yticklabels():
        label.set_fontproperties(jp_font)
        label.set_color(BLUE)

    fat_dates = [d for d, f in zip(dates, body_fats) if f is not None]
    fat_vals = [f for f in body_fats if f is not None]
    if fat_vals:
        ax2 = ax1.twinx()
        ax2.plot(fat_dates, fat_vals, color=GREEN, linewidth=2.0,
                  marker="o", markersize=4.5, markerfacecolor=GREEN,
                  markeredgecolor=GREEN, zorder=3)
        ax2.set_ylabel("体脂肪率（%）", fontproperties=jp_font, fontsize=11, color=GRAY_TEXT)
        ax2.tick_params(axis="y", colors=GREEN)
        for label in ax2.get_yticklabels():
            label.set_fontproperties(jp_font)
            label.set_color(GREEN)
        ax2.spines["top"].set_visible(False)

    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], color=BLUE, lw=2.2, marker="o", label="体重"),
        Line2D([0], [0], color=GREEN, lw=2.2, marker="o", label="体脂肪率"),
        Line2D([0], [0], color=RED, lw=1.6, linestyle="--", label=f"目標 {target}kg" if target else "目標"),
        plt.Rectangle((0, 0), 1, 1, facecolor=LAVENDER, alpha=0.4, label="メンテナンス期間"),
    ]
    ax1.legend(handles=legend_items, loc="upper left", bbox_to_anchor=(0, 1.12),
                ncol=4, frameon=False, prop=jp_font, fontsize=10)

    fig.autofmt_xdate(rotation=0)
    for label in ax1.get_xticklabels():
        label.set_fontproperties(jp_font)
        label.set_fontsize(9)
        label.set_color(GRAY_TEXT)
        label.set_ha("center")

    ax1.spines["top"].set_visible(False)
    ax1.spines["left"].set_color(BLUE)
    ax1.spines["bottom"].set_color("#CCCCCC")
    ax1.grid(axis="y", color="#EDEDED", linewidth=0.8, zorder=0)

    title = f"{client_name} 体重推移" if client_name else "体重推移"
    fig.suptitle(title, fontproperties=jp_bold, fontsize=18, color="#222222", y=0.985)

    footnote = data.get("footnote")
    if footnote is None:
        parts = ["データなし日は線で補間", "体脂肪率は右軸"]
        for r in records:
            if r.get("body_fat_excluded_reason"):
                parts.append(f"{r['date'][5:7]}/{r['date'][8:10]}の体脂肪は{r['body_fat_excluded_reason']}のため除外")
        footnote = "※ " + " ／ ".join(parts)
    fig.text(0.5, 0.008, footnote, ha="center", fontproperties=jp_font,
              fontsize=8.5, color=GRAY_LABEL)

    plt.savefig(out_path, facecolor=CREAM, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main():
    if len(sys.argv) < 3:
        print("usage: generate_weight_chart.py data.json output.png")
        sys.exit(1)
    data = load_data(sys.argv[1])
    render_weight_chart(data, sys.argv[2])
    print(f"saved: {sys.argv[2]}")


if __name__ == "__main__":
    main()
