#! /usr/bin/env python3
import json
from pathlib import Path

class Database():

    def __init__(self, storage_file="database.json"):
        self.file = storage_file
        self.data = self.read_to_dict(self.file)
    
    def cleanup(self):
        self.write_to_disk()
    
    def read_to_dict(self, file):
        if Path(file).exists():
            try:
                dict = json.loads(file)
            except:
                dict = {}
        return dict

    def convert_to_json(self):
        json_lines = json.dumps(self.data, indent=4, sort_keys=True)
        return json_lines

    def write_to_disk(self):
        output = self.convert_to_json()
        # self.convert_to_json always outputs a single string
        with open(self.file, "w+") as file:
            file.write(output)

    def add(self, keyword, value):
        keyword = str(keyword)
        if keyword not in self.data.keys():
            self.data[keyword] = []
        self.data[keyword].append(value)
    
    def remove(self, keyword, value):
        keyword = str(keyword)
        if keyword in self.data.keys():
            self.data[keyword].pop(value)