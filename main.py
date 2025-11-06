from flask import Flask, render_template, request, jsonify
import time, os

app = Flask(__name__)

door_command = "NONE"

# 🔐 Token động (được đặt bởi chương trình nhận diện)
SECRET_TOKEN = None
TOKEN_EXPIRE = 0  # thời điểm hết hạn token

# ========== API: Client đặt token ==========
@app.route('/set_token', methods=['POST'])
def set_token():
    global SECRET_TOKEN, TOKEN_EXPIRE
    data = request.get_json()
    token = data.get("token", "")
    if not token:
        return jsonify({"error": "Thiếu token!"}), 400

    SECRET_TOKEN = token
    TOKEN_EXPIRE = time.time() + 300  # sống 5 phút
    print(f"🔑 Đã nhận token mới: {SECRET_TOKEN[:8]}... (hết hạn sau 5 phút)")
    return jsonify({"message": "Token đã cập nhật thành công!"})


# ========== Giao diện điều khiển ==========
@app.route('/')
def home():
    global SECRET_TOKEN, TOKEN_EXPIRE
    token = request.args.get("token", "")

    if not SECRET_TOKEN or time.time() > TOKEN_EXPIRE:
        return "❌ Token hết hạn hoặc chưa được thiết lập. Vui lòng xác thực lại.", 403
    if token != SECRET_TOKEN:
        return "❌ Truy cập bị từ chối. Token không hợp lệ.", 403

    return render_template('dieukhiencua.html')


# ========== API: Điều khiển cửa ==========
@app.route('/door_control', methods=['POST'])
def door_control():
    global door_command
    data = request.get_json()
    cmd = str(data.get('command', '')).strip().lower()

    if cmd in ['open', '1', 'on', 'mo', 'mở']:
        door_command = "OPEN"
        return "✅ Lệnh MỞ cửa đã gửi!"
    elif cmd in ['close', '0', 'off', 'dong', 'đóng']:
        door_command = "CLOSE"
        return "✅ Lệnh ĐÓNG cửa đã gửi!"
    else:
        return "⚠️ Lệnh không hợp lệ.", 400


# ========== API: ESP32 lấy lệnh ==========
@app.route('/get_command', methods=['GET'])
def get_command():
    global door_command
    cmd = door_command
    door_command = "NONE"
    return cmd


# ========== Chạy ứng dụng ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render tự cấp PORT
    app.run(host="0.0.0.0", port=port)
