

#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <Keypad.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <SPI.h>
#include "SPIFFS.h"
#include "bitmaps.h"

#define TFT_CS   5
#define TFT_DC   2
#define TFT_RST  4
Adafruit_ILI9341 tft(TFT_CS, TFT_DC, TFT_RST);

#define PN532_SDA 21
#define PN532_SCL 22
Adafruit_PN532 nfc(PN532_SDA, PN532_SCL);

const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[ROWS] = {32, 33, 25, 26};
byte colPins[COLS] = {14, 12, 13, 27};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

enum MenuState { MAIN_MENU, STEAMDECK, RFID_UNLOCK, PASSWORD_MANAGER, RFID_VERIFY };
MenuState menuState = MAIN_MENU;

const uint16_t* icons[4][4] = {
  {myBitmapsteam, myBitmapsettings, myBitmapwhatsapp, myBitmapinstagram},
  {myBitmapdiscord, myBitmapvalorant, myBitmapfolder, myBitmapvscode},
  {myBitmapyoutube, myBitmapwall_clock, myBitmapterminal, myBitmapobs},
  {myBitmapbrave, myBitmapgithub, myBitmapcalculator, myBitmapback}
};

const char* iconLabels[4][4] = {
  {"Steam", "Settings", "WhatsApp", "Instagram"},
  {"Discord", "Valorant", "Files", "VS Code"},
  {"YouTube", "Clock", "Terminal", "OBS"},
  {"Brave", "GitHub", "Calc", "Back"}
};

const uint16_t* passIcons[4][4] = {
  { myBitmapsteam,     myBitmapdiscord,   myBitmapvalorant,  myBitmapyoutube },
  { myBitmapgithub,    myBitmapinfinite,  myBitmapmuhib24,   myBitmapbrave  },
  { myBitmapinstagram, myBitmaplinkedin,  myBitmapothers,    myBitmapothers           },
  { myBitmapothers, myBitmapothers, myBitmapothers, myBitmapback   }
};

const char* passLabels[4][4] = {
  {"Steam", "Discord", "Valorant", "YouTube"},
  {"GitHub", "Infinite", "Muhib24", "Brave"},
  {"Instagram", "LinkedIn", "Other", "Item 12"},
  {"Item 13", "Item 14", "Item 15", "Back"}
};

String dynamicAppLabels[4][4];
String dynamicPassLabels[4][4];
bool labelsInitialized = false;

const uint16_t COL_BG        = 0x0000;
const uint16_t COL_PANEL     = 0x18E3;
const uint16_t COL_CARD      = 0x2104;
const uint16_t COL_ACCENT1   = 0x07FF;
const uint16_t COL_ACCENT2   = 0xF81F;
const uint16_t COL_ACCENT3   = 0x07E0;
const uint16_t COL_BUTTON_BG = 0x2945;
const uint16_t COL_TEXT      = 0xFFFF;
const uint16_t COL_MUTED     = 0x8410;
const uint16_t COL_HIGHLIGHT = 0xFFE0;

void drawBitmap32x32Color(int x, int y, const uint16_t *bitmap) {
  const uint16_t fillers[] = {
    0xFF1C, 0xFF3C, 0xFF5D, 0xFF7D, 0xFF9E, 0xFFBE, 0xFFDF,
    0xF7BE, 0xEF5D, 0xDEDB, 0xD6BA
  };
  for (int j = 0; j < 32; j++) {
    for (int i = 0; i < 32; i++) {
      uint16_t color = pgm_read_word(&bitmap[j*32 + i]);
      bool isF = false;
      for (uint8_t k = 0; k < sizeof(fillers)/sizeof(fillers[0]); k++) {
        if (color == fillers[k]) { isF = true; break; }
      }
      if (!isF) tft.drawPixel(x + i, y + j, color);
    }
  }
}

