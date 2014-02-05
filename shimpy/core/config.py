
class Config(dict):
    def set_default(self, key, value):
        if key not in self:
            self[key] = value
