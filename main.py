import time

from bale_bot_message_sender import send_message
from config import SUMMARIZE_BATCH
from model import NewsPost, NewsCategory
from news_collector import fetch_new_posts
from news_summarizer import summarize_and_post_links
from utils import load_posts, save_posts

POLL_INTERVAL = 120  # ثانیه
IMPORTANT_CATEGORIES: list[NewsCategory] = [NewsCategory.WAR_CONFLICT, NewsCategory.POLITICS, NewsCategory.ECONOMY,
                                            NewsCategory.SCIENCE_TECH, NewsCategory.UNKNOWN]


def monitor_channel(seen_sids):
    while True:
        try:
            fetch_new_posts(seen_sids)

        except Exception as e:
            print(f"⚠ خطا: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    all_posts: list[NewsPost] = load_posts()
    seen_sids = {p.sid for p in all_posts}

    important_batch = []
    for new_post in fetch_new_posts(seen_sids):
        all_posts.append(new_post)
        all_posts = all_posts[-1000:]

        if new_post.category and new_post.category in IMPORTANT_CATEGORIES:
            important_batch.append(new_post)

        if len(important_batch) >= SUMMARIZE_BATCH:
            summary = summarize_and_post_links(important_batch)
            send_message(summary)

            important_batch = []
            save_posts(all_posts)

    if important_batch:
        summary = summarize_and_post_links(important_batch)
        send_message(summary)

    save_posts(all_posts)
