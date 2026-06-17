import json
import os
import time
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

_questions_cache = None
_questions_cache_time = 0
_CACHE_TTL = 300  # 5分間キャッシュ

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_ID = os.environ.get("QUIZ_SPREADSHEET_ID")

TRACKS = ["実務編", "フランチャイジー編"]

QUESTIONS_HEADER = [
    "id", "track", "category", "question_text",
    "choice1", "choice2", "choice3", "choice4",
    "correct_index", "explanation",
]
RESPONSES_HEADER = [
    "timestamp", "staff_name", "track", "question_id", "category",
    "selected_index", "correct",
]
INQUIRIES_HEADER = [
    "timestamp", "name", "email", "phone", "message",
]


def _client():
    if CREDENTIALS_JSON:
        info = json.loads(CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def _spreadsheet():
    return _client().open_by_key(SPREADSHEET_ID)


def _get_or_create_sheet(name, header):
    ss = _spreadsheet()
    try:
        ws = ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=1000, cols=len(header))
        ws.append_row(header)
        return ws
    if ws.row_values(1) != header:
        ws.update("A1", [header])
    return ws


def questions_sheet():
    return _get_or_create_sheet("Questions", QUESTIONS_HEADER)


def responses_sheet():
    return _get_or_create_sheet("Responses", RESPONSES_HEADER)


def _all_questions():
    global _questions_cache, _questions_cache_time
    if _questions_cache is None or (time.time() - _questions_cache_time) > _CACHE_TTL:
        _questions_cache = questions_sheet().get_all_records()
        _questions_cache_time = time.time()
    return _questions_cache


def _invalidate_cache():
    global _questions_cache
    _questions_cache = None


def list_questions(track=None, category=None):
    rows = _all_questions()
    if track:
        rows = [r for r in rows if r.get("track") == track]
    if category:
        rows = [r for r in rows if r.get("category") == category]
    return rows


def list_categories(track=None):
    rows = _all_questions()
    if track:
        rows = [r for r in rows if r.get("track") == track]
    seen = []
    for r in rows:
        c = r.get("category")
        if c and c not in seen:
            seen.append(c)
    return seen


def next_question_id():
    rows = _all_questions()
    ids = [int(r["id"]) for r in rows if str(r.get("id", "")).isdigit()]
    return max(ids, default=0) + 1


def add_question(track, category, question_text, choices, correct_index, explanation):
    ws = questions_sheet()
    qid = next_question_id()
    choices = (choices + ["", "", "", ""])[:4]
    ws.append_row([qid, track, category, question_text, *choices, correct_index, explanation])
    _invalidate_cache()
    return qid


def delete_question(question_id):
    ws = questions_sheet()
    rows = ws.get_all_values()
    for i, row in enumerate(rows[1:], start=2):
        if row and row[0] == str(question_id):
            ws.delete_rows(i)
            _invalidate_cache()
            return True
    return False


def record_response(staff_name, track, question_id, category, selected_index, correct):
    ws = responses_sheet()
    ws.append_row([
        datetime.now().isoformat(timespec="seconds"),
        staff_name,
        track,
        question_id,
        category,
        selected_index,
        bool(correct),
    ])


def all_responses():
    return responses_sheet().get_all_records()


def inquiries_sheet():
    return _get_or_create_sheet("Inquiries", INQUIRIES_HEADER)


def record_inquiry(name, email, phone, message):
    ws = inquiries_sheet()
    ws.append_row([
        datetime.now().isoformat(timespec="seconds"),
        name, email, phone, message,
    ])
