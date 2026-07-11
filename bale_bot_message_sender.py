import requests

from config import BALE_BOT_TOKEN, BALE_BOT_CHAT_ID

def send_message(text):
    resp = requests.post(
        f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": BALE_BOT_CHAT_ID,
            "text": text,
        },
    )
    print(resp.json())
