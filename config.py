# ----- ОБЩИЕ НАСТРОЙКИ -----
# Количество комнат для парсинга
DEAL_TYPE = "sale"
ENGINE_VERSION = 2
OFFER_TYPE = "flat"
REGION = 1
ROOMS = 1
SORT = "creation_date_asc"


# ----- ФАЙЛЫ -----
# Папка, в которую сохраняем результат парсинга
OUTPUT_DIRNAME = "trash"

# Имя JSON-файла
# OUTPUT_FILENAME = f"{ROOMS} комн (0-).json"
OUTPUT_FILENAME = "test"

# ----- ПОИСК -----
BASE_URL = (
    "https://www.cian.ru/cat.php?currency=2"
    f"&deal_type={DEAL_TYPE}"
    f"&engine_version={ENGINE_VERSION}"
    f"&offer_type={OFFER_TYPE}"
    f"&region={REGION}"
    f"&room{ROOMS}=1"
    f"&sort={SORT}"
)

# Диапазоны цен (minprice/maxprice)
LIMITS = tuple(range(10_000_000, 250_000_000 + 1, 1_000_000))


# ----- ЗАДЕРЖКИ -----
# Паузы между загрузкой страниц
DELAY_BETWEEN_PAGES = (1, 3)    # сек

# Паузы между загрузкой объявлений
DELAY_BETWEEN_ADS = (1, 2)      # сек


# ----- ПОВТОРЫ -----
# Количество попыток при ошибках сети (HTTP, 429 и т. д.)
FETCH_RETRIES = 5

# Базовая задержка между повторными попытками
FETCH_DELAY = 5


# ----- USER_AGENTS -----
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1"
]


# ----- ЗАГОЛОВКИ -----
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Referer": "https://www.cian.ru/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}
