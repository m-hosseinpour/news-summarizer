import time

from model import NewsPost, NewsCategory
from news_collector import fetch_new_posts
from news_summarizer import summarize_news_posts

POLL_INTERVAL = 120  # ثانیه
SUMMARIZE_BATCH = 5
IMPORTANT_CATEGORIES: list[NewsCategory] = [NewsCategory.WAR_CONFLICT, NewsCategory.POLITICS, NewsCategory.ECONOMY,
                                            NewsCategory.SCIENCE_TECH, NewsCategory.UNKNOWN]


def summarize_in_batches(news_posts: list[NewsPost]):
    summary_list = []
    while news_posts:
        batch = news_posts[:5]
        concat_text = "\n".join([p.text for p in batch])
        summary = summarize_news_posts(concat_text)
        print(summary)
        print("+" * 40)
        summary_list.append(summary)
        news_posts = news_posts[5:]
    return summary_list


def send_summary_list(summary_list: list[str]):
    pass


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
