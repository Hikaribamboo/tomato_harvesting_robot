import cv2
import numpy as np
import requests
import time

ESP_IP = "http://192.168.0.6"  # ← 自分のESP8266のIPに変更

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- 赤色のトマト検出（HSV空間） ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    # --- トマトの輪郭検出 ---
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    target = None
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            x, y, w, h = cv2.boundingRect(c)
            center = (x + w//2, y + h//2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
            target = center

    cv2.imshow("Tomato Detection", frame)

    # --- トマトが見つかったら座標送信 ---
    if target:
        x, y = target
        print(f"Send to ESP: x={x}, y={y}")
        try:
            requests.get(f"{ESP_IP}/move?x={x}&y={y}", timeout=2)
        except:
            print("⚠️ ESPに接続できません")
        time.sleep(3)  # 3秒待機して繰り返す

    if cv2.waitKey(1) & 0xFF == 27:  # ESCで終了
        break

cap.release()
cv2.destroyAllWindows()
