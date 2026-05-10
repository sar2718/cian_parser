import os
from datetime import datetime
from config import OUTPUT_DIRNAME, OUTPUT_FILENAME

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(BASE_DIR, OUTPUT_DIRNAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_unique_filename(base_name: str) -> str:
    name, ext = os.path.splitext(base_name)

    today = datetime.now().strftime("%Y-%m-%d")
    dated_name = f"{name} {today}{ext}"

    final_path = os.path.join(OUTPUT_DIR, dated_name)

    if not os.path.exists(final_path):
        return final_path

    counter = 1
    while True:
        numbered = f"{name} {today} ({counter}){ext}"
        final_path = os.path.join(OUTPUT_DIR, numbered)
        if not os.path.exists(final_path):
            return final_path
        counter += 1


OUTPUT_FILE = generate_unique_filename(OUTPUT_FILENAME)
