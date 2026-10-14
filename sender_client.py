import socket
import os
import json
import time
from discovery import listen_for_peers

PORT = 5001

def send_file(file_path, target_ip):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(f"[*] Connecting to receiver at {target_ip}:{PORT}...")
    try:
        client_socket.connect((target_ip, PORT))
        print("[+] Connected successfully!\n")

        # Metadata Header
        metadata = {'filename': filename, 'filesize': filesize}
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        client_socket.sendall(metadata_bytes.ljust(1024))

        # Stream binary chunks
        sent_bytes = 0
        start_time = time.time()

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(64 * 1024)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                sent_bytes += len(chunk)

                progress = (sent_bytes / filesize) * 100
                print(f"Progress: {progress:.2f}% ({sent_bytes}/{filesize} bytes)", end='\r')

        elapsed = time.time() - start_time
        speed_mbps = (filesize / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        print(f"\n\n[+] File sent in {elapsed:.2f}s ({speed_mbps:.2f} MB/s)")

    finally:
        client_socket.close()

if __name__ == "__main__":
    FILE_TO_SEND = "sample_input.txt"

    if not os.path.exists(FILE_TO_SEND):
        with open(FILE_TO_SEND, "w") as f:
            f.write("Hello Network World! " * 200000)

    # Step 1: Auto-discover peers
    peers = listen_for_peers(timeout=5)

    if not peers:
        print("[-] No receivers found on network automatically.")
        TARGET_IP = input("Enter receiver IP address manually (default 127.0.0.1): ").strip() or "127.0.0.1"
    else:
        peer_ips = list(peers.keys())
        print("\nSelect a discovered peer:")
        for idx, ip in enumerate(peer_ips):
            print(f"[{idx}] {peers[ip]['device_name']} ({ip})")
        
        selection = int(input("Enter peer index number: ").strip() or 0)
        TARGET_IP = peer_ips[selection]

    # Step 2: Send file
    send_file(FILE_TO_SEND, TARGET_IP)