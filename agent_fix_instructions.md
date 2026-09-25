# エージェント修復 指示書（VS Code / Claude Code 向け）

作成日：2026/09/25　依頼者：芹江
目的：GitHub Actions で自動実行している週次エージェントを、**毎週きちんとレポートが LINE に届き、`agents/output/` に保存される状態**に戻す。

---

## 0. 現状（調査結果）

| 症状 | 原因 |
|---|---|
| 9/21（月）以降、全エージェントが失敗 | **Anthropic API の利用上限に到達**。ログ：`You have reached your specified API usage limits. You will regain access on 2026-10-01 at 00:00 UTC.` |
| X下書きも 9/22 以降毎回失敗 | 同上。`x_draft_agent.yml` は 1日2回 × Opus × Web検索で、最も費用がかかっている（実行 136 回） |
| SERIE料金レポートが壊れている（`（トラベルコ注記）|` だけ等） | `pricing_agent.py` が「最後のテキストブロック」だけを保存している |
| SNS レポートが一度も保存されていない | `sns_agent.py` が `save_report()` を呼んでいない。さらに「48時間以内の計量ニュース」が無いと即終了する |
| 1つ失敗すると同じ月曜ジョブの残りが全部止まる | `monday-weekly` ジョブのステップが直列で、失敗時に後続がスキップされる |
| タスク一覧（tasks.json）が更新されない | panda / fudosan / hojyokin / larva で `save_task` が「一時無効」のまま |
| 検索内容が古い | プロンプトに「2026年6月」がハードコードされている（panda / pricing） |
| FC化レポートの連絡先が不正確な可能性 | `fc_agent.py` だけ Web 検索なし（Haiku 単体）で作文している |
| 届く時刻が遅い | GitHub の cron は混雑時に 1〜4 時間遅れる（例：金曜18:00予定 → 22:12 実行） |

※ 不動産の「第1・第3週」判定ミスは修正済み（`weekly_agents.yml` の日付条件を `1〜7日 または 15〜21日` に変更）。

---

## 1. 【社長判断・コード外】API 上限の対応 ★最優先

コードを直しても、**10/1 9:00（JST）までは API が使えないため動きません。**

- 選択肢A：Anthropic Console（console.anthropic.com → Settings → Limits）で月の上限額を引き上げる → すぐ復旧
- 選択肢B：10/1 の自動リセットを待つ（その間は全エージェント停止）

あわせて下記「2. 費用削減」を必ず実施し、同じ上限到達を繰り返さないようにする。

---

## 2. 費用削減（上限到達の再発防止）

### 2-1. `.github/workflows/x_draft_agent.yml`
- 実行を **1日1回（朝6:00 JST）** に減らす：cron `'0 21 * * *'` だけ残し、`'0 9 * * *'` を削除。

### 2-2. `agents/sns_agent.py`
- `search_scandal_news()` / `generate_x_drafts()` / `main()` の `model='claude-opus-4-5'` を **Sonnet 系に変更**（下記 3-0 の共通定数を使う）。
- Web 検索ツールに回数上限を付ける：
  `{'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': 3}`

### 2-3. 全エージェント共通
- Web 検索ツールに `'max_uses': 5` を付ける（panda / pricing / larva / hojyokin / fudosan / fc）。

---

## 3. コード修正

### 3-0. 共通化（新規ファイル `agents/common.py`）
各エージェントに同じコードがコピーされているので、1か所にまとめる。

- `MODEL_MAIN`（レポート作成用、Sonnet 系の最新モデル）と `MODEL_LIGHT`（要約・タスク抽出用、`claude-haiku-4-5-20251001`）を定数で定義する。モデル名はこの1か所で管理する。
- `send_line_message(message)`：今の実装をそのまま移す。
  **LINE の1通は5000文字まで**なので、超えるときは分割して送る。
- `save_task(category, text)`：今の実装を移す。
- `run_web_research(prompt, max_tokens=2000, max_uses=5)`：
  - `client.messages.create(..., tools=[web_search(max_uses)])` を呼ぶ
  - `stop_reason == 'pause_turn'` のときは、返ってきた content を assistant として messages に追加し、もう一度呼ぶ（最大5回）
  - **すべての text ブロックを連結して**返す
  - 結果が空、または50文字未満なら例外にする（壊れたレポートを保存・送信しないため）
- 各エージェントは `from common import ...` に置き換え、重複コードを削除する。

### 3-1. `agents/pricing_agent.py`
- 自前の `for _ in range(10)` ループをやめて `run_web_research()` を使う。
  （現状は `report = block.text` で最後のブロックだけ残るため、レポートが壊れる）
