import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import sys
from datetime import datetime

# ============= ФУНКЦИЯ ДЛЯ ВРЕМЕНИ =============

def log(message):
    """Выводит сообщение с временной меткой"""
    timestamp = datetime.now().strftime("%m.%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# ============= НАСТРОЙКИ (из командной строки или по умолчанию) =============

DEFAULT_MINER_ID = "11111"
DEFAULT_AUTH_KEY = "ffffffffffffffffffffffff"
DEFAULT_TEMP_MIN_OK = 67
DEFAULT_TEMP_MAX_OK = 72
DEFAULT_FAN_MIN = 30
DEFAULT_FAN_MAX = 100
DEFAULT_CHECK_INTERVAL = 10
DEFAULT_FAN_DECREASE_CONFIRM_TIME = 60

MINER_ID = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MINER_ID
AUTH_KEY = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_AUTH_KEY
TEMP_MIN_OK = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_TEMP_MIN_OK
TEMP_MAX_OK = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_TEMP_MAX_OK
FAN_MIN = int(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_FAN_MIN
FAN_MAX = int(sys.argv[6]) if len(sys.argv) > 6 else DEFAULT_FAN_MAX
CHECK_INTERVAL = int(sys.argv[7]) if len(sys.argv) > 7 else DEFAULT_CHECK_INTERVAL
FAN_DECREASE_CONFIRM_TIME = int(sys.argv[8]) if len(sys.argv) > 8 else DEFAULT_FAN_DECREASE_CONFIRM_TIME

TEMP_HIGH_THRESHOLD = TEMP_MAX_OK + 1
TEMP_LOW_THRESHOLD = TEMP_MIN_OK - 1
FAN_INCREASE_INTERVAL = CHECK_INTERVAL
FAN_DECREASE_INTERVAL = FAN_DECREASE_CONFIRM_TIME

MINER_URL = f"https://pitbit.online/miner/{MINER_ID}"
MINER_SETTINGS_URL = f"https://pitbit.online/miner/{MINER_ID}/settings"
AUTH_FAST_URL = f"https://pitbit.online/authfast/{AUTH_KEY}"

print("\n" + "="*60)
print("НАСТРОЙКИ АВТОМАТИЗАЦИИ:")
print("="*60)
print(f"Майнер ID: {MINER_ID}")
print(f"Ключ авторизации: {AUTH_KEY}")
print(f"Нормальная температура: {TEMP_MIN_OK}-{TEMP_MAX_OK}°C")
print(f"Повышение кулера при: >={TEMP_HIGH_THRESHOLD}°C")
print(f"Понижение кулера при: <={TEMP_LOW_THRESHOLD}°C")
print(f"Скорость кулера: {FAN_MIN}-{FAN_MAX}%")
print(f"Проверка температуры каждые: {CHECK_INTERVAL} сек")
print(f"Интервал повышения кулера: {FAN_INCREASE_INTERVAL} сек")
print(f"Подтверждение низкой температуры: {FAN_DECREASE_CONFIRM_TIME} сек")
print("="*60)
print(f"\nИспользование: python pitbit_auto.py [MINER_ID] [AUTH_KEY] [TEMP_MIN] [TEMP_MAX] [FAN_MIN] [FAN_MAX] [CHECK_INTERVAL] [DECREASE_CONFIRM_TIME]")
print(f"Пример: python pitbit_auto.py 11111 ffffffffffffffffffffffff 67 72 30 100 10 60")
print("="*60 + "\n")

# ============= ИНИЦИАЛИЗАЦИЯ =============

try:
    driver = uc.Chrome(user_data_dir=r'C:\selenium_profile')
    log("🔐 Выполняем автоматическую авторизацию...")
    driver.get(AUTH_FAST_URL)
    log("⏳ Ждём 10 секунд для завершения авторизации...")
    time.sleep(10)
    log("✅ Авторизация завершена, переходим к мониторингу")
except Exception as e:
    log(f"❌ КРИТИЧЕСКАЯ ОШИБКА при инициализации браузера: {e}")
    log("Убедитесь, что Chrome установлен и профиль C:\\selenium_profile существует")
    sys.exit(1)

fan_last_update = 0
low_temp_detected_at = 0

# ============= ФУНКЦИИ =============

def reauthorize():
    """Переходит на страницу быстрой авторизации и ждёт 10 секунд"""
    try:
        log("🔐 Переходим на страницу быстрой авторизации...")
        driver.get(AUTH_FAST_URL)
        log("⏳ Ждём 10 секунд для завершения авторизации...")
        time.sleep(10)
        log("✅ Авторизация завершена, продолжаем работу")
        return True
    except Exception as e:
        log(f"❌ Ошибка при авторизации: {e}")
        return False

def get_temperature():
    """Получает температуру со страницы майнера. Возвращает None при ошибке."""
    try:
        temp_elem = driver.find_element(By.ID, f"limittemp{MINER_ID}")
        temp_text = temp_elem.text.strip()
        match = re.search(r'(\d+)\s*°C', temp_text)
        if match:
            return int(match.group(1))
        else:
            log(f"❌ Не удалось распарсить температуру из '{temp_text}'")
            return None
    except Exception as e:
        log(f"❌ Ошибка получения температуры: {e}")
        return None

def set_fan_value(new_value):
    """Устанавливает значение кулера. Возвращает True при успехе, False при ошибке."""
    try:
        fan_input = driver.find_element(By.XPATH, "//input[@type='text'][@value]")
        driver.execute_script(f"arguments[0].value = '{new_value}';", fan_input)
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, fan_input)
        time.sleep(1)
        fan_input.send_keys(Keys.ENTER)
        return True
    except Exception as e:
        log(f"❌ Ошибка установки значения кулера: {e}")
        return False

def get_fan_value():
    """Получает текущее значение кулера. Возвращает None при ошибке."""
    try:
        fan_input = driver.find_element(By.XPATH, "//input[@type='text'][@value]")
        return int(fan_input.get_attribute('value'))
    except Exception as e:
        log(f"❌ Ошибка получения значения кулера: {e}")
        return None

def safe_navigate(url, retry_count=3):
    """Безопасная навигация с повторными попытками"""
    for attempt in range(retry_count):
        try:
            driver.get(url)
            return True
        except Exception as e:
            log(f"❌ Ошибка навигации (попытка {attempt+1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(5)
            else:
                return False
    return False

# ============= ОСНОВНОЙ ЦИКЛ =============

log("🚀 Начинаем мониторинг... (Скрипт работает бесконечно, Ctrl+C для остановки)\n")

consecutive_errors = 0
temp_read_failures = 0

while True:
    try:
        if not safe_navigate(MINER_URL):
            log(f"❌ Не удалось перейти на страницу майнера, ждём {CHECK_INTERVAL} сек")
            consecutive_errors += 1
            time.sleep(CHECK_INTERVAL)
            continue
        
        time.sleep(3)
        
        temp = get_temperature()
        if temp is None:
            temp_read_failures += 1
            log(f"❌ Не удалось получить температуру (попытка {temp_read_failures})")
            
            if reauthorize():
                temp_read_failures = 0
                log(f"⏳ Ждём {CHECK_INTERVAL} сек перед следующей попыткой")
                time.sleep(CHECK_INTERVAL)
                continue
            else:
                log(f"❌ Авторизация не удалась, ждём {CHECK_INTERVAL} сек")
                consecutive_errors += 1
                time.sleep(CHECK_INTERVAL)
                continue
        
        temp_read_failures = 0
        consecutive_errors = 0
        log(f"📊 Температура: {temp}°C")
        now = time.time()
        
        if temp >= TEMP_HIGH_THRESHOLD:
            low_temp_detected_at = 0
            
            if now - fan_last_update < FAN_INCREASE_INTERVAL:
                wait_time = int(FAN_INCREASE_INTERVAL - (now - fan_last_update))
                log(f"⏳ Повышение не чаще раза в {FAN_INCREASE_INTERVAL} сек, ждём ещё {wait_time} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if not safe_navigate(MINER_SETTINGS_URL):
                log(f"❌ Не удалось перейти на страницу настроек, ждём {CHECK_INTERVAL} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            time.sleep(3)
            
            fan_current = get_fan_value()
            if fan_current is None:
                log(f"❌ Не удалось получить значение кулера, ждём {CHECK_INTERVAL} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f"🌀 Текущая скорость кулера: {fan_current}%")
            
            new_fan = min(fan_current + 1, FAN_MAX)
            
            if new_fan == fan_current:
                log(f"⚠️ Кулер уже на максимуме {fan_current}%")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if set_fan_value(new_fan):
                log(f"⬆️ Темп. {temp}°C >= {TEMP_HIGH_THRESHOLD}, повышаем кулер с {fan_current}% до {new_fan}%")
                fan_last_update = now
                time.sleep(3)
            else:
                log(f"❌ Не удалось установить значение")
            
            time.sleep(CHECK_INTERVAL)
            continue
        
        elif temp <= TEMP_LOW_THRESHOLD:
            if low_temp_detected_at == 0:
                low_temp_detected_at = now
                log(f"❄️ Низкая температура {temp}°C обнаружена, ждём {FAN_DECREASE_CONFIRM_TIME} сек для подтверждения")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if now - low_temp_detected_at < FAN_DECREASE_CONFIRM_TIME:
                remaining = int(FAN_DECREASE_CONFIRM_TIME - (now - low_temp_detected_at))
                log(f"⏳ Низкая температура, ждём подтверждения ещё {remaining} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if now - fan_last_update < FAN_DECREASE_INTERVAL:
                wait_time = int(FAN_DECREASE_INTERVAL - (now - fan_last_update))
                log(f"⏳ Понижение не чаще раза в {FAN_DECREASE_INTERVAL} сек, ждём ещё {wait_time} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if not safe_navigate(MINER_SETTINGS_URL):
                log(f"❌ Не удалось перейти на страницу настроек, ждём {CHECK_INTERVAL} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            time.sleep(3)
            
            fan_current = get_fan_value()
            if fan_current is None:
                log(f"❌ Не удалось получить значение кулера, ждём {CHECK_INTERVAL} сек")
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f"🌀 Текущая скорость кулера: {fan_current}%")
            
            new_fan = max(fan_current - 1, FAN_MIN)
            
            if new_fan == fan_current:
                log(f"⚠️ Темп. {temp}°C <= {TEMP_LOW_THRESHOLD}, но кулер уже на минимуме {fan_current}%")
                low_temp_detected_at = 0
                time.sleep(CHECK_INTERVAL)
                continue
            
            if set_fan_value(new_fan):
                log(f"⬇️ Темп. {temp}°C <= {TEMP_LOW_THRESHOLD} (более {FAN_DECREASE_CONFIRM_TIME} сек), понижаем кулер с {fan_current}% до {new_fan}%")
                fan_last_update = now
                low_temp_detected_at = 0
                time.sleep(3)
            else:
                log(f"❌ Не удалось установить значение")
            
            time.sleep(CHECK_INTERVAL)
            continue
        
        else:
            low_temp_detected_at = 0
            log(f"✅ Температура {temp}°C в норме ({TEMP_MIN_OK}-{TEMP_MAX_OK}), ждём {CHECK_INTERVAL} сек")
            time.sleep(CHECK_INTERVAL)
            continue
    
    except KeyboardInterrupt:
        log("\n⛔ Получен сигнал остановки (Ctrl+C)")
        log("🛑 Останавливаем мониторинг...")
        driver.quit()
        sys.exit(0)
    
    except Exception as e:
        consecutive_errors += 1
        log(f"❌ НЕПРЕДВИДЕННАЯ ОШИБКА в основном цикле: {e}")
        log(f"⚠️ Последовательных ошибок: {consecutive_errors}")
        
        if consecutive_errors >= 10:
            log("🚨 КРИТИЧНО: Слишком много ошибок подряд!")
            log("Возможно, проблема с подключением или браузер упал")
            log("⏸️ Ждём 60 секунд перед продолжением...")
            time.sleep(60)
            consecutive_errors = 0
        else:
            log("⏸️ Ждём 30 секунд перед повтором...")
            time.sleep(30)
        continue

