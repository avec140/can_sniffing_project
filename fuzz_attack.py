import can
import time
import random

bus = can.Bus(channel='vcan0', interface='socketcan')

while True:
    msg = can.Message(
        arbitration_id=random.randint(0, 0x7FF),
        data=[random.randint(0,255) for _ in range(8)],
        is_extended_id=False
    )
    bus.send(msg)
    time.sleep(0.05)