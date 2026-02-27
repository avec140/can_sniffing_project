import can
import csv
import time
import argparse
from datetime import datetime

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", default="vcan0")
    ap.add_argument("--bustype", default="socketcan")
    ap.add_argument("--out", default=None, help="output csv path")
    ap.add_argument("--tag", default="ATTACK", help="marker tag for start/end")
    args = ap.parse_args()

    file_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = args.out or f"can_log_{file_ts}.csv"

    bus = can.Bus(channel=args.channel, interface=args.bustype)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "can_id", "dlc", "data_hex"])

        # START 마커 기록
        w.writerow([time.time(), f"MARK_START:{args.tag}", 0, ""])
        f.flush()

        try:
            while True:
                msg = bus.recv(timeout=1.0) #can bus데이터 수신만 함.
                if msg is None:
                    continue

                ts = time.time()
                can_id = hex(msg.arbitration_id).lower()
                dlc = msg.dlc
                data_hex = msg.data.hex().upper()

                w.writerow([ts, can_id, dlc, data_hex])
                f.flush()

        except KeyboardInterrupt:
            pass
        finally:
            # END 마커 기록
            w.writerow([time.time(), f"MARK_END:{args.tag}", 0, ""])
            f.flush()

    bus.shutdown()

if __name__ == "__main__":
    main()