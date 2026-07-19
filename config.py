import os

from dotenv import load_dotenv

load_dotenv()

CHANNEL_URL = os.getenv("CHANNEL_URL", "https://ble.ir/s/akharinkhabar")
MAX_SCROLLS = int(os.getenv("MAX_SCROLLS", "500"))
SCROLL_PAUSE = int(os.getenv("SCROLL_PAUSE", "2"))

BALE_BOT_TOKEN = os.getenv("BALE_BOT_TOKEN")
BALE_BOT_CHAT_ID = int(os.getenv("BALE_BOT_CHAT_ID"))

SUMMARIZE_BATCH = int(os.getenv("SUMMARIZE_BATCH", "3"))

OPEN_AI_MODEL_NAME = os.getenv("OPEN_AI_MODEL_NAME", "qwen3:4b-instruct")
OPEN_AI_BASE_URL = os.getenv("OPEN_AI_BASE_URL", "http://localhost:11434/v1")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY", "ollama")
