"""
Load test data from JSON files.
"""

import json


class TestData:
    json_file_path: str = "test_data/test_data.json"
    json_data: dict = {}

    def load_test_data(self):
        with open(self.json_file_path, "r") as f:
            self.json_data = json.load(f)

    def get_test_data(self, key: str) -> dict:
        if len(self.json_data.keys()) == 0:
            self.load_test_data()
        return self.json_data.get(key, {})
