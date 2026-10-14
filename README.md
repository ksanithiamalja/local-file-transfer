
# 🚀 Offline Local File Transfer Tool

A lightweight, high-speed, and peer-to-peer (P2P) file-sharing desktop application built from scratch in **Python**. It allows users to discover devices on the same local Wi-Fi network automatically and transfer files directly without an internet connection or cloud storage.

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

---

## ✨ Features

- **📶 100% Offline Connectivity**: Works strictly over local network interfaces (Wi-Fi router or Mobile Hotspot). No internet required.
- **⚡ High-Speed Binary Chunking**: Reads and writes files in 64 KB binary chunks to maximize transfer speeds while maintaining minimal RAM usage.
- **🔍 Automatic Peer Discovery**: Uses **UDP Multicast Broadcasting** on port `37020` so nearby devices can auto-detect each other without typing IP addresses manually.
- **🔒 Direct TCP Transfer**: Establishes point-to-point **TCP Sockets** (Port `5001`) for reliable metadata header exchange and data streaming.
- **🎨 Modern GUI Interface**: Styled with **CustomTkinter**, featuring real-time progress bars, dark mode, device scanning, and file pickers.

---

## 📐 System Architecture


```

[ SENDER DEVICE ]                                     [ RECEIVER DEVICE ]
┌───────────────────────────┐                         ┌───────────────────────────┐
│ 1. UDP Scan (37020)       │ ── UDP Peer Discovery ─>│ 1. UDP Broadcaster        │
│                           │ <── Receives IP & Host ──│    (Announces presence)  │
│                           │                         │                           │
│ 2. Selects Target Device  │                         │                           │
│                           │                         │                           │
│ 3. Establishes TCP Socket │ ── TCP Handshake (5001)─>│ 2. TCP Server Listener    │
│    Sends 1KB JSON Metadata│                         │    Parses Filename & Size │
│    Streams 64KB Chunks   │ ── Binary Data Stream ──>│ 3. Direct Disk Writer     │
└───────────────────────────┘                         └───────────────────────────┘

```

---

## 📁 Repository Structure

```text
local-file-transfer/
│
├── file_chunker.py     # Module 1: Binary chunk read/write streaming engine
├── receiver_server.py  # Module 2: Low-level TCP socket server listener
├── sender_client.py    # Module 2: Low-level TCP socket client sender
├── discovery.py        # Module 3: UDP multicast broadcaster & scanner
├── app_gui.py          # Module 4: Integrated CustomTkinter desktop GUI
├── .gitignore          # Excludes temporary test files and pyinstaller builds
└── README.md           # Project documentation

```

---

## 🛠️ Installation & Setup

### Prerequisites

* Python **3.11+** installed on your system.
* Git installed.

### Installation Steps

1. **Clone the Repository**
```bash
git clone [https://github.com/ksanithiamalja/local-file-transfer.git](https://github.com/ksanithiamalja/local-file-transfer.git)
cd local-file-transfer

```


2. **Install Required Packages**
```bash
pip install customtkinter

```



---

## 🚀 How to Run

### Method 1: Launch Graphical Interface (Recommended)

Launch the desktop user interface:

```bash
python app_gui.py

```

1. Click **Choose File** to pick the file you want to send.
2. Click **Scan Nearby Devices** to locate active receivers on your network.
3. Select the target receiver from the drop-down menu and click **Send File**.

### Method 2: Command Line (CLI Testing)

You can also run the modules individually via terminal:

1. **Start Receiver Node:**
```bash
python receiver_server.py

```


2. **Start Sender Node:**
```bash
python sender_client.py

```



---

## 📦 Compiling to Standalone `.exe` (Windows)

To bundle the application into a standalone Windows executable without requiring Python:

1. Install PyInstaller:
```cmd
pip install pyinstaller

```


2. Compile with CustomTkinter asset bundling:
```cmd
pyinstaller --noconfirm --onedir --windowed --add-data "%LOCALAPPDATA%\Programs\Python\Python313\Lib\site-packages\customtkinter;customtkinter/" app_gui.py

```


3. Your compiled app will be located at `dist/app_gui/app_gui.exe`.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

```

---

### Push Updated README to GitHub

Run these commands in your Command Prompt (`C:\Users\HP\local-file-transfer>`):

```cmd
git add README.md
git commit -m "docs: add comprehensive README.md with architecture diagram"
git push origin main

```
