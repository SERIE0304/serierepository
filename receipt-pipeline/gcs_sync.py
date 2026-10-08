# -*- coding: utf-8 -*-
"""
GCS の receipts/ 配下から、まだ取り込んでいない画像だけをダウンロードする。
認証は Application Default Credentials（`gcloud auth application-default login`）を使う想定。

注意: 「ローカルフォルダに同名ファイルが無ければダウンロード」という方式だと、
取り込み後に画像をリネームした時点で元のファイル名が消え、次回また
同じGCSオブジェクトを再ダウンロードしてしまう（＝二重記帳の原因になる）。
そのため「取り込み済みGCSオブジェクト名」を別途マニフェストファイルで
管理し、ローカルのファイル名が変わっても二重取り込みしないようにする。
"""
import os

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "")
# ユーザー認証のADC（サービスアカウントではない）にはデフォルトプロジェクトが
# 紐づかないため、明示的に指定する必要がある。
GCP_PROJECT = os.environ.get("GCP_PROJECT", "serie-concerto")
LOCAL_RECEIPT_DIR = r"C:\Users\user\Desktop\領収書"
GCS_PREFIX = "receipts/"
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "synced_objects.txt")


def _load_manifest() -> set:
    if not os.path.exists(MANIFEST_PATH):
        return set()
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def _append_manifest(object_names) -> None:
    with open(MANIFEST_PATH, "a", encoding="utf-8") as f:
        for name in object_names:
            f.write(name + "\n")


def sync_new_images() -> list:
    """新しくダウンロードした (ローカルファイルパス, GCSオブジェクト名) のリストを返す。"""
    if not GCS_BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME が設定されていません")

    from google.cloud import storage
    client = storage.Client(project=GCP_PROJECT)
    bucket = client.bucket(GCS_BUCKET_NAME)

    os.makedirs(LOCAL_RECEIPT_DIR, exist_ok=True)
    already_synced = _load_manifest()

    downloaded = []
    newly_synced_names = []
    for blob in client.list_blobs(bucket, prefix=GCS_PREFIX):
        if not blob.name or blob.name in already_synced or blob.name == GCS_PREFIX:
            continue
        filename = os.path.basename(blob.name)
        local_path = os.path.join(LOCAL_RECEIPT_DIR, filename)
        # ローカルに同名ファイルが既にあれば（手動保存分と衝突等）、末尾に連番を付ける
        base, ext = os.path.splitext(local_path)
        n = 2
        while os.path.exists(local_path):
            local_path = f"{base}_{n}{ext}"
            n += 1
        blob.download_to_filename(local_path)
        downloaded.append((local_path, blob.name))
        newly_synced_names.append(blob.name)
        print(f"[gcs_sync] ダウンロード: {blob.name} -> {local_path}")

    # 1件でも処理中に例外が起きても、ここまでにダウンロードできた分は
    # 二重取得を防ぐため確実にマニフェストへ記録しておく
    if newly_synced_names:
        _append_manifest(newly_synced_names)

    return downloaded
