from flask import Flask, render_template, request

app = Flask(__name__)

door_command = "NONE"

SECRET_TOKEN = "minhdoorsecure2025"

@app.route('/')
def home():
    token = request.args.get("token", "")
    if token != SECRET_TOKEN:
        return "❌ Truy cập bị từ chối. Bạn chưa được xác thực.", 403
    return render_template('dieukhiencua.html')

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

@app.route('/get_command', methods=['GET'])
def get_command():
    global door_command
    cmd = door_command
    door_command = "NONE"
    return cmd

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
