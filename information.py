import json
import os


class Information:
    def __init__(self):
        self.file = "information.json"
        self.default_questions = [
            "What is your discord username (e.g. User#0000)?",
            "Why were you banned?",
            "Did you deserve it?",
            "What will you do to prevent getting banned again?",
            "How long has it been since you were banned?",
            "Any other information?",
        ]
        self.load()

        print(f"information: {self.info}")

    def load(self):
        if os.stat(self.file).st_size == 0:
            self.info = {}
        else:
            with open(self.file, "r") as f:
                self.info = json.load(f)

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.info, f, indent=4)

    def create_server_info(self, server_id):
        self.info[str(server_id)] = {"questions": self.default_questions}

        self.save()
