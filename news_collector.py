import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from model import NewsPost
from news_classifier import classify_news

CHANNEL_URL = 'https://ble.ir/s/akharinkhabar'  # آدرس کانال
MAX_SCROLLS = 50  # سقف اسکرول برای جلوگیری از حلقه بی‌نهایت
SCROLL_PAUSE = 2  # مکث بعد از هر اسکرول برای لود شدن پیام‌ها

selenium_driver = None


def setup_selenium_driver():
    global selenium_driver

    options = Options()
    options.add_argument('--headless')
    options.set_preference(
        'general.useragent.override',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
    )
    selenium_driver = webdriver.Firefox(options=options)


def normalize_news_text(text: str):
    normalized_text = text.replace("@Akharinkhabar\n|\nakharinkhabar.ir", "")
    normalized_text = text.replace("@Akharinkhabar", "")
    normalized_text = text.replace("akharinkhabar.ir", "")
    normalized_text = text.replace(" | ", "")
    return normalized_text


def parse_messages(html: str, parsed_sids: set[str]):
    soup = BeautifulSoup(html, 'html.parser')
    messages = soup.find_all(
        'div', class_=lambda x: x and x.startswith('MessageItem_messageWrapper')
    )
    messages = reversed(messages)

    news_posts: list[NewsPost] = []
    for msg in messages:
        sid = msg.get('data-sid')
        if not sid or sid in parsed_sids:
            continue

        text_elem = msg.find('div', class_=lambda x: x and x.startswith('Text_text'))
        text = text_elem.get_text(separator='\n', strip=True) if text_elem else ''
        normalized_text = normalize_news_text(text.strip())

        new_post = NewsPost(sid=sid, text=normalized_text, category=classify_news(normalized_text))
        print('─' * 30 + ' NEW-POST ' + '─' * 30)
        print(f"[ {new_post.category.value if new_post.category else None} ]")
        print(new_post.text[:200])
        print(f"🆔 {new_post.sid}")

        news_posts.append(new_post)
        parsed_sids.add(sid)
    return news_posts


def scroll_and_collect(seen_sids: list[str]):
    scroller = selenium_driver.find_element(
        By.CSS_SELECTOR, "div[class*='ChatWrapper_scrollListWrapper']"
    )

    parsed_sids = set()
    for i in range(MAX_SCROLLS):
        news_posts = parse_messages(selenium_driver.page_source, parsed_sids)

        # اگر یکی از پیام‌های قبلی توی صفحه دیده شد، کافیه
        if seen_sids and any(p.sid in seen_sids for p in news_posts):
            print(f"  ✓ به آخرین پیام قبلی رسیدیم (بعد از {i} اسکرول)")
            return news_posts

        # اسکرول به بالای لیست برای لود پیام‌های قدیمی‌تر
        prev_height = selenium_driver.execute_script(
            "return arguments[0].scrollHeight;", scroller
        )
        selenium_driver.execute_script("arguments[0].scrollTop = 0;", scroller)
        time.sleep(SCROLL_PAUSE)

        new_height = selenium_driver.execute_script(
            "return arguments[0].scrollHeight;", scroller
        )

        # اگر ارتفاع تغییری نکرد یعنی پیام قدیمی‌تری وجود نداره
        if new_height == prev_height:
            print(f"  ✓ به ابتدای کانال رسیدیم (بعد از {i + 1} اسکرول)")
            return parse_messages(selenium_driver.page_source, parsed_sids)

    print(f"  ⚠ به سقف {MAX_SCROLLS} اسکرول رسیدیم")
    return parse_messages(selenium_driver.page_source, parsed_sids)


def fetch_new_posts(seen_sids: list[str]):
    setup_selenium_driver()
    try:
        print(f"\n🔄 بررسی کانال... ({time.strftime('%H:%M:%S')})")
        selenium_driver.get(CHANNEL_URL)

        # صبر تا لود شدن اولین پیام
        WebDriverWait(selenium_driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='MessageItem_messageWrapper']")
            )
        )
        time.sleep(2)  # فرصت برای رندر کامل

        page_posts = scroll_and_collect(seen_sids)

        # فیلتر پست‌های جدید
        new_posts = [p for p in page_posts if p.sid not in seen_sids]

        if new_posts:
            print(f"🆕 {len(new_posts)} پست جدید:")

        return reversed(new_posts)
    finally:
        if selenium_driver:
            selenium_driver.quit()
