# -*- coding: utf-8 -*-
"""
ひつじさんチャネルに届く「テキスト」メッセージを、社員（主に小筆さん）からの
日々の進捗報告として扱い、現在のタスク状況を踏まえた次の指示をClaudeに生成させて
LINEへ即時返信する。あわせて要約を社長（diet-coachingチャネル経由）へも通知する。

識別は receipt_handler.py の画像処理と同じ考え方：
- RECEIPT_ALLOWED_USER_IDS（レシート送信者＝MEGUMIさん想定）からのテキストは対象外
- KOBUDE_ALLOWED_USER_IDS が空なら、それ以外の送信者は全員「小筆さん」として扱う
  （userIdが確定したら、この環境変数をそのIDだけに絞り込める。
   receipt-pipeline/README.md のPhase B〔MEGUMIさん特定〕と同じやり方）

小筆さんが担当しうる2つのタスクトラック（補助金・FC化）それぞれの状態を
Firestore の task_state/kobude ドキュメント（{"hojyokin": "...", "fc": "..."}）に保持し、
Claudeが進捗報告を踏まえて更新した説明文を毎回書き戻す。進捗報告と返信は
progress_reports コレクションに全件保存し、あとで社長が履歴を確認できるようにする。

REFERENCE_KNOWLEDGE は agents/hojyokin_agent.py・agents/fc_agent.py が過去に調査した
レポート（agents/output/hojyokin_latest.txt・fc_latest.txt、2026/10/05時点）から、
小筆さんへの指示に直結する実務知識だけを抜き出してここに埋め込んだもの。
調査結果が更新されたら、ここも合わせて更新するのが望ましい（現状は手動同期）。
"""

import json
import os
import urllib.error
import urllib.request

RECEIPT_LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("RECEIPT_LINE_CHANNEL_ACCESS_TOKEN", "")
COACH_LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
COACH_LINE_USER_ID = os.environ.get("COACH_LINE_USER_ID", "")

KOBUDE_ALLOWED_USER_IDS = {
    uid.strip() for uid in os.environ.get("KOBUDE_ALLOWED_USER_IDS", "").split(",") if uid.strip()
}
RECEIPT_ALLOWED_USER_IDS = {
    uid.strip() for uid in os.environ.get("RECEIPT_ALLOWED_USER_IDS", "").split(",") if uid.strip()
}

LINE_PROFILE_URL = "https://api.line.me/v2/bot/profile/{}"
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"

DEFAULT_TASK_STATE = {
    "hojyokin": (
        "小規模事業者持続化補助金（次回公募、通常枠は11月上旬開始見込み）に向けた準備。"
        "現在はまだ様式が公開されていないため、小筆さんには申請の心構え・必要書類の洗い出しを進めてもらっている段階。"
        "社長から那須塩原商工会議所の担当・嶋村さんを紹介予定で、紹介後は小筆さんが実際に窓口へ足を運びながら、"
        "様式公開後すぐに申請できるよう準備を進めてほしい。"
    ),
    "fc": (
        "Honey LaRvaのフランチャイズ化は構想段階。まずはWeek1相当（栃木県よろず支援拠点・中小企業診断士への初期相談）"
        "と、2店舗（大田原・那須塩原）の過去24ヶ月の月次損益・既存マニュアルの有無・会員データの棚卸しが優先。"
    ),
}

