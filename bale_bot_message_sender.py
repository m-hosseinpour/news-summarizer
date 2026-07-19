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
    resp_json = resp.json()
    print(resp_json)
    if (not resp_json["ok"]):
        raise Exception("Error sending message with bale bot")
