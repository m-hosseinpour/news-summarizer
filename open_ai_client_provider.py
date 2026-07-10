from openai import OpenAI

OPEN_AI_MODEL_NAME = "qwen3:4b-instruct"

open_ai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
