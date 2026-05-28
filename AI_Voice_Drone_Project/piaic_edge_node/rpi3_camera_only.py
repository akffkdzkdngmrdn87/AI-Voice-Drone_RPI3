#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2, socket, time, struct, sys

BN_IP = "192.168.3.92" 
running = True 

def video_stream_task():
    global running
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    print("🎥 [Type 2 척후병] 스텔스 카메라 가동! 오직 영상만 송출합네다!", flush=True)
    
    while running:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10.0) 
        try:
            client_socket.connect((BN_IP, 8899))
            while running:
                ret, frame = cap.read()
                if not ret: 
                    time.sleep(0.1)
                    continue
                frame = cv2.resize(frame, (640, 380))
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                if ret:
                    jpg_bytes = buffer.tobytes()
                    msg_size = struct.pack("Q", len(jpg_bytes))
                    client_socket.sendall(msg_size + jpg_bytes)
                time.sleep(0.1)
        except KeyboardInterrupt:
            running = False
            break
        except Exception: 
            if running:
                print("🎥 [영상] 통신 단절. 불사조처럼 재연결을 시도합네다...", flush=True)
                time.sleep(2)
        finally:
            client_socket.close()
    
    cap.release()
    print("\n🛑 [철수] 라즈베리파이 카메라 송출을 안전하게 종료합네다!", flush=True)

if __name__ == '__main__':
    try:
        video_stream_task()
    except KeyboardInterrupt:
        running = False
        sys.exit(0)