String asciiEllipsize(const char* s, int maxChars) {
  String out = String(s);
  if ((int)out.length() <= maxChars) return out;
  if (maxChars <= 3) return out.substring(0, maxChars);
  return out.substring(0, maxChars - 2) + "..";
}


void drawCenteredTextGuarded(const char* text, int centerX, int y, uint8_t textSize, uint16_t color, int maxWidthPx) {
  if (!text) return;
  tft.setTextSize(textSize);
  tft.setTextColor(color);
  String s = String(text);

  int16_t x1, y1;
  uint16_t w, h;
  tft.getTextBounds(s.c_str(), 0, y, &x1, &y1, &w, &h);
  
  if (maxWidthPx > 0 && w > (uint16_t)maxWidthPx) {
    int charWidth = 5 * textSize;
    int allowed = (maxWidthPx / charWidth) - 1;
    if (allowed < 3) allowed = 3;
    s = asciiEllipsize(text, allowed);
    tft.getTextBounds(s.c_str(), 0, y, &x1, &y1, &w, &h);
  }
  
  int x = centerX - (w / 2);
  if (x < 0) x = 0;
  tft.setCursor(x, y);
  tft.print(s);
}

void drawRoundedButton(int x, int y, int w, int h, uint16_t bg, uint16_t borderColor, const char* label) {
  tft.fillRoundRect(x, y, w, h, 8, bg);
  tft.drawRoundRect(x, y, w, h, 8, borderColor);
  drawCenteredTextGuarded(label, x + w/2, y + (h/2) - 8, 2, COL_TEXT, w - 16);
}

void drawMainMenu();
void drawSteamdeckGrid();
void drawPasswordManagerGrid();
void drawRFIDScreen(const char* msg);
void checkRFID();
void handleKey(char key);
void handleSerialIconUpload();

void initializeLabels() {
  if (labelsInitialized) return;
  
  for (int r = 0; r < 4; r++) {
    for (int c = 0; c < 4; c++) {
      dynamicAppLabels[r][c] = String(iconLabels[r][c]);
      dynamicPassLabels[r][c] = String(passLabels[r][c]);
    }
  }
  labelsInitialized = true;
}

void setup() {
  Serial.begin(115200);
  
  if(!SPIFFS.begin(true)){
    Serial.println("SPIFFS Mount Failed");
  } else {
    Serial.println("SPIFFS Mounted");
    File root = SPIFFS.open("/");
    File file = root.openNextFile();
    while(file){
      Serial.print("FILE: ");
      Serial.println(file.name());
      file = root.openNextFile();
    }
  }
  
  initializeLabels();
  
  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(COL_BG);

  // Initialize NFC with error checking
  tft.fillRect(0, 0, tft.width(), 50, COL_PANEL);
  drawCenteredTextGuarded("Initializing NFC...", tft.width()/2, 20, 1, COL_TEXT, tft.width()-20);
  
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("ERROR: NFC module not found!");
    drawCenteredTextGuarded("NFC Error!", tft.width()/2, 60, 2, ILI9341_RED, tft.width()-20);
    drawCenteredTextGuarded("Check connections", tft.width()/2, 90, 1, COL_MUTED, tft.width()-20);
    delay(3000);
  } else {
    Serial.print("Found PN53x chip, version: ");
    Serial.println((versiondata >> 24) & 0xFF, HEX);
    drawCenteredTextGuarded("NFC Ready!", tft.width()/2, 60, 2, COL_ACCENT3, tft.width()-20);
    delay(1000);
  }
  
  nfc.SAMConfig();

  drawMainMenu();
}

void loop() {
  handleSerialIconUpload();
  
  char key = keypad.getKey();
  if (key) handleKey(key);

  if (menuState == RFID_UNLOCK || menuState == RFID_VERIFY) checkRFID();
  yield();
}

File uploadFile;
int uploadRemaining = 0;
String uploadKey = "";