- プロンプトの「那須塩原 イベント 2026年6月」を、**実行日から見て今週・来週**に変える（`datetime` で年月を埋め込む）。
- `max_tokens` を 2000 にする。

### 3-2. `agents/panda_agent.py`
- 検索キーワードの「2026年6月」「2026」を、**実行月と翌月**が入るように動的に作る。
- `run_web_research()` を使う。
- 末尾のコピペ残り（`full_text` の再計算、`pass  # save_task一時無効`、`print('タスク保存：' + str(task))`）を削除する。
  Haiku でアクションを1行抽出して `save_task('パンダカステラ', ...)` を**有効化**する。

### 3-3. `agents/fudosan_agent.py` / `agents/hojyokin_agent.py` / `agents/larva_agent.py`
- 3-2 と同じ修正（`run_web_research()` の利用、末尾の重複コード削除、`save_task` 有効化）。
- hojyokin：プロンプトに「**申請締切日を必ず記載**、締切が過ぎたものは除外」を追加。

### 3-4. `agents/fc_agent.py`
- `run_web_research()`（Web 検索あり）に切り替える。連絡先や費用を推測で書かせない。
- プロンプトに「出典URLを付ける」を追加。

### 3-5. `agents/sns_agent.py`（週次の `main()`）
- 週次用として「**直近7日間**のボクシング・格闘技ニュース（日本人選手・世界戦・計量問題など）」を対象にする。
  計量ニュースが無いというだけで終了しないようにする（`NO_NEWS_TODAY` で終わるのは、ニュースが本当にゼロのときだけ）。
- ニュースと台本を `save_report('sns', ニュース + '\n\n' + 台本)` で保存する（金曜まとめに載せるため）。
- `generate_script()` の `response.content[0].text` を、text ブロックの連結に変える。

### 3-6. `agents/task_manager.py`
- 7日より古いレポート（`生成日時:` の行で判定）は「今週の更新なし」と表示し、古い内容を今週分として要約しないようにする。

---

## 4. ワークフロー修正（`.github/workflows/weekly_agents.yml`）

1. `monday-weekly` の4ステップ（パンダ/料金/SNS/LaRva）に `continue-on-error: true` を付ける。
   → 1つ失敗しても残りが動き、レポートのコミットも実行される。
   ただし失敗通知が出なくなるので、各ステップに `id` を付け、最後に
   `if: steps.panda.outcome == 'failure' || steps.pricing.outcome == 'failure' || ...` の LINE アラートステップを置く（**どれが失敗したかを本文に入れる**）。
2. `monday-monthly` の `python fc_agent.py` も同様に、補助金が失敗しても FC が動くようにする。
3. 失敗アラートで、API 上限エラー（`usage limits`）のときは「⚠️API上限に達しています。Anthropic Consoleで上限を確認してください」と送る。
   （各エージェントで `anthropic.BadRequestError` の本文に `usage limits` が含まれていたら、この文面を LINE に送ってから `exit 1`）
4. `actions/checkout@v4` → `@v5`、`actions/setup-python@v5` → `@v6`（Node20 廃止の警告対応）。
5. 依存パッケージは `pip install anthropic`（`pyjwt cryptography` は今は不要）。

---

## 5. 動作確認（完了条件）

API 上限が解除されてから（1. が済んでから）行う。

1. ローカルで構文チェック：`cd agents && python -m py_compile *.py`
2. GitHub → Actions → 「週次エージェント自動実行」→ **Run workflow**（手動実行）
3. 以下をすべて満たしたら完了：
   - [ ] LINE に パンダ / 料金 / SNS / LaRva / 不動産 / 補助金 / FC の7レポートが届く
   - [ ] `agents/output/` に `*_latest.txt` が7種類すべて今日の日付で保存され、main にコミットされている
   - [ ] `pricing_latest.txt` に競合3件と推奨料金が入っている（壊れていない）
   - [ ] `tasks.json` に今日の日付のタスクが追加されている
   - [ ] 「X下書き」ワークフローを手動実行し、成功する
4. 翌週月曜の自動実行でも同じ結果になることを確認する。

---

## 6. 作業ルール
- 作業ブランチを切ってから修正し、PR を作って芹江の確認後に main へマージする。
- API キーや LINE トークンをコードやログに書かない（GitHub Secrets のみ使用）。
- `agents/activity_log.json` はワークフローでコミットしない（既存の仕組みを維持）。
