import random
import time

import requests

from config import DEFAULT_HEADERS, FETCH_DELAY, FETCH_RETRIES, USER_AGENTS


def create_session() -> requests.Session:
    session = requests.Session()

    headers = DEFAULT_HEADERS.copy()
    rotate_user_agent(session)

    session.headers.update(headers)
    session.get("https://www.cian.ru/")
    return session


def fetch_html(session, url, retries: int = FETCH_RETRIES, delay: int = FETCH_DELAY):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else None
            wait_time = delay + random.uniform(0, 5)

            if status == 429:
                print(
                    f"\t⚠️ 429 Too Many Requests. Повторная попытка ({attempt+1}/{retries}). Ждём {wait_time:.1f} сек..."
                )
                time.sleep(wait_time)
            elif status == 403:
                print(
                    f"\t⚠️ 403 Forbidden. Меняем User-Agent и повторяем попытку ({attempt+1}/{retries})..."
                )
                rotate_user_agent(session)
                time.sleep(wait_time)
            else:
                print(
                    f"\t❌ Ошибка {e.response.status_code if e.response else '???'} при загрузке {url}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"\t⚠️ Ошибка сети: {e}. Попытка {attempt+1}/{retries}")
            time.sleep(delay + random.uniform(0, 3))

    print(f"\t❌ Не удалось загрузить {url} после {retries} попыток, пропускаем")
    return None


def rotate_user_agent(session):
    session.headers["User-Agent"] = random.choice(USER_AGENTS)
