import json


class JsonWriter:
    def __init__(self, path):
        self.path = path
        self.file = None
        self.first_item = True

    def __enter__(self):
        self.file = open(self.path, "w", encoding="utf-8")
        self.file.write("[\n")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.write("\n]")
        self.file.close()

    def write(self, obj):
        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        json.dump(obj, self.file, ensure_ascii=False, indent=4)
        self.file.flush()
