# VSコード指示書 — 金曜レポートを「今週の活動まとめ」に作り替える（案A）

VSコードの Claude Code に、下の「■コピー用」枠をそのまま貼り付けてください。
（リポジトリがローカルに無い場合は、枠内の最初の clone コマンドで用意されます）

---

## 背景（Claudeが理解すべき現状）

- 対象リポジトリ：**SERIE0304/serierepository**
- 金曜18:00に `.github/workflows/weekly_agents.yml` の `friday-review` ジョブが
  `agents/task_manager.py` を実行し、LINEへ「週次振り返り」を送っている。
- ところが毎回「今週のタスクは記録されていません」という空メッセージしか送られない。
  原因は2つ：
  1. 月曜エージェントの `save_task` が無効化されている（`pass # save_task一時無効`）。
  2. GitHub Actions は毎回まっさらな環境で動くため、月曜に作った
     `agents/output/*_latest.txt` や `agents/tasks.json` がリポジトリに保存されず、
     金曜のジョブが読み込めない。
- 各エージェントは `activity_logger.save_report()` で
  `agents/output/{agent名}_latest.txt` にレポートを書き出している
  （panda / pricing / sns / larva / hojyokin / fudosan / fc など）。

---

## ■コピー用（ここから下を全部コピーして貼り付け）

```
リポジトリ SERIE0304/serierepository に対して以下の改修を行ってください。
ローカルに無ければ最初に clone してください：
  git clone https://github.com/SERIE0304/serierepository.git
  cd serierepository

【ゴール】
金曜18:00の週次振り返りLINEを、空メッセージではなく
「今週各エージェントが作った実際のレポートの要約」にする。

【変更① 月曜レポートをリポジトリに保存する（永続化）】
ファイル: .github/workflows/weekly_agents.yml
- monday-weekly ジョブの最後（LINEアラートstepの前）に、
  生成物をコミットして残すstepを追加する。内容:
    - name: レポートをコミット
      run: |
        git config user.name "github-actions"
        git config user.email "actions@github.com"
        git add agents/output/ agents/activity_log.json
        git commit -m "chore: 週次エージェントのレポートを保存 [skip ci]" || echo "変更なし"
        git pull --rebase || true
        git push || echo "push失敗（権限を確認）"
- ジョブ冒頭の actions/checkout@v4 に「持続書き込み権限」を与えるため、
  weekly_agents.yml の先頭（on: の下あたり）に次を追加:
    permissions:
      contents: write

【変更② 金曜の振り返りを「レポート要約」に作り替える】
ファイル: agents/task_manager.py
- send_friday_review() を次の仕様に書き換える:
  1. agents/output/ 内の各 *_latest.txt を読み込む
     （対象: panda, pricing, sns, larva, hojyokin, fudosan, fc。存在するものだけ）
  2. 各レポート本文をエージェントごとに150〜200文字程度に要約して
     1通のLINEメッセージにまとめる。要約は anthropic の
     claude-haiku-4-5-20251001 を使ってよい（ANTHROPIC_API_KEY は環境変数にある）。
     APIを使わず単純に先頭200文字を抜粋する簡易版でも可。
  3. メッセージ冒頭は「【今週の活動まとめ】YYYY/MM/DD」とする。
  4. output/ に1件もレポートが無い場合のみ、従来どおり
     「今週のレポートはまだありません」という短い案内を送る。
  5. 既存の send_line_message() をそのまま使ってLINE送信する。
- tasks.json 依存の旧ロジックは削除してよい。

【変更③ workflowのfridayステップ環境変数】
ファイル: .github/workflows/weekly_agents.yml の friday-review ジョブ
- 「週次タスク振り返りLINE送信」stepの env に ANTHROPIC_API_KEY を追加する
  （要約にAPIを使うため）:
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      LINE_CHANNEL_TOKEN: ${{ secrets.LINE_CHANNEL_TOKEN }}

【動作確認】
- python agents/task_manager.py をローカルで実行し、
  output/ にダミーの *_latest.txt を置いた状態で要約メッセージが
  組み立てられることを確認する（LINE送信はтокенが無ければ失敗してOK、
  メッセージ生成までを確認）。

【仕上げ】
- 変更を新しいブランチにコミットし、日本語で分かりやすいコミットメッセージを付ける。
- プルリクエストを作成し、変更点（変更①②③）を箇条書きで説明する。
- 最後に「何を直したか」を日本語で3行以内で報告する。
```

## ■コピー用（ここまで）

---

## 補足（芹江さん向けメモ）

- この改修後、**次の月曜**に各エージェントがレポートを保存 →
  **その週の金曜**に「今週の活動まとめ」が届くようになります。
- LINE送信先ユーザーID・トークンは既存のまま（変更なし）。
- GitHub Secrets に `ANTHROPIC_API_KEY` と `LINE_CHANNEL_TOKEN` が
  設定されている前提です（既存の月曜ジョブが動いているので設定済みのはず）。
