import os
import json
import time
from datetime import datetime
from get_line_token import get_line_token

TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = "U206a030c1759f1ed8f4c684d03d11915"

def send_line_message(message, retries=2):
    import urllib.request, urllib.error
    data = json.dumps({"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}).encode("utf-8")
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            "https://api.line.me/v2/bot/message/push",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + LINE_CHANNEL_TOKEN}
        )
        try:
            urllib.request.urlopen(req)
            return
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"LINE送信失敗（{attempt + 1}回目）: HTTP {e.code} {body}")
            if attempt < retries:
                time.sleep(2)
            else:
                raise

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": []}

def save_tasks(data):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_task(category, task_text):
    data = load_tasks()
    data["tasks"].append({
        "category": category,
        "task": task_text,
        "done": False,
        "added": datetime.now().strftime("%Y/%m/%d"),
        "week": datetime.now().strftime("%Y-W%W")
    })
    save_tasks(data)

def send_friday_review():
    data = load_tasks()
    today = datetime.now().strftime("%Y/%m/%d")
    tasks = data.get("tasks", [])
    current_week = datetime.now().strftime("%Y-W%W")
    this_week_tasks = [t for t in tasks if t.get("week") == current_week]

    if not this_week_tasks:
        msg = (
            "【週次タスク確認】" + today + "\n\n"
            "今週のタスクは記録されていません。\n"
            "月曜日のレポートを確認して来週のタスクを準備しましょう！💪"
        )
    else:
        done = [t for t in this_week_tasks if t.get("done")]
        pending = [t for t in this_week_tasks if not t.get("done")]
        msg = "【週次タスク確認】" + today + "\n\n"
        if done:
            msg += "✅ 完了済み\n"
            for t in done:
                msg += "【" + t["category"] + "】" + t["task"] + "\n"
            msg += "\n"
        if pending:
            msg += "⬜ 未完了\n"
            for t in pending:
                msg += "【" + t["category"] + "】" + t["task"] + "\n"
            msg += "\n週末中に完了を目指しましょう！\n未完了は月曜日に繰り越されます。"
        else:
            msg += "今週のタスクは全て完了です！素晴らしい！🎉"

    send_line_message(msg)
    print(msg)

if __name__ == "__main__":
    send_friday_review()
