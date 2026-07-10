import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options

CHANNEL_URL = 'https://ble.ir/s/akharinkhabar'   # آدرس کانال
POSTS_FILE = 'posts.json'
POLL_INTERVAL = 120        # ثانیه
MAX_SCROLLS = 5           # سقف اسکرول برای جلوگیری از حلقه بی‌نهایت
SCROLL_PAUSE = 2           # مکث بعد از هر اسکرول برای لود شدن پیام‌ها


# ---------- پارس پیام‌ها از HTML ----------
def parse_messages(html):
    soup = BeautifulSoup(html, 'html.parser')
    messages = soup.find_all(
        'div', class_=lambda x: x and x.startswith('MessageItem_messageWrapper')
    )

    posts = []
    for msg in messages:
        sid = msg.get('data-sid')
        if not sid:
            continue

        text_elem = msg.find('div', class_=lambda x: x and x.startswith('Text_text'))

        posts.append({
            'sid': sid,
            'text': text_elem.get_text(separator='\n', strip=True) if text_elem else '',
        })
    return posts


# ---------- خواندن/نوشتن فایل JSON ----------
def load_posts():
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ خطا در خواندن فایل: {e} — با لیست خالی شروع می‌شود")
    return []


def save_posts(posts):
    try:
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"⚠ خطا در نوشتن فایل: {e}")


# ---------- راه‌اندازی مرورگر ----------
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.set_preference(
        'general.useragent.override',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
    )
    return webdriver.Firefox(options=options)


# ---------- اسکرول به بالا تا رسیدن به آخرین پیام قبلی ----------
def scroll_and_collect(driver, seen_sids):
    scroller = driver.find_element(
        By.CSS_SELECTOR, "div[class*='ChatWrapper_scrollListWrapper']"
    )

    for i in range(MAX_SCROLLS):
        posts = parse_messages(driver.page_source)

        # اگر یکی از پیام‌های قبلی توی صفحه دیده شد، کافیه
        if seen_sids and any(p['sid'] in seen_sids for p in posts):
            print(f"  ✓ به آخرین پیام قبلی رسیدیم (بعد از {i} اسکرول)")
            return posts

        # اسکرول به بالای لیست برای لود پیام‌های قدیمی‌تر
        prev_height = driver.execute_script(
            "return arguments[0].scrollHeight;", scroller
        )
        driver.execute_script("arguments[0].scrollTop = 0;", scroller)
        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight;", scroller
        )

        # اگر ارتفاع تغییری نکرد یعنی پیام قدیمی‌تری وجود نداره
        if new_height == prev_height:
            print(f"  ✓ به ابتدای کانال رسیدیم (بعد از {i + 1} اسکرول)")
            return parse_messages(driver.page_source)

    print(f"  ⚠ به سقف {MAX_SCROLLS} اسکرول رسیدیم")
    return parse_messages(driver.page_source)


def fetch_new_posts(driver):
    # خواندن پست‌های قبلی از فایل
    all_posts = load_posts()
    seen_sids = {p['sid'] for p in all_posts}
    print(f"📂 {len(all_posts)} پست از فایل بارگذاری شد")

    print(f"\n🔄 بررسی کانال... ({time.strftime('%H:%M:%S')})")
    driver.get(CHANNEL_URL)

    # صبر تا لود شدن اولین پیام
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[class*='MessageItem_messageWrapper']")
        )
    )
    time.sleep(2)  # فرصت برای رندر کامل

    # اسکرول به عقب تا رسیدن به پیام‌های قبلی
    page_posts = scroll_and_collect(driver, seen_sids)

    # فیلتر پست‌های جدید
    new_posts = [p for p in page_posts if p['sid'] not in seen_sids]

    if new_posts:
        print(f"🆕 {len(new_posts)} پست جدید:")
        for post in new_posts:
            seen_sids.add(post['sid'])
            all_posts.append(post)
            print('─' * 40)
            print(post['text'][:200])
            print(f"🆔 {post['sid']}")

        all_posts = all_posts[-1000:]
        # ذخیره در فایل (اگر نبود ساخته می‌شود)
        save_posts(all_posts)
        print(f"💾 مجموعاً {len(all_posts)} پست ذخیره شد")
    else:
        print("پست جدیدی نیست")

    return new_posts


# ---------- حلقه اصلی ----------
def monitor_channel(driver):
    try:
        while True:
            try:
                fetch_new_posts(driver)

            except Exception as e:
                print(f"⚠ خطا: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    driver = setup_driver()
    fetch_new_posts(driver)
