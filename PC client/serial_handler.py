import serial
import serial.tools.list_ports
import threading
import time

class SerialHandler:
    def __init__(self, port=None, baud_rate=115200, on_message=None):
        self.port = port
        self.baud_rate = baud_rate
        self.on_message = on_message
        self.serial_conn = None
        self.running = False
        self.thread = None
        self.connected = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()

    def _read_loop(self):
        while self.running:
            if not self.serial_conn or not self.serial_conn.is_open:
                self._connect()
            
            if self.serial_conn and self.serial_conn.is_open:
                try:
                    if self.serial_conn.in_waiting > 0:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if line and self.on_message:
                            self.on_message(line)
                except Exception as e:
                    print(f"Serial read error: {e}")
                    self.connected = False
                    self.serial_conn.close()
            
            time.sleep(0.1)

    def _connect(self):
        try:
            if self.port:
                self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
                self.connected = True
                print(f"Connected to {self.port}")
            else:
                pass
        except Exception as e:
            self.connected = False
            time.sleep(2)

    def send(self, message):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{message}\n".encode())
            except Exception as e:
                print(f"Send Error: {e}")

    def send_icon_data(self, key, data, icon_type="app"):
        """
        Send icon data to Arduino
        icon_type: "app" or "pass" to differentiate between app and password icons
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
            
        total_size = len(data)
        print(f"Sending {icon_type} icon for key {key}, size: {total_size} bytes")
        
        self.send(f"ICON_START:{icon_type}:{key}:{total_size}")
        time.sleep(0.5)
        
        chunk_size = 32
        for i in range(0, total_size, chunk_size):
            chunk = data[i:i+chunk_size]
            hex_chunk = chunk.hex().upper()
            self.send(f"ICON_DATA:{hex_chunk}")
            time.sleep(0.1)
            
        time.sleep(0.5)
        self.send("ICON_END")
        print("Icon upload complete")
        return True

    def get_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]
