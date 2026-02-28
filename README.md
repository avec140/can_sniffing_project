
# CAN_sniffing_project
> vCAN으로 구현한 차량 네트워크 스니핑 및 공격 검증 환경


## 프로젝트 개요(Overview)

현대 차량은 ECU 간 통신을 위해 **CAN (Controller Area Network)** 프로토콜을 사용한다.</br>  
하지만 CAN 통신은 인증(Authentication) 및 암호화(Encryption)가 존재하지 않는 구조적 특성을 가지며, 메시지 위조(Message Injection) 및 재전송(Replay) 공격에 취약하다.</br>
(지금은 보안 프로토콜 적용(SecOC)의 기술을 활용해 무결성을 보장하거나, CAN버스 상 IDS설치해 실시간으로 감지할 수 있도록 대책을 연구하고 있다.)</br>
본 프로젝트는 실제 차량 없이 Linux **SocketCAN(vCAN)** 환경에서 차량 네트워크 공격을 재현하고 분석하는 것을 목표로 한다.</br>

구현 내용:

- CAN Traffic Generation (ECU Simulation)
- CAN Packet Sniffing
- Replay / Injection / Fuzz Attack
- Automatic CSV Dataset Logging and attack session marking


## 프로젝트 목적(Objective)

> 차량 네트워크 공격을 재현하고 분석 가능한 실험 환경 구축

주요 목표:

- Virtual CAN 기반 ECU 통신 시뮬레이션
- 대표적인 CAN 공격 시나리오 구현
- 공격 구간 자동 Dataset 생성


## 시스템 아키텍처(Architecture)
Normal ECU Generator</br>
↓</br>
vcan0</br>
↓</br>
│ CAN Sniffer Logger │</br>
│ (CSV Dataset) │</br>
↓</br>
oneclick_attack</br>
ㅡ Replay Attack</br>
ㅡ Injection Attack</br>
ㅡ Fuzz Attack</br>


## 실험 환경(Environment)

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 |
| Interface | SocketCAN |
| Virtual CAN | vcan0 |
| Language | Python |
| Library | python-can |



## 프로젝트 구조(Project Structure)</br>
 - oneclick_attack.py # 공격 실행 관리 파일</br>
 - can_generator.py # 정상 CAN 트래픽 생성</br>
 - log_sniffer_logger.py # CAN 스니핑 및 CSV 저장</br>
 - replay_attack.py # replay 공격 </br>
 - injection_attack.py #비정상 패킷 injection 공격</br>
 - fuzz_attack.py # fuzzing 공격</br>
 - logs/</br>
 - README.md</br>

## 실행 방법(Usage)


### 1. VCAN 실행
```python
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### 2. 정상 CAN 트래픽 생성
```python
python3 can_generator.py
```
ECU 통신을 가정한 주기적 CAN 메시지를 생성한다.


### 3. 공격 실행
```python
python3 oneclick_attack.py
```
공격기법 선택 가능
1. Replay Attack
2. Injection Attack
3. Fuzz Attack


### 4. 공격 종료
```
ctrl + c
```

공격 종료 시 자동으로:
- CSV 로그 저장
- 공격 시작/종료 Marker 기록
- Dataset 생성 완료

```
생성되는 CAN Dataset
timestamp,can_id,dlc,data_hex
1709050000,MARK_START:Replay_Attack,0,
1709050001,0x100,8,0102030405060708
1709050010,MARK_END:Replay_Attack,0,
```

Marker System
Marker	Description
MARK_START	Attack Start
MARK_END	Attack End

공격 구간을 명확히 분리하여 IDS 분석 및 데이터셋 활용 가능하다.



## 구현된 공격 시나리오(Attack Scenarios)
1. Replay Attack
 - 정상 CAN 메시지를 비정상 주기로 재전송하여 ECU 취약점 재현

2. Injection Attack
 - 위조된 CAN Identifier 및 Payload 주입 공격

3. Fuzz Attack
 - Random CAN Frame 생성으로 Bus Stress 및 예외 상황 유도


## 프로젝트 성과(Key Contribution)

- CAN 공격 재현 자동화 환경 구현

- 공격 Dataset 자동 생성 구조 설계

- 재현 가능한 차량 네트워크 보안 실험 환경 구축
