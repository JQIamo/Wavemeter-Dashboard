import json


class Config:
    def __init__(self, path=''):
        self.path = ''
        self.config_dict = {}

        if path:
            self.load_config(path)

    def load_config(self, path):
        self.path = path

        with open(self.path) as f:
            self.config_dict = json.load(f)

    def has(self, item):
        return item in self.config_dict

    def get(self, item, default=None):
        if self.has(item):
            return self.config_dict[item]
        else:
            return default

    def set(self, item, value):
        self.config_dict[item] = value

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.config_dict, f, indent=4, sort_keys=True)


config = Config()  # placeholder, to be initialized later in main.py
