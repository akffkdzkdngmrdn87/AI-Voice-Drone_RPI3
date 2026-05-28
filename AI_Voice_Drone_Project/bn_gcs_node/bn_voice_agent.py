#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket, sys
import speech_recognition as sr
from ctypes import *

# ALSA 에러 입틀막
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except: pass

# 본진 내부망(Localhost) 통신
HUB_IP = "127.0.0.1" 
running = True

def stt_task():
    global running
    r = sr.Recognizer()
    r.energy_threshold = 150
    r.pause_threshold = 1.5 
    
    # 마이크 자동 검색 (본진 ABKO 웹캠 마이크)
    m_idx = next((i for i, n in enumerate(sr.Microphone.list_microphone_names()) if any(x in n.lower() for x in ["usb", "webcam", "camera"])), None)
    mic = sr.Microphone(device_index=m_idx)
    
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=2)
        print("🎙️ [Type 2 본진 관제탑] 사령관 동무 전용 마이크 개통 완료!", flush=True)
        print("🎙️ [상태] '아리온' 호출 대기 중... (종료: Ctrl+C)", flush=True)
        
        is_rec = False
        buf = ""
        while running:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=10)
                text = r.recognize_google(audio, language="ko-KR")
                
                if not is_rec:
                    if "아리온" in text:
                        is_rec = True
                        buf = text.split("아리온")[-1]
                        print("🚨 [녹음] 사령관 동무의 명령 수집 시작!", flush=True)
                else:
                    buf += " " + text
                    print(f"  [수집]: {buf.strip()}", flush=True)
                    
                if is_rec and ("오버" in buf or "오바" in buf):
                    cmd = buf.replace("오바", "오버").split("오버")[0].strip()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5.0)
                    s.connect((HUB_IP, 9998))
                    s.send(cmd.encode('utf-8'))
                    s.close()
                    print(f"📡 [완료] 중앙 두뇌로 타전 성공: {cmd}", flush=True)
                    is_rec = False
                    buf = ""
            
            except KeyboardInterrupt:
                running = False
                break
            except sr.WaitTimeoutError:
                pass
            except Exception:
                pass
                
    print("\n🛑 [철수] 사령관 전용 마이크 시스템을 안전하게 종료합네다!", flush=True)

if __name__ == '__main__':
    try:
        stt_task()
    except KeyboardInterrupt:
        running = False
        sys.exit(0)

