import json
import base64
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class EncryptionManager:
    def __init__(self, key_file="master.key"):
        self.key_file = key_file
        self.master_key = None
        self.salt = None

    def generate_key(self):
        self.salt = get_random_bytes(16)
        self.master_key = get_random_bytes(32)
        return self.master_key

    def save_key_to_file(self, path):
        if not self.master_key: return
        data = {
            "key": base64.b64encode(self.master_key).decode('utf-8'),
            "salt": base64.b64encode(self.salt).decode('utf-8')
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_key_from_file(self, path):
        if not os.path.exists(path): return False
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.master_key = base64.b64decode(data["key"])
            self.salt = base64.b64decode(data["salt"])
            return True
        except:
            return False

    def encrypt_data(self, data):
        if not self.master_key:
            raise ValueError("Master key not loaded.")

        if isinstance(data, dict) or isinstance(data, list):
            data_str = json.dumps(data)
        else:
            data_str = str(data)

        cipher = AES.new(self.master_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data_str.encode('utf-8'))

        return {
            "nonce": base64.b64encode(cipher.nonce).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "salt": base64.b64encode(self.salt).decode('utf-8')
        }

    def decrypt_data(self, encrypted_package):
        if not self.master_key:
            raise ValueError("Master key not loaded.")

        try:
            nonce = base64.b64decode(encrypted_package['nonce'])
            tag = base64.b64decode(encrypted_package['tag'])
            ciphertext = base64.b64decode(encrypted_package['ciphertext'])
            
            cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            
            try:
                return json.loads(decrypted_data.decode('utf-8'))
            except json.JSONDecodeError:
                return decrypted_data.decode('utf-8')
                
        except (ValueError, KeyError) as e:
            print(f"Decryption failed: {e}")
            return None

    def clear_key(self):
        self.master_key = None
        self.salt = None
