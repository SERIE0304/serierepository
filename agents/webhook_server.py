from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(json.dumps(data, indent=2, ensure_ascii=False))
    for event in data.get('events', []):
        user_id = event.get('source', {}).get('userId', 'なし')
        print(f"\n★★★ User ID: {user_id} ★★★\n")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=8080)
