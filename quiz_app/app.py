import os
import random
from collections import defaultdict

from flask import Flask, render_template, request, redirect, url_for, session, flash

import sheets

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
QUIZ_QUESTION_COUNT = int(os.environ.get("QUIZ_QUESTION_COUNT", 10))


def _track(page):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    ip = ip.split(",")[0].strip()
    sheets.record_pageview(page, ip)


@app.route("/")
def index():
    _track("トップ")
    return render_template("index.html", tracks=sheets.TRACKS,
                           track_passwords={k: True for k in sheets.TRACK_PASSWORDS})


@app.route("/quiz/categories", methods=["POST"])
def quiz_categories():
    staff_name = request.form.get("staff_name", "").strip()
    track = request.form.get("track", "").strip()
    if not staff_name or track not in sheets.TRACKS:
        flash("名前と編を選択してください")
        return redirect(url_for("index"))
    required_pw = sheets.TRACK_PASSWORDS.get(track)
    if required_pw and request.form.get("track_password", "") != required_pw:
        flash("パスワードが違います")
        return redirect(url_for("index"))
    # カテゴリ選択を省略して直接クイズ開始
    questions = sheets.list_questions(track, None)
    if not questions:
        flash("対象の問題がありません")
        return redirect(url_for("index"))
    questions = random.sample(questions, min(QUIZ_QUESTION_COUNT, len(questions)))
    session["quiz"] = {
        "staff_name": staff_name,
        "track": track,
        "category": "全体",
        "question_ids": [q["id"] for q in questions],
        "current": 0,
        "score": 0,
        "results": [],
    }
    _track(f"クイズ開始:{track}")
    return redirect(url_for("quiz_question"))


@app.route("/quiz/start", methods=["POST"])
def quiz_start():
    staff_name = request.form.get("staff_name", "").strip()
    track = request.form.get("track", "").strip()
    category = request.form.get("category") or None
    if not staff_name or track not in sheets.TRACKS:
        flash("名前を入力してください")
        return redirect(url_for("index"))

    questions = sheets.list_questions(track, category)
    if not questions:
        flash("対象の問題がありません")
        return redirect(url_for("index"))

    questions = random.sample(questions, min(QUIZ_QUESTION_COUNT, len(questions)))
    session["quiz"] = {
        "staff_name": staff_name,
        "track": track,
        "category": category or "全体",
        "question_ids": [q["id"] for q in questions],
        "current": 0,
        "score": 0,
        "results": [],
    }
    _track(f"クイズ開始:{track}")
    return redirect(url_for("quiz_question"))


@app.route("/quiz/question", methods=["GET"])
def quiz_question():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("index"))

    idx = quiz["current"]
    if idx >= len(quiz["question_ids"]):
        return redirect(url_for("quiz_result"))

    qid = quiz["question_ids"][idx]
    question = next((q for q in sheets.list_questions() if str(q["id"]) == str(qid)), None)
    if not question:
        quiz["current"] += 1
        session["quiz"] = quiz
        return redirect(url_for("quiz_question"))

    choices = [c for c in [question["choice1"], question["choice2"],
                            question["choice3"], question["choice4"]] if c]
    correct_text = choices[int(question["correct_index"])]
    shuffled = choices[:]
    random.shuffle(shuffled)
    shuffled_correct_index = shuffled.index(correct_text)
    return render_template(
        "quiz.html", question=question, choices=shuffled,
        correct_index=shuffled_correct_index,
        progress=idx + 1, total=len(quiz["question_ids"]),
    )


@app.route("/quiz/answer", methods=["POST"])
def quiz_answer():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("index"))

    qid = request.form.get("question_id")
    selected_index = int(request.form.get("selected_index", -1))
    correct_index_shuffled = request.form.get("correct_index_shuffled", "-1")
    timed_out = selected_index == -1
    question = next((q for q in sheets.list_questions() if str(q["id"]) == str(qid)), None)
    correct = bool(question) and not timed_out and str(selected_index) == str(correct_index_shuffled)

    if correct:
        quiz["score"] += 1
    # セッションサイズ超過を防ぐため最小限のデータのみ保存
    quiz["results"].append({
        "qid": str(qid),
        "selected_index": selected_index,
        "correct": correct,
        "timed_out": timed_out,
    })

    try:
        sheets.record_response(
            quiz["staff_name"], quiz["track"], qid, quiz["category"], selected_index, correct,
        )
    except Exception:
        pass  # Sheets書き込み失敗はクイズフローに影響させない

    quiz["current"] += 1
    session["quiz"] = quiz
    return redirect(url_for("quiz_question"))