REFERENCE_KNOWLEDGE = """
【補助金まわりの実務知識（小規模事業者持続化補助金）】
- 平均採択率は約6割（62%前後）。「必ず通る」保証は制度上誰にもできないが、審査基準に忠実に・不採択の典型パターンを
  避けて作り込めば、現実的に採択率を大きく引き上げられる。小筆さんには、楽観的な激励ではなく、以下の具体的な
  チェック観点に沿った作り込みを指示すること。

- 【商工会議所の事業支援計画書（様式4）のスケジュール】次回（第20回）公募は申請受付開始2026/11/5、様式4の
  発行"依頼"締切は2026/12/4（申請そのものの締切より早い点に要注意）。様式4は依頼した当日には発行されないため、
  事業計画がある程度まとまった段階で早めに商工会議所（嶋村さん）に相談を始める必要がある。

- 【書面審査の4項目】①自社の経営状況分析の妥当性 ②経営方針・目標と今後のプランの適切性 ③補助事業計画の有効性
  ④積算の透明・適切性。経営計画書（様式2）は「企業概要→顧客ニーズと市場動向→自社の強み→経営方針・目標と今後の
  プラン」を1本のストーリーとしてつなげる構成が評価されやすい。売上推移・顧客データ・競合比較などの数字・事実・
  根拠を盛り込み、「審査員が事業者の顔・本気度・将来像を具体的にイメージできるか」を基準に仕上げる。

- 【加点項目（該当すれば必ず使う）】重点政策加点（赤字賃上げ加点、原油・物価高騰等の事業環境変化加点 等）と
  政策加点（賃金引上げ加点、地方創生型加点、事業承継加点 等）から、それぞれ1種類ずつ・最大2種類まで選んで加点を
  狙える。該当しそうな項目がないか必ず確認すること。

- 【典型的な不採択理由（＝絶対に避けるべきこと）】
  1) 提出書類の不備・様式の記載漏れ
  2) 事業内容が補助金の目的（販路開拓・生産性向上）からずれている
  3) 経費の大半が汎用性の高い物品（PC等、他用途に転用できるもの）に偏っている
  4) 経営課題や数値目標が曖昧で「申請者の顔」が見えない
  5) 経費金額が相場と乖離している、または内容が具体性に欠ける
  6) 記載ボリュームが薄く、事業への本気度が伝わらない
  小筆さんの報告内容がこれらに当てはまりそうな場合は、具体的に指摘して書き直しを促すこと。

【FC化まわりの実務知識（Honey LaRva）】
- 【法定開示書面（中小小売商業振興法）】加盟店契約前に、本部概要・加盟金/保証金等の金銭面・ロイヤリティ・
  既存加盟店の営業成績・契約解除条件など"22項目"の情報を書面で開示・説明する法的義務がある（以前9項目と
  案内していたのは古い情報なので訂正済み）。違反が認められると、まず主務大臣（経済産業大臣等）から是正の
  勧告があり、従わない場合はその旨が公表される（行政指導が先で、いきなり刑事罰ではない）。

- 【FC本部を作るタイミング】FC本部構築の一般的な起算点は「2号店のオペレーションが1号店と同質になった瞬間」。
  Honey LaRvaはすでに大田原・那須塩原の2店舗運営の実績があるため、この条件はすでに満たしている可能性が高く、
  今はFC化の検討を始めるのに適した時期と言える。

- 【費用相場】FC本部構築支援コンサルは月額25万円(1年目)→15万円(2年目)→10万円(3年目)程度のプランが一般的。
  商標登録費は1区分・10年で約33,000円、3区分なら約99,000円。日本フランチャイズチェーン協会の正会員になるには
  協会の倫理綱領への賛同と所定の基準を満たす必要がある。

- 【フィットネス業界の成功・失敗パターン】成功例では開業6ヶ月以内に初期費用を回収し1年以内に2店舗目を出す
  ペースが一つの目安。失敗の最大要因は「資金不足」（想定より初期費用が膨らみ赤字が続くケース）。FC化後は
  本部が成功パターンを加盟店に落とし込める形にできるかが加盟店の生存率を左右する。

- FC化前に整備すべき3本柱：①運営マニュアルの体系化（Tier1即時対応〜Tier3の2〜3ヶ月整備）②2店舗の収支モデルの可視化
  （損益分岐点・初期投資額の相場感）③研修制度の骨格（オープニング研修など）。
- 相談先の例：栃木県よろず支援拠点（無料相談）、中小企業診断士、弁護士（FC法務）。
"""

