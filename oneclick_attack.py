import subprocess
import sys
import signal
from datetime import datetime
from pathlib import Path

ATTACKS = {
    "1": ("Replay Attack", "replay_attack.py"),
    "2": ("Injection Attack", "injection_attack.py"),
    "3": ("Fuzz Attack", "fuzz_attack.py"),
}

LOGGER_SCRIPT = "log_sniffer_logger.py"
LOG_DIR = "logs"


def show_menu():
    print("\n========== CAN Attack Runner ==========")
    for k, (name, script) in ATTACKS.items():
        print(f"{k}. {name} ({script})")
    print("0. Exit")
    print("======================================\n")


def stop_process(p):
    if p is None:
        return
    if p.poll() is None:
        try:
            p.send_signal(signal.SIGINT)
            p.wait(timeout=3)
        except Exception:
            p.terminate()
            try:
                p.wait(timeout=2)
            except Exception:
                p.kill()


def run_attack(choice: str):
    name, attack_script = ATTACKS[choice]
    Path(LOG_DIR).mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    tag = f"{choice}_{name.replace(' ', '_')}_{ts}"
    out_csv = str(Path(LOG_DIR) / f"{tag}.csv")

    print(f"\n[+] Selected: {name}")
    print(f"[+] 1) Start CSV Logger -> {out_csv}")
    print(f"[+]    Marker tag: {tag}")

    # tag를 logger에 전달 (START/END 마커 자동 기록)
    logger_p = subprocess.Popen(
        ["python3", LOGGER_SCRIPT, "--out", out_csv, "--tag", tag],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"[+] 2) Run attack -> {attack_script}")
    print("[+]    Stop ATTACK with Ctrl+C\n")

    try:
        subprocess.run(["python3", attack_script], check=False)
    except KeyboardInterrupt:
        print("\n[!] Attack stopped by user")

    print("[+] 3) Stop Logger")
    stop_process(logger_p)

    print(f"[+] CSV saved: {out_csv}\n")


def main():
    while True:
        show_menu()
        choice = input("Select attack number: ").strip()

        if choice == "0":
            print("Bye.")
            sys.exit(0)

        if choice not in ATTACKS:
            print("Invalid selection")
            continue

        run_attack(choice)


if __name__ == "__main__":
    main()