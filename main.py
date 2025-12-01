from flask import Flask, render_template, request, jsonify
import time, os, json
from datetime import datetime

app = Flask(__name__)

door_command = "NONE"
SECRET_TOKEN = None
TOKEN_EXPIRE = 0  
CURRENT_USER = None
LOG_FILE = "door_logs.json"

# Tạo file log nếu chưa có
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def save_log(user_id, action):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)

    logs.append({
        "user_id": user_id,
        "action": action,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Giờ máy bạn
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

# ========== API nhận token + user_id ==========
@app.route('/set_token', methods=['POST'])
def set_token():
    global SECRET_TOKEN, TOKEN_EXPIRE, CURRENT_USER
    data = request.get_json()
    token = data.get("token", "")
    user_id = data.get("user_id", "")

    if not token or not user_id:
        return jsonify({"error": "Thiếu token hoặc user_id!"}), 400

    SECRET_TOKEN = token
    TOKEN_EXPIRE = time.time() + 300
    CURRENT_USER = user_id
    print(f"🔑 Nhận token mới từ user '{user_id}': {SECRET_TOKEN[:8]}...")
    return jsonify({"message": "Token + user_id đã cập nhật thành công!"})

# ========== Giao diện điều khiển ==========
@app.route('/')
def home():
    token = request.args.get("token", "")
    if not SECRET_TOKEN or time.time() > TOKEN_EXPIRE:
        return "❌ Token hết hạn hoặc chưa được thiết lập.", 403
    if token != SECRET_TOKEN:
        return "❌ Token không hợp lệ.", 403
    return render_template('dieukhiencua.html')

# ========== API điều khiển cửa ==========
@app.route('/door_control', methods=['POST'])
def door_control():
    global door_command, CURRENT_USER
    data = request.get_json()
    cmd = str(data.get('command', '')).strip().lower()

    if cmd in ['open', '1', 'on', 'mo', 'mở']:
        door_command = "OPEN"
        save_log(CURRENT_USER, "MỞ cửa")
        return "✅ Lệnh MỞ cửa đã gửi!"
    elif cmd in ['close', '0', 'off', 'dong', 'đóng']:
        door_command = "CLOSE"
        save_log(CURRENT_USER, "ĐÓNG cửa")
        return "✅ Lệnh ĐÓNG cửa đã gửi!"
    else:
        return "⚠️ Lệnh không hợp lệ.", 400

# ========== API ESP32 lấy lệnh ==========
@app.route('/get_command', methods=['GET'])
def get_command():
    global door_command
    cmd = door_command
    door_command = "NONE"
    return cmd

# ========== API lấy log ==========
@app.route('/logs', methods=['GET'])
def logs():
    token = request.args.get("token", "")
    if token != SECRET_TOKEN:
        return "❌ Token không hợp lệ.", 403
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
    return jsonify(logs)

# ========== Chạy server ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
