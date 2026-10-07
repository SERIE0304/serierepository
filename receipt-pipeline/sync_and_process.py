# -*- coding: utf-8 -*-
"""
1時間おき（Windowsタスクスケジューラ）に実行される本体スクリプト。

1. GCS receipts/ から新着画像を 領収書フォルダへ同期
2. 新着分だけ Claude で OCR 抽出
3. ledger.jsonl に追記
4. ledger.jsonl 全体から現金出納帳.xlsx を再構築（Desktop\\領収書 と Downloads の両方）
5. 取り込んだ画像を「日付_勘定科目_店名_金額円.jpg」にリネーム

どの一歩が失敗しても、ログに残して次回実行時にリカバリできるようにする。
一度ダウンロード済み（synced_objects.txtに記録済み）のGCSオブジェクトは
再ダウンロードしない。処理対象は「このセッションで新しくダウンロードした分」
のみとし、フォルダ全体の再スキャンは行わない（既存のリネーム済みファイルを
誤って再処理しないため）。
"""
import json
import os
import re
import sys
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import gcs_sync
import ocr
from excel_builder import build_workbook

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "ledger.jsonl")
LOG_PATH = os.path.join(os.path.dirname(__file__), "run_log.txt")
XLSX_OUT_1 = r"C:\Users\user\Desktop\領収書\現金出納帳_セリエコンチェルト (1).xlsx"
XLSX_OUT_2 = r"C:\Users\user\Downloads\現金出納帳_セリエコンチェルト (1).xlsx"

INVALID_CHARS = r'\/:*?"<>|'


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sanitize(s):
    if not s:
        return ""
    s = str(s)
    for ch in INVALID_CHARS:
        s = s.replace(ch, "")
    s = s.replace("\u3000", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:40]


def append_ledger(record: dict) -> None:
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def rename_image(local_path: str, record: dict) -> None:
    folder = os.path.dirname(local_path)
    ext = os.path.splitext(local_path)[1]
    base = f"{record['date']}_{sanitize(record['category'])}_{sanitize(record['store'])}_{record['amount']}円"
    if record["status"] == "needs_review":
        base += "_自動要確認"
    new_name = base + ext
    new_path = os.path.join(folder, new_name)
    n = 2
    while os.path.exists(new_path) and new_path != local_path:
        new_path = os.path.join(folder, f"{base}_{n}{ext}")
        n += 1
    if new_path != local_path:
        os.rename(local_path, new_path)
    return new_path


def process_one(local_path: str, gcs_object_name: str) -> bool:
    with open(local_path, "rb") as f:
        image_bytes = f.read()

    result = ocr.extract_receipt(image_bytes)

    if not result.get("readable", False):
        log(f"読み取り不可: {local_path} ({result.get('notes')}) — 画像はそのまま残し、台帳には記帳しません")
        return False

    amount = result.get("amount")
    if amount is None:
        log(f"金額不明: {local_path} — 台帳には記帳しません。手動確認してください")
        return False

    confidence = result.get("confidence", "high")
    status = "needs_review" if confidence in ("low", "medium") else "new"

    record = {
        "date": result.get("date"),
        "is_income": False,
        "category": result.get("category") or "雑費",
        "store": result.get("store"),
        "items": result.get("items"),
        "reg": result.get("reg"),
        "amount": amount,
        "status": status,
        "note": result.get("notes") or None,
        "file": None,  # 下で確定後に設定
        "source": "line_auto",
        "gcs_object": gcs_object_name,
    }

    if not record["date"] or not re.match(r"^\d{4}-\d{2}-\d{2}$", record["date"]):
        log(f"日付が不正のため記帳をスキップ: {local_path} date={record['date']!r}")
        return False

    new_path = rename_image(local_path, record)
    record["file"] = os.path.basename(new_path)
    append_ledger(record)
    log(f"記帳: {record['date']} {record['category']} {record['store']} {amount}円 status={status} -> {new_path}")
    return True


def rebuild_excel() -> bool:
    try:
        saved, final_balance = build_workbook(LEDGER_PATH, [XLSX_OUT_1, XLSX_OUT_2])
        log(f"Excel再構築 完了: 最終残高={final_balance}円")
        return True
    except PermissionError:
        log("Excelがロック中（開かれている可能性）のため今回は再構築をスキップ。次回実行時に再試行します")
        return False
    except Exception:
        log("Excel再構築で予期しないエラー:\n" + traceback.format_exc())
        return False


def main():
    log("=== sync_and_process 開始 ===")
    try:
        downloaded = gcs_sync.sync_new_images()
    except Exception:
        log("GCS同期で失敗:\n" + traceback.format_exc())
        downloaded = []

    if not downloaded:
        log("新着画像なし")
    else:
        log(f"新着画像 {len(downloaded)} 件を処理します")
        processed = 0
        for local_path, gcs_object_name in downloaded:
            try:
                if process_one(local_path, gcs_object_name):
                    processed += 1
            except Exception:
                log(f"画像処理で予期しないエラー ({local_path}):\n" + traceback.format_exc())
        log(f"{processed}/{len(downloaded)} 件を台帳に記帳しました")

        if processed > 0:
            rebuild_excel()

    log("=== sync_and_process 終了 ===\n")


if __name__ == "__main__":
    main()
