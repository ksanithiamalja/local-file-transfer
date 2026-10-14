import socket
import json
import time

BROADCAST_PORT = 37020
BROADCAST_IP = "255.255.255.255"  # Special IP to send packets to ALL devices on local Wi-Fi

def start_broadcaster(device_name="Receiver-PC", transfer_port=5001):
    """
    Runs on the RECEIVER side. Continually broadcasts network presence every 2 seconds.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = {
        "device_name": device_name,
        "transfer_port": transfer_port
    }
    payload = json.dumps(message).encode('utf-8')

    print(f"[*] UDP Broadcaster active as '{device_name}' on port {BROADCAST_PORT}...")
    try:
        while True:
            sock.sendto(payload, (BROADCAST_IP, BROADCAST_PORT))
            time.sleep(2)  # Broadcast presence every 2 seconds
    except KeyboardInterrupt:
        print("\n[*] Stopping discovery broadcast.")
    finally:
        sock.close()


def listen_for_peers(timeout=10):
    """
    Runs on the SENDER side. Listens for nearby receiver broadcasts and returns their IP & metadata.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    sock.settimeout(timeout)

    print(f"[*] Scanning local network for nearby receivers (Timeout: {timeout}s)...")
    
    discovered_peers = {}
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                info = json.loads(data.decode('utf-8'))

                if ip not in discovered_peers:
                    discovered_peers[ip] = info
                    print(f"[+] Discovered Peer: {info.get('device_name')} at IP: {ip}")
            except socket.timeout:
                break
    finally:
        sock.close()

    return discovered_peers


if __name__ == "__main__":
    choice = input("Run mode - (1) Broadcast presence or (2) Scan for peers: ").strip()
    if choice == "1":
        name = input("Enter device name (default Receiver-PC): ").strip() or "Receiver-PC"
        start_broadcaster(device_name=name)
    elif choice == "2":
        peers = listen_for_peers(timeout=5)
        print("\nScan complete. Discovered peers:", peers)