# プロジェクト概要

このリポジトリには2つのWebサイトが含まれています。

---

## 1. タスク管理アプリ (`task-app/`)

**URL**: `https://serie0304.github.io/serierepository/task-app/`

### 技術スタック
- 純粋なHTML / CSS / JavaScript（フレームワークなし）
- Firebase Realtime Database（データ共有）
- Firebase Authentication（Email/Password）
- PWA対応（manifest.json, sw.js）

### Firebase設定
- プロジェクト: `serie-concerto`
- DB URL: `https://serie-concerto-default-rtdb.asia-southeast1.firebasedatabase.app`
- 設定ファイル: `task-app/firebase-config.js`

### ファイル構成
```
task-app/
├── index.html        # メインHTML（モーダル・UI構造）
├── app.js            # メインロジック（タスク・タイムカード・スタッフ管理）
├── auth.js           # ログイン処理（パスワードのみでログイン）
├── style.css         # ドラゴンクエスト風ダークUI
├── firebase-config.js
├── sw.js             # Service Worker（PWAキャッシュ）
└── manifest.json
```

### 主な機能
- **ログイン**: パスワードのみ入力（メール不要）。`/passwords/` にID→メール対応を保存
- **タスク管理**: 全スタッフ共通・Firebase共有。ステータス管理あり
- **タイムカード**: スタッフは自分のみ表示、管理者は全員表示
- **スタッフ管理**: 管理者が権限付与/削除
- **定型文ボタン**: タイムカードメモ（午前のみ/早退/遅刻/直行/直帰）、タスクメモ（対応中/確認待ち/保留/要確認）

### UIデザイン方針
- ドラゴンクエスト風ダークテーマ（黒背景・青ボーダー・白文字）
- モバイルファースト
- コメントは書かない

### Firebase DBの構造
```
/passwords/{staffId}      # パスワード → メールアドレス対応
/tasks/{taskId}           # タスク一覧
/timecards/{date}/{staffId}  # タイムカード
/staff/{uid}              # スタッフ情報・管理者フラグ
```

---

## 2. なんだパンダベビーカステラ HP（ルート `/`）

**URL**: `https://serie0304.github.io/serierepository/`

- ファイル: `index.html`, `images/`, `robots.txt`, `sitemap.xml`
- 別チャットで管理・更新中

---

## デプロイ

- **ブランチ**: `integrate/both-sites`
- **GitHub Pages設定**: Settings → Pages → Branch: `integrate/both-sites`
- どちらのサイトもこのブランチから同時にデプロイされる
- `.claude/` フォルダは `.gitignore` で除外（サブモジュール問題を防ぐため）

---

## 開発時の注意

- コードにコメントを追加しない（既存方針）
- 新機能はモバイルで動作確認
- Firebase認証のメールは社内ID形式（`{staffId}@serie-concerto.internal`）
- Service Worker のキャッシュは `sw.js` 内の `CACHE_VERSION` を更新して強制リフレッシュ
