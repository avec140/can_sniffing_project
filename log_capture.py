import can
import csv
import time
from datetime import datetime

CHANNEL = "vcan0"
BUSTYPE = "socketcan"

# CSV 파일 이름 생성
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
csv_file = f"can_log_{timestamp}.csv"

bus = can.Bus(channel=CHANNEL, interface=BUSTYPE)

print(f"[+] Logging CAN data to {csv_file}")
print("[+] Press Ctrl+C to stop")

with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)

    # CSV Header
    writer.writerow([
        "timestamp",
        "can_id",
        "dlc",
        "data_hex"
    ])

    try:
        while True:
            msg = bus.recv()

            if msg:
                ts = time.time()
                can_id = hex(msg.arbitration_id)
                dlc = msg.dlc
                data_hex = msg.data.hex()

                writer.writerow([
                    ts,
                    can_id,
                    dlc,
                    data_hex
                ])

                file.flush()

    except KeyboardInterrupt:
        print("\n[!] Logging stopped")

bus.shutdown()