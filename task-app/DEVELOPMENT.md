# タスク管理アプリ 開発引き継ぎ書

## アプリURL
https://serie0304.github.io/serierepository/task-app/

---

## 技術構成

| 項目 | 内容 |
|------|------|
| 言語 | HTML / CSS / JavaScript（フレームワークなし） |
| データベース | Firebase Realtime Database |
| 認証 | Firebase Authentication (Email/Password) |
| ホスティング | GitHub Pages |
| PWA | manifest.json + sw.js |

### Firebase
- プロジェクト名: `serie-concerto`
- DB URL: `https://serie-concerto-default-rtdb.asia-southeast1.firebasedatabase.app`
- コンソール: https://console.firebase.google.com/project/serie-concerto
- 設定ファイル: `task-app/firebase-config.js`

### GitHub
- リポジトリ: https://github.com/SERIE0304/serierepository
- デプロイブランチ: `integrate/both-sites`
- デプロイ方式: GitHub Actions（`.github/workflows/deploy-pages.yml`）
- プッシュすると自動デプロイ

---

## ファイル構成

```
task-app/
├── index.html        # UI全体（モーダル・フォーム構造）
├── app.js            # メインロジック
├── auth.js           # ログイン処理
├── style.css         # デザイン（DQ風ダークUI）
├── firebase-config.js # Firebase接続設定
├── sw.js             # Service Worker（PWAキャッシュ）
└── manifest.json     # PWA設定
```

---

## Firebaseデータ構造

```
/passwords/{staffId}         # パスワード → メールアドレス対応
/tasks/{taskId}              # タスク一覧（全員共通）
/timecards/{date}/{staffId}  # タイムカード（日付/スタッフID）
/staff/{uid}                 # スタッフ情報・管理者フラグ
```

---

## ログイン仕様

- メールアドレスは不要、パスワードのみ入力
- `/passwords/` にスタッフID→メール対応を保存
- メール形式: `{staffId}@serie-concerto.internal`

---

## 完成済み機能

- [x] パスワードのみでログイン（メール不要）
- [x] タイムカード（スタッフは自分のみ、管理者は全員表示）
- [x] タスク管理（全スタッフ共通・Firebase共有）
- [x] スタッフ管理（管理者権限の付与/削除）
- [x] タイムカード保存後にランダムお疲れ様メッセージ
- [x] タイムカード・タスクのメモ欄に定型文ボタン

### 定型文ボタン
- タイムカード用: 午前のみ / 早退 / 遅刻 / 直行 / 直帰
- タスク用: 対応中 / 確認待ち / 保留 / 要確認

---

## UIデザイン方針

- ドラゴンクエスト風ダークテーマ（黒背景・青ボーダー・白文字）
- モバイルファースト（スマホ優先）
- コードにコメントは書かない

---

## 開発時の注意

### Service Worker キャッシュ更新
UIを変更したのに反映されない場合は `sw.js` の `CACHE_VERSION` を上げる

```js
// sw.js の先頭付近
const CACHE_VERSION = 'v6'; // ← 数字を上げる
```

### デプロイ手順
```bash
# integrate/both-sites ブランチで作業・コミット
git checkout integrate/both-sites
git add .
git commit -m "変更内容"
git push origin integrate/both-sites
# → GitHub Actionsが自動デプロイ（約1分）
```

### ブランチ構成
| ブランチ | 内容 |
|---------|------|
| `integrate/both-sites` | **本番デプロイブランチ**（タスクアプリ＋なんだパンダHP） |
| `claude/magical-darwin-ofvqr0` | タスクアプリ開発用（過去のfeatureブランチ） |
| `claude/nandapanda-hp-seo-odxqm2` | なんだパンダHP開発用（過去のfeatureブランチ） |

> **注意**: 変更は必ず `integrate/both-sites` にプッシュすること

---

## 今後の開発アイデア（未実装）

- 定型文のカスタマイズ機能（ユーザーが追加・編集できる）
- 月次タイムカード集計・CSV出力
- タスクの担当者アサイン機能
- プッシュ通知（PWA）

---

## Copilotへの指示例

```
.github/copilot-instructions.md と task-app/DEVELOPMENT.md を参照してください。
[やりたいことを具体的に書く]
```
