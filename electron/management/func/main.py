import os
import shutil
import sys
import time
import subprocess

# Konfiguration
TOR_DIR = r"C:\tor\tor"
TOR_EXE = os.path.join(TOR_DIR, "tor.exe")
TEMPLATE_TOR_DIR = os.path.join(os.path.dirname(__file__), "tor")
HIDDEN_SERVICE_DIR = r"C:\tor\hidden_service"
TORRC_PATH = os.path.join(TOR_DIR, "torrc")
HOSTNAME_FILE = os.path.join(HIDDEN_SERVICE_DIR, "hostname")
ONION_OUT = os.path.join(os.path.dirname(__file__), "onion_domain.txt")
LOCAL_PORT = 8080

def purple(text): return f"\033[95m{text}\033[0m"
def red(text): return f"\033[91m{text}\033[0m"
def green(text): return f"\033[92m{text}\033[0m"

def create_hidden_service_dir():
    if not os.path.exists(HIDDEN_SERVICE_DIR):
        print(purple(f"[*] Erstelle Hidden Service Verzeichnis: {HIDDEN_SERVICE_DIR}"))
        os.makedirs(HIDDEN_SERVICE_DIR)

def create_torrc():
    if not os.path.exists(TORRC_PATH):
        print(purple(f"[*] Erstelle torrc: {TORRC_PATH}"))
        config = f"""SocksPort 9050
HiddenServiceDir {HIDDEN_SERVICE_DIR}
HiddenServicePort 80 127.0.0.1:{LOCAL_PORT}
"""
        with open(TORRC_PATH, 'w') as f:
            f.write(config)

def start_tor():
    print(purple("[*] Starte Tor..."))
    return subprocess.Popen(
        [TOR_EXE, "-f", TORRC_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def wait_for_onion(timeout=60):
    print(purple("[*] Warte auf .onion-Generierung..."))
    elapsed = 0
    while elapsed < timeout:
        if os.path.exists(HOSTNAME_FILE):
            with open(HOSTNAME_FILE, 'r') as f:
                onion = f.read().strip()
                print(green(f"[+] .onion-Domain: {onion}"))
                with open(ONION_OUT, 'w') as out:
                    out.write(onion + '\n')
                print(green(f"[+] Gespeichert in: {ONION_OUT}"))
                return True
        time.sleep(2)
        elapsed += 2
    raise TimeoutError(red("[-] Timeout: .onion-Domain nicht generiert."))

def stop_tor(proc):
    print(purple("[!] Beende Tor..."))
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

if __name__ == "__main__":
    if not os.path.exists(TOR_EXE):
        print(red("[-] Tor nicht gefunden unter C:\\tor\\tor, versuche zu kopieren..."))
        shutil.copytree(TEMPLATE_TOR_DIR, TOR_DIR)
        if not os.path.exists(TOR_EXE):
            print(red("[-] Tor konnte nicht gefunden oder kopiert werden."))
            exit(1)

    create_hidden_service_dir()
    create_torrc()

    if os.path.exists(ONION_OUT):
        print(green("[*] onion_domain.txt existiert bereits. nichts zu tun."))

    tor_proc = start_tor()
    try:
        wait_for_onion()
        while True:
            time.sleep(1)
    finally:
        stop_tor(tor_proc)