void handleSerialIconUpload() {
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.startsWith("ICON_START:")) {
      int firstColon = line.indexOf(':');
      int secondColon = line.indexOf(':', firstColon + 1);
      int thirdColon = line.indexOf(':', secondColon + 1);
      
      String iconType = line.substring(firstColon + 1, secondColon);
      uploadKey = line.substring(secondColon + 1, thirdColon);
      uploadRemaining = line.substring(thirdColon + 1).toInt();
      
      String filename = "/" + iconType + "_" + uploadKey + ".raw";
      Serial.print("Opening for write: "); Serial.println(filename);
      
      if (SPIFFS.exists(filename)) SPIFFS.remove(filename);
      
      uploadFile = SPIFFS.open(filename, "w");
      if (uploadFile) {
         Serial.println("UPLOAD_START_OK");
      } else {
         Serial.println("UPLOAD_START_FAIL");
      }
    }
    else if (line.startsWith("ICON_DATA:")) {
      if (uploadFile) {
        String hexData = line.substring(10);
        for (int i = 0; i < hexData.length(); i += 2) {
           char byteStr[3];
           byteStr[0] = hexData[i];
           byteStr[1] = hexData[i+1];
           byteStr[2] = '\0';
           uint8_t b = (uint8_t) strtol(byteStr, NULL, 16);
           uploadFile.write(b);
           uploadRemaining--;
           if (i % 32 == 0) yield();
        }
      }
    }
    else if (line == "ICON_END") {
      if (uploadFile) {
        uploadFile.close();
        Serial.println("UPLOAD_DONE");
        if (menuState == STEAMDECK) drawSteamdeckGrid();
        else if (menuState == PASSWORD_MANAGER) drawPasswordManagerGrid();
      }
    }
    else if (line.startsWith("LABEL_APP:")) {
      int firstColon = line.indexOf(':');
      int secondColon = line.indexOf(':', firstColon + 1);
      
      String key = line.substring(firstColon + 1, secondColon);
      String name = line.substring(secondColon + 1);
      
      char keyMap[4][4] = {
        {'A','B','C','D'},
        {'3','6','9','#'},
        {'2','5','8','0'},
        {'1','4','7','*'}
      };
      
      for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
          if (String(keyMap[r][c]) == key) {
            dynamicAppLabels[r][c] = name;
            Serial.println("LABEL_APP_OK");
            if (menuState == STEAMDECK) drawSteamdeckGrid();
            return;
          }
        }
      }
    }
    else if (line.startsWith("LABEL_PASS:")) {
      int firstColon = line.indexOf(':');
      int secondColon = line.indexOf(':', firstColon + 1);
      
      String key = line.substring(firstColon + 1, secondColon);
      String name = line.substring(secondColon + 1);
      
      char keyMap[4][4] = {
        {'A','B','C','D'},
        {'3','6','9','#'},
        {'2','5','8','0'},
        {'1','4','7','*'}
      };
      
      for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
          if (String(keyMap[r][c]) == key) {
            dynamicPassLabels[r][c] = name;
            Serial.println("LABEL_PASS_OK");
            if (menuState == PASSWORD_MANAGER) drawPasswordManagerGrid();
            return;
          }
        }
      }
    }
  }
}

void drawMainMenu() {
  tft.fillScreen(COL_BG);
  tft.fillRect(0, 0, tft.width(), 50, COL_PANEL);
  drawCenteredTextGuarded("O.R.C.A DECK", tft.width()/2, 10, 2, COL_ACCENT1, tft.width()-20);
  drawCenteredTextGuarded("Secure Launcher", tft.width()/2, 32, 1, COL_MUTED, tft.width()-20);

  int m = 18;
  int btnW = (tft.width() - 3*m) / 2;
  int btnH = 60;
  int x0 = m;
  int x1 = 2*m + btnW;
  int y0 = 65;
  int y1 = y0 + btnH + m;

  drawRoundedButton(x0, y0, btnW, btnH, COL_BUTTON_BG, COL_ACCENT1, "Apps");
  drawRoundedButton(x1, y0, btnW, btnH, COL_BUTTON_BG, COL_ACCENT2, "Passwords");
  drawRoundedButton(x0, y1, tft.width() - 2*m, btnH, COL_BUTTON_BG, COL_ACCENT3, "RFID Unlock");
}

