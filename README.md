# ORCA DECK – My Proud Achievement

*An advanced, secure RFID‑based password manager and application launcher I built from scratch.*

<p align="center">
  <a href="https://github.com/Muhib-Mehdi"><img src="https://img.shields.io/badge/GitHub-Muhib--Mehdi-181717?style=for-the-badge&logo=github" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/muhib-mehdi-677bb7391/"><img src="https://img.shields.io/badge/LinkedIn-Muhib--Mehdi-0A66C2?style=for-the-badge&logo=linkedin" alt="LinkedIn" /></a>
</p>

## Tech Stack
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white" alt="Arduino" />
  <img src="https://img.shields.io/badge/CustomTkinter-2C2C2C?style=for-the-badge&logo=python&logoColor=white" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Serial-FF6600?style=for-the-badge&logo=usb&logoColor=white" alt="Serial Communication" />
</p>

## About ORCA DECK

ORCA DECK is my personal security solution that blends hardware and software to deliver a reliable, RFID‑based password manager and application launcher. It showcases my skills in embedded systems programming and desktop application development.

### Key Features
- 🔐 **Secure Password Management** – Encrypted storage for all your credentials.
- 🚀 **Application Launcher** – Open any program with a single RFID tap.
- 🛡️ **RFID Authentication** – Hardware‑level security using unique RFID cards.
- ⚡ **SPIFFS Efficiency** – Fast flash storage without the overhead of SD cards.
- 🔒 **Auto‑Lock** – Automatic lock after inactivity to protect your data.
- 🎨 **Modern UI** – Clean, intuitive interface built with CustomTkinter.
- 📱 **Cross‑Platform** – Runs smoothly on Windows with serial communication support.

## Architecture Overview

The system consists of two main components:
1. **Hardware** – An Arduino‑based RFID reader with integrated flash storage.
2. **Software** – A Python desktop application that manages passwords and launches apps.

Communication between the two is handled via reliable serial protocols.

## Getting Started
### Prerequisites
- Windows 10/11
- Python 3.8+
- Arduino IDE
- RFID RC522 module
- Compatible RFID cards

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Muhib-Mehdi/orca-deck.git
   ```
2. Upload the Arduino firmware to your board.
3. Configure the COM port in `assets/config.json`.
4. Run the application using the executable:
   - Navigate to the `dist` folder.
   - Double-click `ORCA DECK.exe`.

   *Note: No Python installation is required to run the executable.*

## Project Structure
```
20ORCA DECK/
├── dist/
│   └── ORCA DECK.exe          # Standalone executable
├── PC client/
│   ├── orca_deck_app.py       # Main application
│   ├── serial_handler.py      # Serial communication
│   ├── encryption_manager.py  # Encryption handling
│   ├── security_manager.py    # Security questions
│   ├── password_manager.py    # Password UI
│   ├── app_launcher.py        # App launcher UI
│   └── settings_panel.py      # Settings UI
├── assets/
│   ├── authorized_uids.json   # Authorized RFID cards
│   ├── passwords.json         # Encrypted passwords
│   ├── security_data.json     # Security questions
│   ├── apps.json              # App configurations
│   ├── mappings.json          # Key mappings
│   └── config.json            # COM port settings
├── sketch_oct16a/
│   ├── sketch_oct16a.ino      # Arduino firmware
│   └── bitmaps.h              # Icon data
├── README.md
└── requirements.txt
```

### Initial Setup
On first launch, you'll complete a 2-step setup process:
1. **Step 1:** Answer 3 security questions (backup recovery method)
2. **Step 2:** Scan your RFID card to register it as your master key

After setup, simply scan your RFID card to unlock the system.

## Security Features
- **Encrypted Password Storage** – Industry‑standard cryptography.
- **RFID‑Based Access Control** – Only authorized cards can unlock the system.
- **Security Questions** – Backup authentication method.
- **Auto‑Lock** – Locks after a period of inactivity.
- **Master Key Protection** – Secure key management.

## Contributing
I welcome contributions! Feel free to open a Pull Request.

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- CustomTkinter for the beautiful UI components
- PySerial for reliable serial communication
- The open‑source community for countless Python libraries

---
<p align="center">
  <i>Developed with ❤️ by Muhib Mehdi</i><br/>
  <a href="https://github.com/Muhib-Mehdi">GitHub</a> | 
  <a href="https://www.linkedin.com/in/muhib-mehdi-677bb7391/">LinkedIn</a>
</p>
