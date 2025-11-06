from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

door_command = "NONE"

# 🔐 Token động (sẽ được set mỗi phiên bởi chương trình nhận diện)
SECRET_TOKEN = None
TOKEN_EXPIRE = 0  # thời điểm hết hạn token

# ========== API: NHẬN TOKEN MỚI TỪ CLIENT ========== #
@app.route('/set_token', methods=['POST'])
def set_token():
    """
    Client (chương trình nhận diện khuôn mặt) sẽ gọi POST /set_token 
    kèm token ngẫu nhiên. Server lưu token này trong 5 phút.
    """
    global SECRET_TOKEN, TOKEN_EXPIRE
    data = request.get_json()
    token = data.get("token", "")
    if not token:
        return jsonify({"error": "Thiếu token!"}), 400

    SECRET_TOKEN = token
    TOKEN_EXPIRE = time.time() + 300  # token sống 5 phút
    print(f"🔑 Đã nhận token mới: {SECRET_TOKEN[:8]}... (hết hạn sau 5 phút)")
    return jsonify({"message": "Token đã cập nhật thành công!"})


# ========== TRANG CHÍNH: GIAO DIỆN ĐIỀU KHIỂN ========== #
@app.route('/')
def home():
    global SECRET_TOKEN, TOKEN_EXPIRE
    token = request.args.get("token", "")

    # Kiểm tra hợp lệ
    if not SECRET_TOKEN or time.time() > TOKEN_EXPIRE:
        return "❌ Token hết hạn hoặc chưa được thiết lập. Vui lòng xác thực lại.", 403
    if token != SECRET_TOKEN:
        return "❌ Truy cập bị từ chối. Token không hợp lệ.", 403

    return render_template('dieukhiencua.html')


# ========== API: ĐIỀU KHIỂN CỬA ========== #
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


# ========== API: THIẾT BỊ ESP32 LẤY LỆNH MỚI NHẤT ========== #
@app.route('/get_command', methods=['GET'])
def get_command():
    global door_command
    cmd = door_command
    door_command = "NONE"
    return cmd


# ========== MAIN ========== #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
