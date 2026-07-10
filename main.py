import time

from bale_bot_message_sender import send_message
from model import NewsPost, NewsCategory
from news_collector import fetch_new_posts
from news_summarizer import summarize_news_posts

POLL_INTERVAL = 120  # ثانیه
SUMMARIZE_BATCH = 3
BALE_POST_LINK_TEMPLATE = "https://ble.ir/akharinkhabar/{post_id}"
IMPORTANT_CATEGORIES: list[NewsCategory] = [NewsCategory.WAR_CONFLICT, NewsCategory.POLITICS, NewsCategory.ECONOMY,
                                            NewsCategory.SCIENCE_TECH, NewsCategory.UNKNOWN]


def summarize_in_batches(news_posts: list[NewsPost]):
    summary_list = []
    while news_posts:
        batch = news_posts[:SUMMARIZE_BATCH]

        concat_text = "\n\n***\n\n".join([p.text for p in batch])
        summary = summarize_news_posts(concat_text)
        summary += "\n\n\n"
        for p in batch:
            separator_index = p.sid.index("-", 1)
            post_id = p.sid[:separator_index] + "/" + p.sid[separator_index + 1:]
            summary += BALE_POST_LINK_TEMPLATE.format(post_id=post_id) + "\n"

        print(summary)
        print('=' * 50)
        summary_list.append(summary)
        news_posts = news_posts[SUMMARIZE_BATCH:]
    return summary_list


def send_summary_list(summary_list: list[str]):
    for summary in summary_list:
        send_message(summary)


def monitor_channel():
    while True:
        try:
            fetch_new_posts()

        except Exception as e:
            print(f"⚠ خطا: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    news_posts = fetch_new_posts()
    important_posts = [p for p in news_posts if p.category and p.category in IMPORTANT_CATEGORIES]
    summary_list = summarize_in_batches(important_posts)
    send_summary_list(summary_list)
