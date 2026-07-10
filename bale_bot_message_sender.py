import requests

TOKEN = ""
CHAT_ID = 0

def send_message(text):
    resp = requests.post(
        f"https://tapi.bale.ai/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
        },
    )
    print(resp.json())