void drawBitmapFromSPIFFS(int x, int y, const char* filename) {
  if (!SPIFFS.exists(filename)) return;
  
  File f = SPIFFS.open(filename, "r");
  if (!f) return;

  uint8_t buf[64];
  for (int j = 0; j < 32; j++) {
    if (f.read(buf, 64) != 64) break;
    
    for (int i = 0; i < 32; i++) {
      uint16_t color = (buf[i*2] << 8) | buf[i*2+1];
      tft.drawPixel(x + i, y + j, color);
    }
  }
  f.close();
}

void drawSteamdeckGrid() {
  tft.fillScreen(COL_BG);
  tft.fillRect(0, 0, tft.width(), 35, COL_PANEL);
  drawCenteredTextGuarded("Applications", tft.width()/2, 10, 2, COL_TEXT, tft.width()-20);

  const int iconSize = 32;
  const int pad = 5;
  int totalW = 4*iconSize + 3*pad;
  int xStart = (tft.width() - totalW) / 2;
  int yStart = 45;

  char keyMap[4][4] = {
    {'A','B','C','D'},
    {'3','6','9','#'},
    {'2','5','8','0'},
    {'1','4','7','*'}
  };

  for (int r = 0; r < 4; ++r) {
    for (int c = 0; c < 4; ++c) {
      int x = xStart + c * (iconSize + pad);
      int y = yStart + r * (iconSize + 22);
      
      
      String keyStr = String(keyMap[r][c]);
      String filename = "/app_" + keyStr + ".raw";
      
      if (SPIFFS.exists(filename)) {
        drawBitmapFromSPIFFS(x, y, filename.c_str());
      } else if (icons[r][c]) {
        drawBitmap32x32Color(x, y, icons[r][c]);
      }

      drawCenteredTextGuarded(dynamicAppLabels[r][c].c_str(), x + iconSize/2, y + iconSize + 3, 1, COL_TEXT, iconSize);
    }
  }
}

void drawPasswordManagerGrid() {
  tft.fillScreen(COL_BG);
  tft.fillRect(0, 0, tft.width(), 42, COL_PANEL);
  drawCenteredTextGuarded("Password Manager", tft.width()/2, 8, 2, COL_ACCENT1, tft.width()-20);
  drawCenteredTextGuarded("Select, then scan card", tft.width()/2, 26, 1, COL_MUTED, tft.width()-30);

  const int iconSize = 32;
  const int padX = 10, padY = 16;
  int totalW = 4*iconSize + 3*padX;
  int xStart = (tft.width() - totalW) / 2;
  int yStart = 52;

  char keyMap[4][4] = {
    {'A','B','C','D'},
    {'3','6','9','#'},
    {'2','5','8','0'},
    {'1','4','7','*'}
  };

  for (int r = 0; r < 4; ++r) {
    for (int c = 0; c < 4; ++c) {
      int x = xStart + c * (iconSize + padX);
      int y = yStart + r * (iconSize + padY);
      
      
      String keyStr = String(keyMap[r][c]);
      String filename = "/pass_" + keyStr + ".raw";
      
      if (SPIFFS.exists(filename)) {
        drawBitmapFromSPIFFS(x, y, filename.c_str());
      } else if (passIcons[r][c]) {
        drawBitmap32x32Color(x, y, passIcons[r][c]);
      }
      
      drawCenteredTextGuarded(dynamicPassLabels[r][c].c_str(), x + iconSize/2, y + iconSize + 3, 1, COL_TEXT, iconSize);
    }
  }
}

