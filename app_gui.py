import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import socket
import json
import time

# Configure GUI appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PORT = 5001
BROADCAST_PORT = 37020

class FileTransferApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Offline File Sharing Tool")
        self.geometry("600x500")
        self.resizable(False, False)

        self.selected_file_path = None
        self.discovered_peers = {}

        self.create_widgets()

        # Start UDP Broadcaster in background thread
        threading.Thread(target=self.run_udp_broadcaster, daemon=True).start()
        # Start TCP Receiver in background thread
        threading.Thread(target=self.run_tcp_receiver, daemon=True).start()

    def create_widgets(self):
        # Header Label
        self.header_label = ctk.CTkLabel(self, text="Local File Share", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=15)

        # File Selection Frame
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=20, pady=10)

        self.select_file_btn = ctk.CTkButton(self.file_frame, text="Choose File", command=self.select_file)
        self.select_file_btn.pack(side="left", padx=10, pady=10)

        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True, padx=10)

        # Device Discovery Section
        self.peer_label = ctk.CTkLabel(self, text="Discovered Devices on Local Wi-Fi:", font=ctk.CTkFont(size=14, weight="bold"))
        self.peer_label.pack(pady=(10, 5), padx=20, anchor="w")

        self.scan_btn = ctk.CTkButton(self, text="Scan Nearby Devices", command=self.start_peer_scan)
        self.scan_btn.pack(padx=20, anchor="w")

        self.peer_box = ctk.CTkOptionMenu(self, values=["No devices found"])
        self.peer_box.pack(fill="x", padx=20, pady=10)

        # Progress Section
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=20, pady=20)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Status: Ready")
        self.status_label.pack(pady=5)

        # Send Button
        self.send_btn = ctk.CTkButton(self, text="Send File", fg_color="green", hover_color="darkgreen", command=self.start_file_send)
        self.send_btn.pack(pady=15)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file_path = file_path
            self.file_label.configure(text=os.path.basename(file_path))

    def start_peer_scan(self):
        self.scan_btn.configure(state="disabled", text="Scanning...")
        threading.Thread(target=self.scan_peers_worker, daemon=True).start()

    def scan_peers_worker(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", BROADCAST_PORT))
        sock.settimeout(3)

        self.discovered_peers.clear()
        start_time = time.time()

        while time.time() - start_time < 3:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                info = json.loads(data.decode('utf-8'))
                self.discovered_peers[f"{info.get('device_name')} ({ip})"] = ip
            except socket.timeout:
                break
        sock.close()

        options = list(self.discovered_peers.keys()) if self.discovered_peers else ["No devices found"]
        self.peer_box.configure(values=options)
        self.peer_box.set(options[0])
        self.scan_btn.configure(state="normal", text="Scan Nearby Devices")

    def start_file_send(self):
        if not self.selected_file_path:
            messagebox.showwarning("Warning", "Please select a file to send first.")
            return

        selected_peer_str = self.peer_box.get()
        if selected_peer_str not in self.discovered_peers:
            messagebox.showwarning("Warning", "Please scan and select a valid peer device.")
            return

        target_ip = self.discovered_peers[selected_peer_str]
        threading.Thread(target=self.send_file_worker, args=(self.selected_file_path, target_ip), daemon=True).start()

    def send_file_worker(self, file_path, target_ip):
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((target_ip, PORT))
            
            # Send Metadata
            metadata = {'filename': filename, 'filesize': filesize}
            client_socket.sendall(json.dumps(metadata).encode('utf-8').ljust(1024))

            # Stream Binary Chunks
            sent_bytes = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
                    sent_bytes += len(chunk)
                    
                    # Update Progress Bar in UI
                    progress = sent_bytes / filesize
                    self.progress_bar.set(progress)
                    self.status_label.configure(text=f"Status: Sending... {int(progress * 100)}%")

            self.status_label.configure(text="Status: Transfer Complete!")
            messagebox.showinfo("Success", f"Successfully sent {filename}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")
        finally:
            client_socket.close()

    def run_udp_broadcaster(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        hostname = socket.gethostname()
        payload = json.dumps({"device_name": hostname, "transfer_port": PORT}).encode('utf-8')

        while True:
            try:
                sock.sendto(payload, ("255.255.255.255", BROADCAST_PORT))
                time.sleep(2)
            except Exception:
                pass

    def run_tcp_receiver(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen(5)

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.receive_file_worker, args=(conn,), daemon=True).start()

    def receive_file_worker(self, conn):
        try:
            metadata_bytes = conn.recv(1024)
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            filename = metadata['filename']
            filesize = metadata['filesize']

            save_path = f"received_{filename}"
            received_bytes = 0

            with open(save_path, 'wb') as f:
                while received_bytes < filesize:
                    chunk = conn.recv(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_bytes += len(chunk)
                    
                    progress = received_bytes / filesize
                    self.progress_bar.set(progress)
                    self.status_label.configure(text=f"Status: Receiving {filename}... {int(progress * 100)}%")

            self.status_label.configure(text=f"Status: Received {filename}!")
            messagebox.showinfo("File Received", f"Received file saved as: {save_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    app = FileTransferApp()
    app.mainloop()