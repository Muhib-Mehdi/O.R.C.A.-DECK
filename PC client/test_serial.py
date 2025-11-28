import unittest
from unittest.mock import MagicMock, patch
from serial_handler import SerialHandler
import time

class TestSerialHandler(unittest.TestCase):
    @patch('serial.Serial')
    def test_serial_connection(self, mock_serial):
        # Setup mock
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance
        mock_instance.is_open = True
        mock_instance.in_waiting = 1
        mock_instance.readline.return_value = b"TEST_MESSAGE\n"
        
        # Callback
        received_msgs = []
        def on_msg(msg):
            received_msgs.append(msg)
            
        # Init handler
        handler = SerialHandler(port="COM_MOCK", on_message=on_msg)
        
        # Start (mocking the thread loop to run once)
        handler._connect()
        handler.serial_conn = mock_instance # Force set
        
        # Simulate one read loop iteration
        if handler.serial_conn.in_waiting > 0:
            line = handler.serial_conn.readline().decode('utf-8').strip()
            if line and handler.on_message:
                handler.on_message(line)
                
        self.assertEqual(received_msgs, ["TEST_MESSAGE"])
        
        # Test send
        handler.send("HELLO")
        mock_instance.write.assert_called_with(b"HELLO\n")

if __name__ == '__main__':
    unittest.main()