void flashIconGrid4x4(int r, int c) {
  const int iconSize = 32;
  const int pad = 5;
  int totalW = 4*iconSize + 3*pad;
  int xStart = (tft.width() - totalW) / 2;
  int yStart = 45;
  int x = xStart + c * (iconSize + pad);
  int y = yStart + r * (iconSize + 22);

  tft.drawRect(x-1, y-1, iconSize+2, iconSize+2, COL_HIGHLIGHT);
  delay(120);
  tft.drawRect(x-1, y-1, iconSize+2, iconSize+2, COL_BG);
  
  char keyMap[4][4] = {
    {'A','B','C','D'},
    {'3','6','9','#'},
    {'2','5','8','0'},
    {'1','4','7','*'}
  };
  String keyStr = String(keyMap[r][c]);
  String filename = "/app_" + keyStr + ".raw";
  
  if (SPIFFS.exists(filename)) {
    drawBitmapFromSPIFFS(x, y, filename.c_str());
  } else if (icons[r][c]) {
    drawBitmap32x32Color(x, y, icons[r][c]);
  }
  
  drawCenteredTextGuarded(dynamicAppLabels[r][c].c_str(), x + iconSize/2, y + iconSize + 3, 1, COL_TEXT, iconSize);
}

void flashIconPassGrid(int r, int c) {
  const int iconSize = 32;
  const int padX = 10, padY = 16;
  int totalW = 4*iconSize + 3*padX;
  int xStart = (tft.width() - totalW) / 2;
  int yStart = 52;
  int x = xStart + c * (iconSize + padX);
  int y = yStart + r * (iconSize + padY);

  tft.drawRect(x-1, y-1, iconSize+2, iconSize+2, COL_HIGHLIGHT);
  delay(120);
  tft.drawRect(x-1, y-1, iconSize+2, iconSize+2, COL_BG);
  
  char keyMap[4][4] = {
    {'A','B','C','D'},
    {'3','6','9','#'},
    {'2','5','8','0'},
    {'1','4','7','*'}
  };
  String keyStr = String(keyMap[r][c]);
  String filename = "/pass_" + keyStr + ".raw";
  
  if (SPIFFS.exists(filename)) {
    drawBitmapFromSPIFFS(x, y, filename.c_str());
  } else if (passIcons[r][c]) {
    drawBitmap32x32Color(x, y, passIcons[r][c]);
  }
  
  drawCenteredTextGuarded(dynamicPassLabels[r][c].c_str(), x + iconSize/2, y + iconSize + 3, 1, COL_TEXT, iconSize);
}

char pendingPassKey = 0;

void handleKey(char key) {
  if (menuState == MAIN_MENU) {
    if (key == 'A') { menuState = STEAMDECK; drawSteamdeckGrid(); }
    else if (key == 'B') { menuState = PASSWORD_MANAGER; drawPasswordManagerGrid(); }
    else if (key == 'C') { menuState = RFID_UNLOCK; drawRFIDScreen("Scan your tag..."); }
    return;
  }

  if (menuState == STEAMDECK) {
    int r=-1, c=-1;
    switch(key) {
      case 'A': r=0; c=0; break;
      case 'B': r=0; c=1; break;
      case 'C': r=0; c=2; break;
      case 'D': r=0; c=3; break;
      case '3': r=1; c=0; break;
      case '6': r=1; c=1; break;
      case '9': r=1; c=2; break;
      case '#': r=1; c=3; break;
      case '2': r=2; c=0; break;
      case '5': r=2; c=1; break;
      case '8': r=2; c=2; break;
      case '0': r=2; c=3; break;
      case '1': r=3; c=0; break;
      case '4': r=3; c=1; break;
      case '7': r=3; c=2; break;
      case '*': menuState = MAIN_MENU; drawMainMenu(); return;
    }
    if (r >= 0 && c >= 0) {
      flashIconGrid4x4(r, c);
      Serial.print("APP_LAUNCH: ");
      Serial.println(key);
    }
    return;
  }

  if (menuState == PASSWORD_MANAGER) {
    int r=-1, c=-1;
    switch(key) {
      case 'A': r=0; c=0; break;
      case 'B': r=0; c=1; break;
      case 'C': r=0; c=2; break;
      case 'D': r=0; c=3; break;
      case '3': r=1; c=0; break;
      case '6': r=1; c=1; break;
      case '9': r=1; c=2; break;
      case '#': r=1; c=3; break;
      case '2': r=2; c=0; break;
      case '5': r=2; c=1; break;
      case '8': r=2; c=2; break;
      case '0': r=2; c=3; break;
      case '1': r=3; c=0; break;
      case '4': r=3; c=1; break;
      case '7': r=3; c=2; break;
      case '*': menuState = MAIN_MENU; drawMainMenu(); return;
    }
    if (r >= 0 && c >= 0) {
      flashIconPassGrid(r, c);
      Serial.print("PASS_LAUNCH: ");
      Serial.println(key);
    }
    return;
  }
}

