import json
import os
from pathlib import Path

from pydantic import TypeAdapter
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from model import NewsPost

POSTS_FILE = 'news_posts.json'

NewsPostList = TypeAdapter(list[NewsPost])


def load_posts() -> list[NewsPost]:
    if os.path.exists(POSTS_FILE):
        try:
            return NewsPostList.validate_json(Path(POSTS_FILE).read_bytes())
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ خطا در خواندن فایل: {e} — با لیست خالی شروع می‌شود")
    return []


def save_posts(news_posts: list[NewsPost]):
    try:
        data: bytes = NewsPostList.dump_json(news_posts, indent=2)
        Path(POSTS_FILE).write_bytes(data)
    except IOError as e:
        print(f"⚠ خطا در نوشتن فایل: {e}")
