"""
auth.py — загрузка cookies и Selenium-аутентификация
"""
import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

COOKIES_FILE = Path("/root/.avito_cookies/cookies.json")
AVITO_URL = "https://www.avito.ru"


def load_cookies() -> list:
    """Загрузить cookies из JSON файла."""
    if not COOKIES_FILE.exists():
        raise FileNotFoundError(f"Cookies file not found: {COOKIES_FILE}")
    with open(COOKIES_FILE, "r") as f:
        return json.load(f)


def save_cookies(driver, output_file: Path = COOKIES_FILE):
    """Сохранить cookies из Selenium driver в JSON."""
    cookies = driver.get_cookies()
    with open(output_file, "w") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    os.chmod(output_file, 0o600)
    print(f"  ✓ Cookies saved to {output_file} ({len(cookies)} cookies)")


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Создать Chrome driver с options."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # SOCKS5 proxy через SSH reverse tunnel от ПК Олега (10.06.2026)
    # Hermes поднял Dante на 127.0.0.1:1080, туда биндится Аликс через ssh -R
    options.add_argument("--proxy-server=socks5://127.0.0.1:1080")
    
    # Используем Google Chrome (не snap chromium)
    options.binary_location = "/usr/bin/google-chrome"
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def apply_cookies(driver, cookies: list, base_url: str = AVITO_URL):
    """Применить cookies к driver. Сначала открыть base_url, потом add_cookie."""
    driver.get(base_url)
    for cookie in cookies:
        # Selenium add_cookie не принимает sameSite=None без secure=True для HTTPS
        cookie_clean = {k: v for k, v in cookie.items() if k in ("name", "value", "domain", "path")}
        if "expiry" in cookie and cookie["expiry"]:
            cookie_clean["expiry"] = cookie["expiry"]
        try:
            driver.add_cookie(cookie_clean)
        except Exception as e:
            print(f"  ! Cookie {cookie.get('name')}: {e}")


def verify_auth(driver) -> bool:
    """Проверить, залогинены ли мы на Avito."""
    driver.get(f"{AVITO_URL}/profile")
    # Если залогинены — увидим имя/аватар
    # Иначе — форму логина
    try:
        # Ждём загрузки
        import time
        time.sleep(3)
        # Проверяем по URL — если редиректнуло на login, не залогинены
        current_url = driver.current_url
        if "login" in current_url.lower() or "auth" in current_url.lower():
            return False
        # Проверяем наличие признаков залогина (можно по title)
        title = driver.title
        if "Вход" in title or "Login" in title or "войти" in title.lower():
            return False
        return True
    except Exception:
        return False


def refresh_cookies(headless: bool = True) -> int:
    """Обновить cookies (залогиниться, скопировать, сохранить)."""
    driver = create_driver(headless=headless)
    try:
        driver.get(AVITO_URL)
        print("  → Залогинься вручную в открывшемся браузере (если появится форма)")
        print("  → Подожди 60 сек пока я проверю авторизацию")
        import time
        for i in range(60):
            time.sleep(1)
            if verify_auth(driver):
                print(f"  ✓ Авторизация подтверждена через {i+1} сек")
                save_cookies(driver)
                return 0
        print("  ✗ Авторизация не подтверждена за 60 сек")
        return 1
    finally:
        driver.quit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--refresh":
        sys.exit(refresh_cookies())
    else:
        # Просто проверить cookies
        driver = create_driver()
        try:
            cookies = load_cookies()
            print(f"  → Загружено {len(cookies)} cookies")
            apply_cookies(driver, cookies)
            print("  → Cookies применены")
            if verify_auth(driver):
                print("  ✓ АВТОРИЗАЦИЯ УСПЕШНА!")
            else:
                print("  ✗ Авторизация не подтверждена — cookies протухли")
                print("    Запусти: python3 auth.py --refresh")
        finally:
            driver.quit()
