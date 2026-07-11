from openai import OpenAI

from config import OPEN_AI_BASE_URL, OPEN_AI_API_KEY

open_ai_client = OpenAI(
    base_url=OPEN_AI_BASE_URL,
    api_key=OPEN_AI_API_KEY,
)