@app.route("/quiz/result")
def quiz_result():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("index"))
    total = len(quiz["question_ids"])
    score = quiz["score"]
    percentage = round(100 * score / total) if total else 0

    # セッションに保存した最小データから問題詳細を復元
    all_q = sheets.list_questions()
    q_map = {str(q["id"]): q for q in all_q}
    results = []
    for r in quiz["results"]:
        q = q_map.get(str(r["qid"]))
        choices = [q[c] for c in ["choice1", "choice2", "choice3", "choice4"] if q and q.get(c)] if q else []
        results.append({
            "question_text": q["question_text"] if q else "",
            "selected_index": r["selected_index"],
            "correct_index": int(q["correct_index"]) if q else None,
            "correct": r["correct"],
            "timed_out": r["timed_out"],
            "explanation": q.get("explanation", "") if q else "",
            "choices": choices,
        })

    session.pop("quiz", None)
    return render_template(
        "result.html", score=score, total=total, percentage=percentage,
        results=results, staff_name=quiz["staff_name"], track=quiz["track"],
    )


@app.route("/simulator")
def simulator():
    _track("シミュレーター")
    return render_template("simulator.html")


@app.route("/comparison")
def comparison():
    _track("FC比較")
    return render_template("comparison.html")


@app.route("/inquiry", methods=["GET", "POST"])
def inquiry():
    if request.method == "GET":
        _track("問い合わせ")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("お名前・メールアドレス・お問い合わせ内容は必須です")
            return redirect(url_for("inquiry"))
        sheets.record_inquiry(name, email, phone, message)
        return render_template("inquiry_done.html")
    return render_template("inquiry.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("パスワードが違います")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


def _require_admin():
    return session.get("is_admin", False)


@app.route("/admin")
def admin_dashboard():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    responses = sheets.all_responses()
    pageviews = sheets.all_pageviews()

    # ページ別集計
    from collections import Counter
    pv_by_page = Counter(p["page"] for p in pageviews)
    pv_total = len(pageviews)
    # 日別集計（直近7日）
    from datetime import date, timedelta
    today = date.today()
    pv_daily = {}
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        pv_daily[d] = sum(1 for p in pageviews if p.get("timestamp", "").startswith(d))

    by_staff = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0}))
    by_category = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0}))
    for r in responses:
        track = r.get("track", "未分類")
        staff = r.get("staff_name", "")
        category = r.get("category", "")
        is_correct = str(r.get("correct")).strip().lower() in ("true", "1")
        by_staff[track][staff]["total"] += 1
        by_staff[track][staff]["correct"] += 1 if is_correct else 0
        by_category[track][category]["total"] += 1
        by_category[track][category]["correct"] += 1 if is_correct else 0

    def _rate(stats):
        return round(100 * stats["correct"] / stats["total"]) if stats["total"] else 0

    ranking_by_track = {}
    for track in sheets.TRACKS:
        ranking_by_track[track] = sorted(
            (
                {"staff_name": name, "correct": s["correct"], "total": s["total"], "rate": _rate(s)}
                for name, s in by_staff.get(track, {}).items()
            ),
            key=lambda x: x["rate"],
            reverse=True,
        )

    category_stats_by_track = {}
    for track in sheets.TRACKS:
        category_stats_by_track[track] = [
            {"category": name, "correct": s["correct"], "total": s["total"], "rate": _rate(s)}
            for name, s in by_category.get(track, {}).items()
        ]

    return render_template(
        "admin_dashboard.html", tracks=sheets.TRACKS,
        ranking_by_track=ranking_by_track, category_stats_by_track=category_stats_by_track,
        pv_by_page=pv_by_page, pv_total=pv_total, pv_daily=pv_daily,
    )


@app.route("/admin/questions", methods=["GET", "POST"])
def admin_questions():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        track = request.form.get("track", "").strip()
        category = request.form.get("category", "").strip()
        question_text = request.form.get("question_text", "").strip()
        choices = [request.form.get(f"choice{i}", "").strip() for i in range(1, 5)]
        correct_index = int(request.form.get("correct_index", 0))
        explanation = request.form.get("explanation", "").strip()
        if track in sheets.TRACKS and category and question_text and choices[0] and choices[1]:
            sheets.add_question(track, category, question_text, choices, correct_index, explanation)
            flash("問題を追加しました")
        else:
            flash("編・カテゴリ・問題文・選択肢1・選択肢2は必須です")
        return redirect(url_for("admin_questions"))

    questions = sheets.list_questions()
    return render_template("admin_questions.html", questions=questions, tracks=sheets.TRACKS)


@app.route("/admin/questions/<question_id>/delete", methods=["POST"])
def admin_delete_question(question_id):
    if not _require_admin():
        return redirect(url_for("admin_login"))
    sheets.delete_question(question_id)
    flash("問題を削除しました")
    return redirect(url_for("admin_questions"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