SYSTEM_PROMPT = """あなたは株式会社芹江コンチェルト（栃木県那須塩原市黒磯）の業務サポートAI「ひつじさん」です。
会社の事業：
- Lodgers Bldg SERIE（旅館業）
- Honey LaRva（フィットネスボクシングジム）
- パンダベビーカステラ（移動販売）

社員の小筆さんから届いた日々の進捗報告やメッセージを受け取り、社長に代わって次にやるべき具体的な仕事を指示する役割です。
小筆さんが関わりうるタスクは次の2つです。メッセージの内容から関係するものを判断し、関係するものだけに触れてください
（両方に関係する内容であれば両方に触れてよい）。

【補助金タスクの現在状況】
{hojyokin_state}

【FC化タスクの現在状況】
{fc_state}

{reference_knowledge}

【対応方針】
- まず小筆さんの報告・質問の内容を一言ねぎらう／受け止める
- 関係するタスクの現在状況と実務知識を踏まえて、次に取るべき具体的な行動を1〜3個、箇条書きで指示する
- 単なる激励で終わらせず、実務知識にある具体的な制度名・書類名・相談先などを盛り込んで実行可能な指示にする
- 補助金タスクに関係する報告の場合は、必ず「採択されやすくするための実務知識」（書面審査4項目・加点項目・
  典型的な不採択理由）に照らして具体的にチェック・助言すること。特に小筆さんが書いた・考えている内容が
  不採択の典型パターン（経費が汎用品に偏っている、数値目標が曖昧、記載が薄い 等）に当てはまりそうなら、
  遠慮せず指摘して直させる。該当しそうな加点項目があれば積極的に使うよう勧める。
  ただし「必ず採択される」「100%通る」という断定は絶対にしないこと（採択率は平均6割程度の相対審査のため）。
  代わりに「このチェック観点を満たせば通る確率を大きく上げられる」という誠実な伝え方をする。
- FC化タスクに関係する報告の場合も同様に、実務知識にある具体的な数字・制度名（法定開示22項目・起算点の条件・
  費用相場・成功/失敗パターン）を使って、一般論ではなく実行可能な指示にする。
- 社長の判断・報告が必要な内容があれば、その旨を明記する
- 丁寧で分かりやすい、ですます調。LINEメッセージとして読みやすい長さ（450字程度まで）

出力は次のJSON形式のみを返してください（前後に説明文やコードブロック記法を付けないこと）：
{{"reply": "小筆さんへ送るLINE返信文", "updated_task_state": {{"hojyokin": "補助金タスクの状況説明（進展が無ければ元の文章のままでよい）", "fc": "FC化タスクの状況説明（進展が無ければ元の文章のままでよい）"}}}}
"""


def _firestore_client():
    from google.cloud import firestore
    return firestore.Client()


def _get_task_state(db) -> dict:
    doc = db.collection("task_state").document("kobude").get()
    state = dict(DEFAULT_TASK_STATE)
    if doc.exists:
        data = doc.to_dict()
        for key in DEFAULT_TASK_STATE:
            if data.get(key):
                state[key] = data[key]
    return state


def _save_task_state(db, state: dict) -> None:
    from google.cloud import firestore as fs
    payload = {key: state.get(key, DEFAULT_TASK_STATE[key]) for key in DEFAULT_TASK_STATE}
    payload["updated_at"] = fs.SERVER_TIMESTAMP
    payload["updated_by"] = "ai"
    db.collection("task_state").document("kobude").set(payload)


def _log_progress_report(db, user_id, display_name, report, reply, before, after):
    from google.cloud import firestore as fs
    db.collection("progress_reports").add({
        "timestamp": fs.SERVER_TIMESTAMP,
        "user_id": user_id,
        "display_name": display_name,
        "report": report,
        "reply": reply,
        "task_state_before": before,
        "task_state_after": after,
    })


def get_display_name(user_id: str) -> str:
    if not user_id:
        return ""
    req = urllib.request.Request(
        LINE_PROFILE_URL.format(user_id),
        headers={"Authorization": f"Bearer {RECEIPT_LINE_CHANNEL_ACCESS_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8")).get("displayName", "")
    except Exception as e:
        print(f"[get_display_name] 取得失敗: {e}")
        return ""


