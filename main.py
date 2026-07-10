import time

from bale_bot_message_sender import send_message
from model import NewsPost, NewsCategory
from news_collector import fetch_new_posts
from news_summarizer import summarize_news_posts
from utils import load_posts, save_posts

POLL_INTERVAL = 120  # ثانیه
SUMMARIZE_BATCH = 3
BALE_POST_LINK_TEMPLATE = "https://ble.ir/akharinkhabar/{post_id}"
IMPORTANT_CATEGORIES: list[NewsCategory] = [NewsCategory.WAR_CONFLICT, NewsCategory.POLITICS, NewsCategory.ECONOMY,
                                            NewsCategory.SCIENCE_TECH, NewsCategory.UNKNOWN]


def summarize_and_send(important_batch: list[NewsPost]):
    concat_text = "\n\n***\n\n".join([p.text for p in important_batch])
    summary = summarize_news_posts(concat_text)
    summary += "\n\n\n"
    for p in important_batch:
        separator_index = p.sid.index("-", 1)
        post_id = p.sid[:separator_index] + "/" + p.sid[separator_index + 1:]
        summary += BALE_POST_LINK_TEMPLATE.format(post_id=post_id) + "\n"

    print('=' * 50 + ' SUMMARY-TO-SEND ' + '=' * 50)
    print(summary)
    send_message(summary)


def monitor_channel(seen_sids):
    while True:
        try:
            fetch_new_posts(seen_sids)

        except Exception as e:
            print(f"⚠ خطا: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    # خواندن پست‌های قبلی از فایل
    all_posts: list[NewsPost] = load_posts()
    seen_sids = {p.sid for p in all_posts}

    important_batch = []
    for new_post in fetch_new_posts(seen_sids):
        if new_post.category and new_post.category in IMPORTANT_CATEGORIES:
            important_batch.append(new_post)

        if len(important_batch) >= SUMMARIZE_BATCH:
            summarize_and_send(important_batch)
            important_batch = []

        all_posts.append(new_post)
        all_posts = all_posts[-1000:]
        save_posts(all_posts)

    if important_batch:
        summarize_and_send(important_batch)
