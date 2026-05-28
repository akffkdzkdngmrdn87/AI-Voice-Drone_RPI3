# AI 음성 드론_RPI3 (On-Device AI Autonomous Drone Control System)
> 제한된 에지 컴퓨팅 자원(1GB RAM) 및 EXAONE 32B INT4 양자화 모델 기반 무인 항공기(UAV) 자율 비행 제어 아키텍처

본 저장소는 거대 언어 모델(LLM)의 자연어 처리 및 인지 능력을 무인 항공기(UAV)의 물리적 기동 제어와 통합한 '임베디드 AI(Embodied AI)' 실증 연구 프로젝트입니다. 대규모 클라우드 인프라에 의존하지 않고, 가용 메모리가 1GB에 불과한 에지 컴퓨팅(Edge Computing) 환경 내에서 시스템을 독립적으로 구동시키는 '온디바이스(On-Device)' 아키텍처 구현을 목표로 설계되었습니다.

## 🌟 Core Architecture & Features (핵심 기술 및 구조)

### 1. 분산 제어 아키텍처 설계 (3-Node Resource Distribution)
라즈베리파이 3(1GB RAM) 단일 노드 환경에서 발생하는 메모리 부족(OOM) 및 연산 병목 현상을 해결하기 위해 시스템의 논리적 역할을 분리하였습니다.
* **AI 추론 노드 (aicar):** 320억 개 파라미터 규모의 거대 언어 모델(LLM) 로드 및 제어 명령 추론 연산 전담.
* **지상 관제국 (bn):** 가상 물리 엔진(SITL) 구동, 음성 인식(STT) 처리 및 노드 간 통신 라우팅 허브 역할 수행. ROS 2와 PX4 환경 간의 이기종 통신 규격(uORB)을 직렬화하는 'MicroXRCE-DDS' 미들웨어 운용.
* **에지 노드 (piaic):** 물리 엔진 기동 및 3차원 비행 역학 제어에 하드웨어 리소스를 집중 할당.

### 2. 대규모 언어 모델 최적화 및 RAG 구축
* **4-bit 양자화(INT4):** 복합 제어 명령 처리를 위해 EXAONE 4.0 32B 모델을 채택하였으며, 단일 GPU(12GB VRAM) 환경에서의 구동을 위해 Q4_K_M 포맷으로 가중치를 양자화하여 VRAM 점유율을 최적화하였습니다.
* **도메인 특화 RAG:** LLM의 환각(Hallucination) 현상을 억제하고 정규화된 기계어 매핑의 신뢰성을 확보하기 위해 검색 증강 생성 알고리즘을 도입하였습니다.

### 3. 훈련 데이터 증강 및 QLoRA 미세조정(Fine-Tuning)
* **음성 노이즈 주입 알고리즘:** 야외 환경의 음향적 노이즈로 인한 음성 인식 오류 패턴을 분석하여, 알고리즘 상에서 70%의 난수 확률로 텍스트 훼손 노이즈를 주입하였습니다. 이를 통해 약 1,500만 자 규모의 강건성(Robustness) 특화 훈련 데이터셋을 자동 구축하였습니다.
* **QLoRA 미세조정:** 12GB VRAM 제약 하에서 모델의 기저 가중치를 동결하고 저차원 어댑터(Low-Rank Adapter) 행렬만을 선별적으로 학습하여 제어 명령 추론 정확도를 향상시켰습니다.

### 4. 3차원 비행 역학 제어 및 고도 보정 알고리즘
* 자연어 명령을 기반으로 기체의 방향각(Yaw)과 기울기(Pitch)를 삼각함수로 연산하여 NED(North, East, Down) 좌표계 기준의 3D 목표 웨이포인트(Waypoint)를 산출합니다.
* **절대 고도 기준점 (Absolute Altitude Anchor):** 복합 기동 중 발생하는 누적 제어 오차로 인한 기체 수직 고도 하락 현상을 보정하기 위해, 초기 이륙 고도를 전역 변수로 할당(Anchoring)하여 수직 제어의 역학적 안정성을 확보하였습니다.

