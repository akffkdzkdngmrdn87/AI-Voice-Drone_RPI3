#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# [aicar 콤퓨타 전용] 궁극의 15만 개 복합 기동 & 극한 발음 파괴 교본 자동 생산소
# MIT, 스탠퍼드 AI 논문의 '문자 단위 교란술'을 반영한 극한 노이즈 주입 엔진!
# ==============================================================================

import json
import random

def apply_infinite_phonetic_destruction(text):
    """
    사령관 동무의 지시대로, 전장의 혹한기 얼어붙은 입술에서 나오는 
    모든 뭉개진 발음을 무한대에 가깝게 파괴하여 주입합네다!
    """
    # 🚨 30% 확률로 또렷하게 말하고, 70% 확률로 무자비하게 발음을 뭉깹네다!
    if random.random() > 0.7: 
        return text
    
    # 🚨 [1단계] 똘똘이가 영혼을 갈아 넣은 극한의 발음 파괴 사전!
    extreme_replacements = {
        '도착': ['두착', '도창', '토착', '도짝', '뚜착', '도챡', '도차악'],
        '착륙': ['창륙', '장육', '장륙', '창뉵', '챵뉵', '착육', '착뉵', '차륙', '찰뉵', '내려앉아라', '땅에박아라', '챡륙'],
        '고도': ['구도', '고두', '호도', '높이', '고더', '꼬도', '고됴'],
        '상승': ['상숭', '샹승', '쌍승', '위로가라', '상씀', '상슨', '샹슩', '올라가라', '상승해'],
        '하강': ['아강', '하걍', '밑으로까라', '하강해라', '아걍', '하캉', '화강', '내려가라'],
        '전진': ['전징', '젅진', '앞으로가라', '전진해', '전지인', '쪈진', '젼진', '앞으로가'],
        '좌회전': ['자회전', '좌해전', '자해전', '왼쪽으로틀어라', '자외전', '좌외전', '쫘회전', '자웨전', '왼쪽으로돌아'],
        '우회전': ['우해전', '우에전', '오른쪽으로틀어라', '우외전', '우웨전', '우히전', '우측으로돌아'],
        '정지': ['점지', '정찌', '멈춰', '점찌', '전지', '스톱', '정지해라', '가만히있어'],
        '목표': ['목펴', '몯표', '목뾰', '모표', '목포', '목표물'],
        '복귀': ['복끼', '볻귀', '보끼', '복기', '봌귀', '돌아와라'],
        '거리': ['거리', '거뤼', '거르', '거디'],
        '남았다': ['나마따', '남앗다', '남았당', '남아따', '남아쓰']
    }
    
    result = text
    for key, values in extreme_replacements.items():
        if key in result and random.random() < 0.8: # 파괴될 확률을 극대화!
            result = result.replace(key, random.choice(values))
            
    # 🚨 [2단계] 알고리즘 숫자의 교란! (1000 -> 천, 1만 등 무작위 섞기)
    if '0000' in result and random.random() < 0.5:
        result = result.replace('0000', '만')
    elif '000' in result and random.random() < 0.5:
        result = result.replace('000', '천')
        
    return result

def generate_massive_dataset(num_samples=150000): # 🚨 15만 개 초대용량!
    print(f"🔥 [초대형 공장 가동] {num_samples}개의 뭉개진 발음 & 복합 기동 교본 생산 중...")
    
    # [전술 1] 단일 기동 명령
    single_actions = [
        ("고도를 올려라", "고도를 {val}{unit} 상승합네다."),
        ("앞으로 전진해라", "전방으로 {val}{unit} 진격합네다."),
        ("착륙해라", "고도를 낮추고 {val}{unit} 밖 안전 구역에 착륙합네다."),
        ("복귀하라", "즉시 본진으로 복귀 기동을 개시합네다.")
    ]
    
    # 🚨 [전술 2] 사령관 동무가 직접 지시한 [연속 복합 기동 명령]!
    complex_actions = [
        ("앞으로 {val1}{unit} 가다가 정지한 이후에 좌회전해서 {val2}{unit} 가라", 
         "명령 수신: 전방으로 {val1}{unit} 이동 후 정지, 좌측으로 90도 회전하여 {val2}{unit} 추가 진격합네다!"),
        ("고도를 {val1}{unit} 올리고 우회전한 다음 {val2}{unit} 전진해라", 
         "명령 수신: 고도 {val1}{unit} 상승 후 우측 회전, 이어서 {val2}{unit} 전방으로 이동합네다!"),
        ("{val1}{unit} 후퇴한 뒤에 정지하고, 고도를 {val2}{unit} 깎아라", 
         "명령 수신: 후방으로 {val1}{unit} 후퇴 후 대기, 즉시 고도를 {val2}{unit} 하강합네다!"),
        ("목표까지 {val1}{unit} 전진 후 착륙하고 {val2}분간 대기하라",
         "명령 수신: 전방으로 {val1}{unit} 이동 후 착륙, 해당 위치에서 {val2}분간 대기 모드로 전환합네다!")
    ]
    
    units = ["m", "km", "피트", "마일", "메다", "센치"]
    dataset = []
    
    for i in range(num_samples):
        # 50% 확률로 단일 명령, 50% 확률로 복잡한 2연속 복합 명령을 훈련시킵네다!
        if random.random() < 0.5:
            val = random.randint(10, 50000)
            unit = random.choice(units)
            action_in, action_out = random.choice(single_actions)
            raw_instruction = f"거리 {val}{unit} 남았다. {action_in}"
            response = action_out.format(val=val, unit=unit)
        else:
            val1 = random.randint(5, 1000)
            val2 = random.randint(5, 1000)
            unit = random.choice(units)
            action_in, action_out = random.choice(complex_actions)
            raw_instruction = action_in.format(val1=val1, val2=val2, unit=unit)
            response = action_out.format(val1=val1, val2=val2, unit=unit)
        
        # 🚨 발음 파괴 엔진 통과!
        instruction = apply_infinite_phonetic_destruction(raw_instruction)
        
        dataset.append({
            "instruction": instruction,
            "response": response
        })

    # 파일 저장
    output_file = "massive_drone_knowledge.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for data in dataset:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    print(f"✅ [생성 완료] 15만 개의 무적 교본이 '{output_file}'에 적재되었습네다!")
    print("   ('창뉵', '장육', '쫘회전' 등 극한의 얼어붙은 발음이 완벽히 포함되었습네다!)")

if __name__ == "__main__":
    generate_massive_dataset()

