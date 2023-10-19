import cv2
import mediapipe as mp
# import socket
import time  # 导入time模块以使用sleep功能

# 初始化MediaPipe和摄像头
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

# 初始化socket客户端
# # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '10.50.185.91'  # 请替换为Jetson的实际IP地址
server_port = 65432  # 服务器端口号应与服务器代码中的一致
# # client_socket.connect((server_ip, server_port))

# 初始化变量
is_recording = False
initial_position_x = None
prev_wrist_x = None
angle = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        wrist_x = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist_position = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                wrist_x = int(wrist_position.x * frame.shape[1])
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        key = cv2.waitKey(1)
        
        if key == 13:  # Enter键
            if not is_recording:
                if wrist_x is not None:
                    initial_position_x = wrist_x
                    is_recording = True
            else:
                is_recording = False
        
        elif key == 27:  # ESC键
            break
        
        if is_recording and wrist_x is not None and initial_position_x is not None:
            distance_moved_x = wrist_x - initial_position_x
            if prev_wrist_x is not None:
                if wrist_x > prev_wrist_x:
                    angle += 2
                elif wrist_x < prev_wrist_x:
                    angle -= 2
                angle = max(0, min(180, angle))  # 将角度限制在0到180度之间
#                 client_socket.sendall((str(angle) + '\n').encode('utf-8'))
                print(f"Sent angle: {angle}") 
                time.sleep(0.01)  # 每次发送数据后，暂停秒
            prev_wrist_x = wrist_x
        
            cv2.putText(frame, f"Angle: {angle}", (frame.shape[1] - 150, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        
        cv2.imshow('Hand Tracking', frame)

finally:
#     client_socket.close()
    cap.release()
    cv2.destroyAllWindows()
