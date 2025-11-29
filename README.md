# ORCA DECK – Advanced RFID-Based Password Manager & Application Launcher

*A cutting-edge, secure hardware solution combining RFID authentication with password management and application launching capabilities.*

<p align="center">
  <a href="https://github.com/Muhib-Mehdi"><img src="https://img.shields.io/badge/GitHub-Muhib--Mehdi-181717?style=for-the-badge&logo=github" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/muhib-mehdi-677bb7391/"><img src="https://img.shields.io/badge/LinkedIn-Muhib--Mehdi-0A66C2?style=for-the-badge&logo=linkedin" alt="LinkedIn" /></a>
</p>

## Tech Stack
<p align="center">
  <img src="https://img.shields.io/badge/ESP32-FFFFFF?style=for-the-badge&logo=espressif&logoColor=E7352C" alt="ESP32" />
  <img src="https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white" alt="Arduino" />
  <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white" alt="C++" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TFT--ILI9341-FF6600?style=for-the-badge&logo=display&logoColor=white" alt="TFT Display" />
  <img src="https://img.shields.io/badge/PN532-4B8BBE?style=for-the-badge&logo=nfc&logoColor=white" alt="PN532 NFC Module" />
</p>

## About ORCA DECK

ORCA DECK is a sophisticated hardware security solution that combines RFID authentication with password management and application launching capabilities. Built around the powerful ESP32 microcontroller, this device offers enterprise-grade security through hardware-level authentication while providing an intuitive touchscreen interface for seamless interaction.

![ORCA DECK System](Pic1.png)

### Key Features
- 🔐 **RFID-Based Authentication** – Hardware-level security using unique RFID cards/tokens
- 🗄️ **Encrypted Password Storage** – Securely store and manage multiple credentials
- 🚀 **Application Launcher** – Launch applications with a single RFID tap
- 🖥️ **Integrated Touchscreen Interface** – 2.4" color TFT display for intuitive navigation
- ⌨️ **Physical Keypad** – 4x4 membrane keypad for manual input and navigation
- 💾 **Flash Storage** – Built-in SPIFFS for fast, reliable data storage
- 🔒 **Auto-Lock** – Automatic locking after periods of inactivity
- 🔄 **Serial Communication** – Robust USB communication with companion desktop app
- 🎨 **Custom Bitmap Graphics** – High-quality icon rendering for enhanced UX

## Hardware Wiring Diagram

The ORCA DECK integrates multiple components with precise pin assignments to ensure optimal performance and reliability.

### TFT Display (ILI9341) Connections
| Device Pin | ESP32 Connection | Notes |
|------------|------------------|-------|
| TFT CS | GPIO 5 | Chip Select |
| TFT DC | GPIO 2 | Data/Command |
| TFT RST | GPIO 4 | Reset |
| TFT MOSI | GPIO 23 | SPI MOSI |
| TFT MISO | GPIO 19 | SPI MISO (may be unused) |
| TFT SCK | GPIO 18 | SPI SCK |
| TFT VCC | 3.3V | DO NOT connect 5V unless display is 5V tolerant |
| TFT GND | GND | Ground connection |

### PN532 NFC Module Connections
| Device Pin | ESP32 Connection | Notes |
|------------|------------------|-------|
| PN532 SDA | GPIO 21 | I²C SDA |
| PN532 SCL | GPIO 22 | I²C SCL |
| PN532 VCC | 3.3V | Some breakouts accept 5V - use 3.3V for consistency |
| PN532 GND | GND | Ground connection |

### 4x4 Keypad Matrix Connections
| Keypad Pin | ESP32 Connection | Notes |
|------------|------------------|-------|
| Row 1 | GPIO 32 | rowPins[0] |
| Row 2 | GPIO 33 | rowPins[1] |
| Row 3 | GPIO 25 | rowPins[2] |
| Row 4 | GPIO 26 | rowPins[3] |
| Col 1 | GPIO 14 | colPins[0] |
| Col 2 | GPIO 12 | colPins[1] |
| Col 3 | GPIO 13 | colPins[2] |
| Col 4 | GPIO 27 | colPins[3] |
| Keypad GND | GND | Ensure common ground with ESP32 |