void drawRFIDScreen(const char* msg) {
  tft.fillScreen(COL_BG);
  tft.fillRect(0, 0, tft.width(), 56, COL_PANEL);
  drawCenteredTextGuarded("RFID", tft.width()/2, 8, 2, COL_ACCENT3, tft.width()-16);
  drawCenteredTextGuarded(msg, tft.width()/2, 36, 1, COL_ACCENT1, tft.width()-16);
}

unsigned long lastRFIDRead = 0;
unsigned long verificationStartTime = 0;
bool isVerifying = false;

void checkRFID() {
  uint8_t uid[7];
  uint8_t uidLength;
  
  if (isVerifying && (millis() - verificationStartTime > 5000)) {
      tft.fillScreen(COL_BG);
      drawCenteredTextGuarded("Timeout", tft.width()/2, tft.height()/2 - 8, 3, ILI9341_RED, tft.width()-32);
      delay(1000);
      isVerifying = false;
      menuState = MAIN_MENU;
      drawMainMenu();
      return;
  }
  
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "AUTH_OK") {
       isVerifying = false;
       tft.fillScreen(COL_BG);
       drawCenteredTextGuarded("Access Granted!", tft.width()/2, tft.height()/2 - 8, 3, COL_ACCENT3, tft.width()-32);
       delay(1400);
       
       if (menuState == RFID_VERIFY && pendingPassKey) {
          Serial.print("PASS_LAUNCH: ");
          Serial.println(pendingPassKey);
          pendingPassKey = 0;
          menuState = PASSWORD_MANAGER;
          drawPasswordManagerGrid();
       } else {
          Serial.println("RFID_UNLOCK_OK"); // Confirm unlock to PC (redundant but safe)
          menuState = MAIN_MENU;
          drawMainMenu();
       }
    }
    else if (cmd == "AUTH_FAIL") {
       isVerifying = false;
       tft.fillScreen(COL_BG);
       drawCenteredTextGuarded("Access Denied!", tft.width()/2, tft.height()/2 - 8, 3, ILI9341_RED, tft.width()-32);
       delay(1400);
       if (menuState == RFID_VERIFY) {
          pendingPassKey = 0;
          menuState = PASSWORD_MANAGER;
          drawPasswordManagerGrid();
       } else {
          menuState = MAIN_MENU;
          drawMainMenu();
       }
    }
  }

  if (!isVerifying && (millis() - lastRFIDRead > 500)) {
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 50)) { 
      lastRFIDRead = millis();
      verificationStartTime = millis();
      isVerifying = true;
      
      String uidStr = "";
      for (uint8_t i = 0; i < uidLength; i++) {
        if (uid[i] < 0x10) uidStr += "0";
        uidStr += String(uid[i], HEX);
      }
      uidStr.toUpperCase();
      
      Serial.print("RFID_READ: ");
      Serial.println(uidStr);
      
      drawRFIDScreen("Scanned! Verifying...");
    }
  }
}
