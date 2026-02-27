import can
import time
import random

def main():
    try:
        bus = can.Bus(
            channel='vcan0',
            interface='socketcan'
        )

        print("Random CAN Generator Started (ID: 0x100, 100ms interval)")
        print("Press Ctrl+C to stop\n")

        while True:
            msg = can.Message(#can메시지 랜덤 생성 구간
                arbitration_id=0x100,
                data=[random.randint(0, 255) for _ in range(8)],
                is_extended_id=False
            )

            try:#can메시지 송신 및 수신된 메시지 확인 프린트구간
                bus.send(msg)
                print(f"Sent → ID=0x100 DATA={msg.data.hex()}")
            except can.CanError:
                print("Message NOT sent")


            time.sleep(0.1)  # 100ms 주기

    except KeyboardInterrupt:#can메시지 생성 중단 신호 만들기
        print("\nStopped by user")
    finally:
        bus.shutdown()
        print("Bus shutdown complete")

if __name__ == "__main__":
    main()