## 🛠 Tech Stack (기술 스택)
* **AI & LLM:** EXAONE 4.0 32B, llama.cpp, QLoRA (INT4 Quantization)
* **Robotics & Simulation:** ROS 2 Humble, PX4 Autopilot, Gazebo SITL (gz_x500)
* **Hardware:** Raspberry Pi 3 (Edge Node), RTX 4070 (GCS Node)
* **Language/Middleware:** Python 3.10, C++, MicroXRCE-DDS

## ⚙️ Prerequisites (사전 준비 및 설치 사항)

### 1. 언어 모델(LLM) 다운로드
음성 제어 추론을 위한 **EXAONE 4.0 32B (Q4_K_M GGUF)** 모델은 플랫폼 용량 제한으로 인해 Hugging Face를 경유하여 로컬 환경에 직접 다운로드해야 합니다.
~~~bash
# Hugging Face CLI 설치 및 인증 진행 (Access Token 필요)
pip install -U "huggingface_hub[cli]"
huggingface-cli login

# GGUF 모델 다운로드 (루트 디렉토리 내 models 디렉토리에 저장)
mkdir -p models
huggingface-cli download \
  [HuggingFace_Repository_Name]/EXAONE-4.0-32B-Instruct-Q4_K_M.gguf \
  --local-dir ./models \
  --local-dir-use-symlinks False
~~~

### 2. 가상 물리 엔진(PX4/Gazebo) 및 관제 소프트웨어(QGC) 설치
지상 관제국(`bn`) 시스템에 시뮬레이션 환경과 모니터링 툴을 구축합니다.
~~~bash
# PX4 Autopilot 소스코드 클론 및 환경 설정 스크립트 실행
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh

# QGroundControl(QGC) 다운로드 및 실행 권한 부여
wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-x86_64.AppImage
chmod +x ./QGroundControl-x86_64.AppImage
~~~

## 🚀 How to Run (실행 방법)

본 시스템은 3개의 독립적인 하드웨어 노드(`aicar`, `bn`, `piaic`) 환경에서 분산 구동됩니다. 데이터 스트림의 종속성에 따라 아래의 순서대로 시스템을 기동해야 합니다.

### 1. AI Brain Node (`aicar` 콤퓨타)
거대 언어 모델(LLM) 기반의 추론 서버를 최우선적으로 가동하여 자연어 처리 대기 상태를 확보합니다.
~~~bash
cd ~/AI_Voice_Drone_Project/aicar_brain_node
python3 -u llm_brain.py
~~~

### 2. GCS Server Node (`bn` 콤퓨타)
지상 관제국 환경에서는 가상 물리 엔진(SITL), 통신 미들웨어, 관제 소프트웨어(QGC), 음성 라우팅 허브를 구동합니다. 각각 독립된 터미널 세션을 열어 순차적으로 실행합니다.
~~~bash
# [터미널 1] 가상 물리 엔진(Gazebo) 및 PX4 제어기 기동
cd ~/PX4-Autopilot
make px4_sitl gz_x500

# [터미널 2] ROS 2 - PX4 통신 브릿지 기동
MicroXRCEAgent udp4 -p 8888

# [터미널 3] 지상 관제 소프트웨어(QGC) 기동
cd ~
./QGroundControl-x86_64.AppImage

# [터미널 4] 통신 라우팅 허브 및 음성 인식(STT) 에이전트 기동
cd ~/AI_Voice_Drone_Project/bn_gcs_node
python3 -u bn_hub_server.py
python3 -u bn_voice_agent.py
~~~

### 3. Edge Node (`piaic` 콤퓨타 - Raspberry Pi 3)
GCS 서버의 통신망 및 물리 엔진이 정상적으로 구축된 것을 확인한 후, 에지 디바이스에서 3차원 비행 역학 제어 스크립트를 최종적으로 실행합니다.
~~~bash
cd ~/AI_Voice_Drone_Project/piaic_edge_node
python3 -u drone_control.py
~~~

## 📈 Future Roadmap
* **프로토타입 3단계 실증:** 본 가상 물리 환경(SITL) 시뮬레이션을 통해 검증된 비행 제어 알고리즘 스크립트를 실제 F450 프레임 기반의 멀티콥터 기체 하드웨어에 직접 이식하여, 야외 물리적 환경에서의 비행 성능 및 제어 신뢰성을 평가할 계획입니다.
