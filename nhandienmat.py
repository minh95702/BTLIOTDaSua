import cv2
import numpy as np
import os
import time
import requests

# ======= CẤU HÌNH SERVER RENDER =======
# ⚠️ ĐỔI đường link này thành link thật của bạn sau khi deploy Render
RENDER_URL = "https://your-render-app.onrender.com/door_control"

# ======= THƯ MỤC DỮ LIỆU =======
trained_dir = "trained_faces"

if not os.path.exists(trained_dir):
    print("❌ Không tìm thấy thư mục trained_faces! Hãy chạy file train trước.")
    exit()

# ======= ĐỌC ẢNH TRUNG BÌNH CỦA TỪNG NGƯỜI =======
trained_faces = {}
for file in os.listdir(trained_dir):
    if file.lower().endswith((".jpg", ".png", ".jpeg")):
        name = os.path.splitext(file)[0]
        path = os.path.join(trained_dir, file)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            trained_faces[name] = cv2.resize(img, (100, 100))

if not trained_faces:
    print("❌ Không có dữ liệu khuôn mặt trong thư mục trained_faces!")
    exit()

print(f"✅ Đã tải {len(trained_faces)} mẫu khuôn mặt trung bình.")

# ======= KHỞI TẠO NHẬN DIỆN KHUÔN MẶT =======
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ======= MỞ CAMERA =======
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Không mở được camera!")
    exit()

print("🎯 Bắt đầu nhận diện (tự dừng khi phát hiện khuôn mặt đúng).")

# ======= HÀM TÍNH ĐỘ KHÁC BIỆT =======
def face_distance(img1, img2):
    return np.sqrt(np.mean((img1.astype("float") - img2.astype("float")) ** 2))

# ======= VÒNG LẶP CHÍNH =======
recognized = False
recognized_name = None
threshold = 60.0  # Ngưỡng nhận diện: có thể chỉnh 50–80

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được khung hình!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (100, 100))

        # So sánh với từng mẫu
        min_dist = float("inf")
        best_name = "Unknown"

        for name, avg_face in trained_faces.items():
            dist = face_distance(face, avg_face)
            if dist < min_dist:
                min_dist = dist
                best_name = name

        if min_dist > threshold:
            best_name = "Unknown"

        # Hiển thị
        color = (0, 255, 0) if best_name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"{best_name} ({min_dist:.1f})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Nếu nhận diện đúng => thoát
        if best_name != "Unknown":
            recognized = True
            recognized_name = best_name
            print(f"✅ Nhận diện thành công: {best_name} (độ lệch {min_dist:.1f})")
            time.sleep(1)
            break

    cv2.imshow("Nhận diện khuôn mặt", frame)

    if recognized:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ======= KẾT THÚC CAMERA =======
cap.release()
cv2.destroyAllWindows()

# ======= GỬI LỆNH MỞ CỬA LÊN SERVER =======
if recognized:
    print(f"🚪 Mở cửa cho: {recognized_name}")
    try:
        res = requests.post(RENDER_URL, json={"command": "open"}, timeout=5)
        if res.status_code == 200:
            print("✅ Đã gửi lệnh mở cửa lên server Render.")
        else:
            print(f"⚠️ Server trả mã lỗi: {res.status_code}")
    except Exception as e:
        print("❌ Lỗi khi gửi yêu cầu tới server:", e)
else:
    print("❌ Không nhận diện được khuôn mặt nào hợp lệ.")
