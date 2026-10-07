# -*- coding: utf-8 -*-
"""
本日(2026-10-06/07)のセッションで処理した receipts.jsonl（151件）と、
手動で追加した調整項目（元入金・各月補充・4件の確定修正）を、
今後の自動パイプラインが参照する唯一の正 ledger.jsonl に統合する、
一回限りの移行スクリプト。

実行後は ledger.jsonl が Single Source of Truth になり、
このスクリプトは再実行しない。
"""
import json
import os

SOURCE_JSONL = r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user\5b3797b9-90ef-42a3-8f20-491d3a314d8e\scratchpad\receipts.jsonl"
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "ledger.jsonl")

# 2026-07-02/03 に元々入力済みだった4件（Excelテンプレートにハードコードされていたもの）。
# 今後 ledger.jsonl だけから全シートを再構築できるよう、ここにも正式に記録する。
PRE_EXISTING_JULY_ENTRIES = [
    {"date": "2026-07-02", "category": "消耗品費", "store": "セリア 大田原住吉店",
     "items": "消臭バッグ 等", "reg": "T4200001013662", "amount": 220,
     "status": "new", "source": "pre_existing"},
    {"date": "2026-07-02", "category": "消耗品費", "store": "TRIAL 大田原店",
     "items": "天然水 等（プリカ・ポイント払い）", "reg": "T9290001072902", "amount": 1334,
     "status": "new", "source": "pre_existing"},
    {"date": "2026-07-02", "category": "車両費", "store": "ハヤシ自動車工業",
     "items": "部品・消耗品", "reg": "T7060002025561", "amount": 9743,
     "status": "new", "source": "pre_existing"},
    {"date": "2026-07-03", "category": "消耗品費", "store": "TRIAL 那須塩原店",
     "items": "天然水・食品・ウェットティッシュ 等（プリカ・ポイント払い）", "reg": None, "amount": 1721,
     "status": "new", "source": "pre_existing"},
]

# ユーザー指示による入金（元入金 20万円、7〜9月は毎月1日に20万円補充、10月は補充なし）
DEPOSITS = [
    {"date": "2026-07-01", "amount": 200000, "summary_override": "現金補充（元入金）"},
    {"date": "2026-08-01", "amount": 200000, "summary_override": "現金補充（元入金）"},
    {"date": "2026-09-01", "amount": 200000, "summary_override": "現金補充（元入金）"},
]

with open(SOURCE_JSONL, encoding="utf-8") as f:
    records = [json.loads(line) for line in f if line.strip()]

ledger = []

for e in PRE_EXISTING_JULY_ENTRIES:
    ledger.append({
        "date": e["date"], "is_income": False, "category": e["category"],
        "store": e["store"], "items": e["items"], "reg": e["reg"], "amount": e["amount"],
        "status": e["status"], "note": None, "file": None, "source": e["source"],
    })

for d in DEPOSITS:
    ledger.append({
        "date": d["date"], "is_income": True, "category": "", "store": None, "items": None,
        "reg": None, "amount": d["amount"], "status": "new", "note": None, "file": None,
        "source": "manual_deposit", "summary_override": d["summary_override"],
    })

included = 0
for r in records:
    if r["status"] not in ("new", "needs_review"):
        continue
    if not r.get("date") or r["date"] <= "2026-07-03":
        continue
    if r.get("amount") is None:
        continue
    ledger.append({
        "date": r["date"], "is_income": False, "category": r["category"],
        "store": r["store"], "items": r.get("items"), "reg": r.get("reg"), "amount": r["amount"],
        "status": r["status"], "note": r.get("note"), "file": r.get("file"),
        "source": "line_manual_2026_10_06",
    })
    included += 1

ledger.sort(key=lambda x: (x["date"], x.get("file") or ""))

with open(LEDGER_PATH, "w", encoding="utf-8") as f:
    for row in ledger:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"migrated: {included} receipt entries + {len(PRE_EXISTING_JULY_ENTRIES)} pre-existing + {len(DEPOSITS)} deposits")
print(f"total ledger rows: {len(ledger)}")
print(f"written to: {LEDGER_PATH}")
