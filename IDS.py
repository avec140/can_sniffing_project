import can
import time
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

CHANNEL = "vcan0"
BUSTYPE = "socketcan"

BASELINE_FILE = "baseline.json"
NORMAL_LOG = "can_log_normal.csv"

# 탐지 민감도 (값 ↑ = 덜 민감)
Z_DT = 4.0
Z_BYTE = 6.0

# 알람 스팸 방지(초)
COOLDOWN_PERIOD = 1.0
COOLDOWN_PAYLOAD = 0.5

# baseline 학습 최소 샘플 수
MIN_SAMPLES = 30


def hex_to_8bytes(h: str) -> np.ndarray:
    """data_hex -> (8,) uint8"""
    b = bytes.fromhex(str(h).strip())
    if len(b) < 8:
        b += bytes([0] * (8 - len(b)))
    return np.frombuffer(b[:8], dtype=np.uint8)


def train_baseline_from_csv(csv_path: str) -> dict:
    print(f"[+] Training baseline from CSV: {csv_path}")

    df = pd.read_csv(csv_path)
    df["can_id"] = df["can_id"].astype(str).str.lower()

    baseline = {}

    for cid, g in df.groupby("can_id"):
        g = g.sort_values("timestamp")
        if len(g) < MIN_SAMPLES:
            continue

        ts = g["timestamp"].values
        dt = np.diff(ts)
        if len(dt) < 5:
            continue

        mean_dt = float(np.mean(dt))
        std_dt = float(np.std(dt) + 1e-6)

        X = np.stack(g["data_hex"].apply(hex_to_8bytes).values)  # (N,8)

        baseline[cid] = {
            "dt_mean": mean_dt,
            "dt_std": std_dt,
            "byte_mean": X.mean(axis=0).tolist(),
            "byte_std": (X.std(axis=0) + 1e-6).tolist(),
            "count": int(len(g)),
        }

    print(f"[+] Baseline trained. IDs={len(baseline)}")
    return baseline


def load_or_build_baseline() -> dict:
    if Path(BASELINE_FILE).exists():
        print(f"[+] Loading baseline: {BASELINE_FILE}")
        with open(BASELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # baseline.json 없으면 CSV로 학습
    if not Path(NORMAL_LOG).exists():
        raise FileNotFoundError(
            f"baseline.json도 없고 {NORMAL_LOG}도 없어서 baseline을 만들 수 없습니다."
        )

    baseline = train_baseline_from_csv(NORMAL_LOG)

    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)

    print(f"[+] Saved baseline: {BASELINE_FILE}")
    return baseline


def main():
    baseline = load_or_build_baseline()

    bus = can.interface.Bus(channel=CHANNEL, bustype=BUSTYPE)

    last_seen = {}  # can_id -> last timestamp
    last_alert = defaultdict(float)  # (can_id, type) -> last alert time

    print("\n[+] Realtime Statistical IDS Running on vcan0")
    print("[+] Ctrl+C to stop\n")

    try:
        for msg in bus:
            now = time.time()
            cid = hex(msg.arbitration_id).lower()

            if cid not in baseline:
                continue

            b = baseline[cid]
            if b.get("count", MIN_SAMPLES) < MIN_SAMPLES:
                continue

            # -----------------------------
            # 1) Period anomaly (Replay)
            # -----------------------------
            if cid in last_seen and b.get("dt_mean") is not None:
                dt = now - last_seen[cid]
                z = abs(dt - float(b["dt_mean"])) / float(b["dt_std"])

                if z > Z_DT and (now - last_alert[(cid, "dt")]) > COOLDOWN_PERIOD:
                    print(
                        f"[ALERT][PERIOD] ID={cid} dt={dt:.4f}s "
                        f"(mean={float(b['dt_mean']):.4f}, z={z:.2f})"
                    )
                    last_alert[(cid, "dt")] = now

            last_seen[cid] = now

            # -----------------------------
            # 2) Payload anomaly (Injection/Fuzz)
            # -----------------------------
            data = bytes(msg.data)
            if len(data) < 8:
                data += bytes([0] * (8 - len(data)))

            x = np.frombuffer(data[:8], dtype=np.uint8)

            mu = np.array(b["byte_mean"], dtype=np.float64)
            sd = np.array(b["byte_std"], dtype=np.float64)

            zvec = np.abs(x - mu) / sd
            max_z = float(np.max(zvec))
            idx = int(np.argmax(zvec))

            if max_z > Z_BYTE and (now - last_alert[(cid, "byte")]) > COOLDOWN_PAYLOAD:
                print(
                    f"[ALERT][PAYLOAD] ID={cid} max_z={max_z:.2f} "
                    f"byte[{idx}]={int(x[idx])} (mean≈{mu[idx]:.1f})"
                )
                last_alert[(cid, "byte")] = now

    except KeyboardInterrupt:
        print("\n[!] IDS stopped.")

    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()