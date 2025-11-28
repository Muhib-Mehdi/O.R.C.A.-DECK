import json
import hashlib
import os

SECURITY_FILE = "security_data.json"

class SecurityManager:
    def __init__(self, data_dir):
        self.file_path = os.path.join(data_dir, SECURITY_FILE)
        self.questions = [
            "What was the name of your first pet?",
            "What is your mother's maiden name?",
            "What city were you born in?"
        ]
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)

    def is_setup(self):
        return bool(self.data.get("answers"))

    def set_answers(self, answers):
        hashed_answers = []
        for ans in answers:
            norm = ans.lower().strip()
            hashed = hashlib.sha256(norm.encode()).hexdigest()
            hashed_answers.append(hashed)
        
        self.data["answers"] = hashed_answers
        self.save_data()

    def verify_answers(self, answers):
        if not self.is_setup(): return False
        
        stored = self.data.get("answers", [])
        if len(answers) != len(stored): return False
        
        for i, ans in enumerate(answers):
            norm = ans.lower().strip()
            hashed = hashlib.sha256(norm.encode()).hexdigest()
            if hashed != stored[i]:
                return False
        return True

    def get_questions(self):
        return self.questions