def reply_message(reply_token: str, text: str) -> None:
    if not reply_token:
        return
    payload = {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]}
    req = urllib.request.Request(
        LINE_REPLY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RECEIPT_LINE_CHANNEL_ACCESS_TOKEN}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as e:
        print(f"[reply_message] 送信失敗: {e.code} {e.read().decode('utf-8', 'ignore')[:300]}")
    except Exception as e:
        print(f"[reply_message] 送信失敗: {e}")


def notify_president(summary: str) -> None:
    """社長の個人LINE（diet-coachingチャネル経由、既存の週次レポート等と同じ宛先）へ要約を通知する。
    未設定なら何もしない（必須機能ではないため失敗時も処理は継続する）。"""
    if not COACH_LINE_CHANNEL_ACCESS_TOKEN or not COACH_LINE_USER_ID:
        return
    payload = {"to": COACH_LINE_USER_ID, "messages": [{"type": "text", "text": summary}]}
    req = urllib.request.Request(
        LINE_PUSH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {COACH_LINE_CHANNEL_ACCESS_TOKEN}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"[notify_president] 送信失敗（社長通知はスキップ）: {e}")


def _ask_claude(state: dict, report: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = SYSTEM_PROMPT.format(
        hojyokin_state=state["hojyokin"],
        fc_state=state["fc"],
        reference_knowledge=REFERENCE_KNOWLEDGE,
    )
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=900,
        system=system,
        messages=[{"role": "user", "content": report}],
    )
    text = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
    try:
        if text.startswith("```"):
            text = text.strip("`").split("\n", 1)[-1]
        parsed = json.loads(text)
        updated = parsed.get("updated_task_state") or {}
        parsed["updated_task_state"] = {
            key: (updated.get(key) or state[key]) for key in DEFAULT_TASK_STATE
        }
        return parsed
    except Exception as e:
        print(f"[_ask_claude] JSON解析失敗（そのままLINE返信として使う）: {e} raw={text[:200]!r}")
        return {"reply": text[:600], "updated_task_state": state}


def handle_text_event(ev: dict) -> None:
    """ひつじさんチャネルに届いたテキストメッセージ（進捗報告）を処理する。
    例外は内部で握りつぶし、呼び出し元は継続する。"""
    try:
        msg = ev.get("message", {})
        text = msg.get("text", "").strip()
        source = ev.get("source", {})
        user_id = source.get("userId", "")
        reply_token = ev.get("replyToken", "")

        if not text or not user_id:
            return

        if user_id in RECEIPT_ALLOWED_USER_IDS:
            print(f"[handle_text_event] レシート送信者（MEGUMIさん想定）のテキストのため対象外: userId={user_id}")
            return
        if KOBUDE_ALLOWED_USER_IDS and user_id not in KOBUDE_ALLOWED_USER_IDS:
            print(f"[handle_text_event] 許可リスト外のため対象外: userId={user_id}")
            return

        display_name = get_display_name(user_id)
        print(f"[handle_text_event] 進捗報告受信 userId={user_id} displayName={display_name!r} text={text[:50]!r}")

        db = _firestore_client()
        before = _get_task_state(db)
        result = _ask_claude(before, text)
        reply_text = (result.get("reply") or "").strip() or "報告ありがとうございます。確認しました。"
        after = result.get("updated_task_state", before)

        reply_message(reply_token, reply_text)
        _save_task_state(db, after)
        _log_progress_report(db, user_id, display_name, text, reply_text, before, after)

        notify_president(
            f"【ひつじさん自動応答】{display_name or '社員'}さんより進捗報告:\n{text[:200]}\n\n"
            f"→返信した指示:\n{reply_text[:400]}"
        )
    except Exception as e:
        print(f"[handle_text_event] 予期しないエラー（処理は継続）: {e}")
