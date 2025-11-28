import unittest
import json
from encryption_manager import EncryptionManager

class TestEncryption(unittest.TestCase):
    def setUp(self):
        self.em = EncryptionManager()
        self.password = "test_password"
        self.data = {"steam": {"username": "user", "password": "pass"}}

    def test_encryption_decryption(self):
        # Generate key
        self.em.generate_key(self.password)
        
        # Encrypt
        encrypted = self.em.encrypt_data(self.data)
        self.assertIn("ciphertext", encrypted)
        self.assertIn("nonce", encrypted)
        self.assertIn("tag", encrypted)
        self.assertIn("salt", encrypted)
        
        # Decrypt
        decrypted = self.em.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.data)

    def test_wrong_password(self):
        # Generate key
        self.em.generate_key(self.password)
        encrypted = self.em.encrypt_data(self.data)
        
        # Try to decrypt with wrong password
        em2 = EncryptionManager()
        em2.load_key("wrong_password", encrypted["salt"])
        
        decrypted = em2.decrypt_data(encrypted)
        self.assertIsNone(decrypted)

if __name__ == '__main__':
    unittest.main()