![ORCA DECK Wiring](Pic2.png)

## System Architecture

The ORCA DECK operates on a dual-component architecture:
1. **Hardware Layer** – ESP32-based embedded system with integrated peripherals
2. **Software Layer** – Companion desktop application for management and control

Communication between components occurs via reliable serial protocols over USB.

![ORCA DECK Architecture](Pic3.png)

## Getting Started

### Prerequisites
- Windows 10/11
- Arduino IDE
- ESP32 development board
- ILI9341 TFT display
- PN532 NFC module
- 4x4 membrane keypad
- RFID cards/tags
- MicroUSB cable

### Hardware Assembly
1. Connect all components according to the wiring diagram above
2. Ensure proper power supply (3.3V for all modules)
3. Verify all ground connections are properly tied together

### Firmware Installation
1. Install ESP32 board support in Arduino IDE:
   - Go to File → Preferences
   - Add `https://dl.espressif.com/dl/package_esp32_index.json` to Additional Board Manager URLs
   - Open Boards Manager (Tools → Board → Boards Manager)
   - Search for and install "ESP32 by Espressif Systems"
2. Install required libraries:
   ```
   Sketch → Include Library → Manage Libraries
   Search and install:
   - Adafruit GFX Library
   - Adafruit ILI9341
   - Keypad
   - Adafruit PN532
   ```
3. Open the sketch file: `sketch_oct16a/sketch_oct16a.ino`
4. Select your ESP32 board: Tools → Board → ESP32 Arduino → [Your Board]
5. Select the appropriate COM port
6. Compile and upload the firmware

### Desktop Application Setup
1. Install Python 3.8+
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python PC\ client/orca_deck_app.py
   ```

## Project Structure
```
ORCA/
├── PC client/
│   ├── orca_deck_app.py       # Main application
│   └── ...                    # Additional modules
├── sketch_oct16a/
│   ├── sketch_oct16a.ino      # ESP32 firmware
│   └── bitmaps.h              # Icon data
├── assets/
│   └── ...                    # Configuration files
├── dist/
│   └── ORCA DECK.exe          # Standalone executable
├── README.md
└── requirements.txt
```

## Security Implementation

### RFID Authentication
- Uses industry-standard MIFARE protocol
- Unique UID verification
- Tamper-resistant hardware validation

### Password Encryption
- AES-256 encryption for stored credentials
- Secure key derivation
- In-memory protection during active sessions

### Communication Security
- Serial data validation
- Command checksum verification
- Session timeout mechanisms

## Customization Options

### Display Themes
Modify color schemes in the firmware:
```cpp
const uint16_t COL_BG        = 0x0000;  // Black background
const uint16_t COL_PANEL     = 0x18E3;  // Panel color
const uint16_t COL_CARD      = 0x2104;  // Card color
const uint16_t COL_ACCENT1   = 0x07FF;  // Accent color 1
const uint16_t COL_ACCENT2   = 0xF81F;  // Accent color 2
const uint16_t COL_ACCENT3   = 0x07E0;  // Accent color 3
```

### Keypad Layout
Adjust key mapping in firmware:
```cpp
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
```

## Troubleshooting

### Common Issues
1. **Display Not Working** – Check TFT_CS, TFT_DC, and TFT_RST connections
2. **NFC Not Responding** – Verify PN532 SDA/SCL wiring and power supply
3. **Keypad Unresponsive** – Confirm row/col pin assignments match code
4. **Serial Communication Errors** – Ensure correct COM port selection

### Diagnostic Commands
Monitor serial output for debugging information:
```bash
# View device logs
Serial.begin(115200);
Serial.println("Debug information");
```

## Contributing

Contributions to enhance the ORCA DECK are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Adafruit for excellent display and NFC libraries
- Arduino community for continuous support
- ESP32 development team for robust hardware platform

---

<p align="center">
  <i>Developed with ❤️ by Muhib Mehdi</i><br/>
  <a href="https://github.com/Muhib-Mehdi">GitHub</a> | 
  <a href="https://www.linkedin.com/in/muhib-mehdi-677bb7391/">LinkedIn</a>
</p>
