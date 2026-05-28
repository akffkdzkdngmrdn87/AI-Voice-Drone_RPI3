#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket, re, json, random
from llama_cpp import Llama
import jinja2

_original_init = jinja2.Environment.__init__
def _patched_init(self, *args, **kwargs):
    ext = kwargs.get("extensions", [])
    if "jinja2.ext.loopcontrols" not in ext: kwargs["extensions"] = list(ext) + ["jinja2.ext.loopcontrols"]
    _original_init(self, *args, **kwargs)
jinja2.Environment.__init__ = _patched_init

def load_our_glorious_data():
    data_list = []
    try:
        with open("massive_drone_knowledge.jsonl", "r", encoding="utf-8") as f:
            for line in f: data_list.append(json.loads(line))
    except Exception: pass
    return data_list

def get_advice_from_data(data_list):
    if not data_list: return ""
    advice = "\n[참고 데이터]\n"
    for s in random.sample(data_list, min(3, len(data_list))): 
        advice += f"- 사용자 지시: {s.get('instruction', '')}\n"
    return advice

def main():
    print("🚀 [aicar] 엑사원(LLM) 두뇌 가동! (사령관 특명: WAIT 삭제 & 정밀 각도 타격망 탑재)")
    our_data = load_our_glorious_data()
    llm = Llama(model_path="./EXAONE-4.0-32B-Q4_K_M.gguf", n_ctx=2048, n_gpu_layers=35, chat_format="chatml", verbose=False)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 9999)) 
    server_socket.listen(5)
    
    while True:
        conn, addr = server_socket.accept()
        try:
            raw = conn.recv(4096).decode('utf-8')
            if not raw: continue

            # 🌟 [사령관 동무 특명 1] 위대한 STT 발음 교정 방어막 (유지)
            data = raw.replace("269", "이륙해").replace("26회", "이륙해").replace("26해", "이륙해").replace("이육해", "이륙해").replace("일육해", "이륙해").replace("이륙 해", "이륙해").replace("이렇게", "이륙해")
            data = data.replace("장육해", "착륙해").replace("장유해", "착륙해").replace("착육해", "착륙해").replace("창육해", "착륙해").replace("착륙 해", "착륙해")
            data = data.replace("26", "이륙").replace("이육", "이륙").replace("장육", "착륙")
            data = data.replace("전방", "전진").replace("전징","전진").replace("진징", "전진").replace("징진", "전진").replace("젠징", "전진")
            data = data.replace("백미터", "100m")
            data = data.replace("좌 ", "좌회전 ").replace("우 ", "우회전 ") 

            advice = get_advice_from_data(our_data)

            # 🌟 [사령관 동무 특명 2 & 3] WAIT 영구 삭제 및 조건부 각도 타격 규칙 맹렬 추가!!!
            sys_msg = f"""당신은 무인 자율 비행체(UAV) 제어 인공지능입니다.{advice}
[프로토콜 규격] 
전진:GO_FORWARD_[거리(m)]
후진:GO_BACKWARD_[거리(m)]
좌회전:TURN_LEFT_[각도(도)]
우회전:TURN_RIGHT_[각도(도)]
상향:PITCH_UP_[각도(도)]
하향:PITCH_DOWN_[각도(도)]
이륙:TAKEOFF_1.5
착륙:LAND_1.5

[🌟 3D 입체 기동 및 맹렬 돌격 규칙]
1. [대기 삭제] 불필요한 대기(WAIT) 명령은 일절 사용하지 말고 즉각 명령을 연달아 내리십시오.
2. [기본 각도 90도] 사용자가 각도를 생략하고 방향만 지시한 경우(예: '좌회전', '우회전', '좌측', '우측'), 무조건 기본값인 90도로 회전하십시오. (예: TURN_LEFT_90)
3. [정밀 각도 타격] 사용자가 명시적인 각도를 지시한 경우(예: '좌회전 15도', '우측 120도', '우회전 75도'), 90도로 임의 변경하지 말고 사용자가 부른 숫자 100% 그대로 기입하여 회전하십시오. (예: TURN_LEFT_15, TURN_RIGHT_120)
4. 이륙(날아올라 등)과 관련된 모든 명령은 TAKEOFF_1.5, 착륙(내려와 등)은 LAND_1.5로 통일합니다.

[예시]
'전진 100m' -> GO_FORWARD_100
'좌회전 50m' -> TURN_LEFT_90 \\n GO_FORWARD_50
'좌회전 15도 50m' -> TURN_LEFT_15 \\n GO_FORWARD_50
'우측 75도 전진 20m' -> TURN_RIGHT_75 \\n GO_FORWARD_20

[보안 규약] 응답은 오직 'COMMAND: [명령어]' 형식으로만 출력하십시오. 복합 명령은 반드시 줄바꿈(\\n)으로 구분하십시오."""

            resp = llm.create_chat_completion(
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": data}],
                max_tokens=250, temperature=0.1
            )
            answer = resp["choices"][0]["message"]["content"].strip()
            if not answer.startswith("COMMAND:"): answer = f"COMMAND: {answer}"
            pure_cmd = answer.replace("COMMAND:", "").strip()

            print(f"[추론 완료] 하달 명령:\n{pure_cmd}", flush=True)
            conn.send(pure_cmd.encode('utf-8'))
        except Exception: pass
        finally: conn.close()

if __name__ == '__main__': main()

