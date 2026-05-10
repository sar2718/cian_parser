import os
import json


def load_json_files(folder_path: str) -> list:

    all_ads = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)

                if isinstance(content, list):
                    all_ads.extend(content)
                elif isinstance(content, dict):
                    all_ads.append(content)

            print(
                f" Загружено объявлений из {filename}: {len(content) if isinstance(content, list) else 1}"
            )

        except Exception as e:
            print(f" Ошибка при чтении {file_path}: {e}")

    return all_ads


def merge_ads(ad_list: list) -> tuple[list, int, int]:

    merged_ads = {}
    duplicate_count = 0

    for i, ad in enumerate(ad_list, start=1):
        url = ad.get("url")

        if url in merged_ads:
            duplicate_count += 1
            continue

        merged_ads[url] = ad

    return list(merged_ads.values()), duplicate_count


def save_to_json(data: list, output_path: str):

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n Сохранено {len(data)} объявлений в файл: {output_path}")
    except Exception as e:
        print(f" Ошибка при сохранении: {e}")


def main():

    folder = input("Введите путь к папке с JSON-файлами: ").strip()
    output_file = input("Введите имя итогового файла (с расширением .json): ").strip()

    print("\n Загружаем файлы...")
    all_ads = load_json_files(folder)
    print(f"\n Найдено объявлений: {len(all_ads)}")

    merged_ads, duplicates = merge_ads(all_ads)

    print(f"\n РЕЗУЛЬТАТ:")
    print(f"   ├ Всего объявлений до объединения: {len(all_ads)}")
    print(f"   ├ Уникальных объявлений: {len(merged_ads)}")
    print(f"   ├ Найдено дубликатов: {duplicates}")

    save_to_json(merged_ads, output_file)


if __name__ == "__main__":
    main()
