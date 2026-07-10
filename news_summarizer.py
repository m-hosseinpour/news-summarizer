from model import NewsCategory

from open_ai_client_provider import open_ai_client, OPEN_AI_MODEL_NAME

SYSTEM_PROMPT = """تو یک خلاصه‌ساز حرفه‌ای اخبار فارسی هستی.
متنی که کاربر می‌فرسته شامل چندین خبر است که پشت سر هم قرار دارند.
وظیفه تو:
- یک خلاصه مختصر و مفید از همه اخبار بنویس
- هیچ نکته مهمی رو حذف نکن
- خروجی برای خواندن سریع مناسب باشه
- ساده و روان بنویس
- فقط خلاصه رو بنویس، توضیح اضافه نده"""


def summarize_news_posts(news_text: str) -> NewsCategory | None:
    news_text_strip = news_text.strip()
    if not news_text_strip:
        return None

    response = open_ai_client.chat.completions.create(
        model=OPEN_AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": news_text},
        ],
        temperature=0.3,  # کمتر = دقیق‌تر و خلاصه‌تر
        max_tokens=500,  # حداکثر طول پاسخ
        timeout=120,  # تایم‌اوت برای CPU ضعیف
    )
    return response.choices[0].message.content.strip()


# تست
if __name__ == "__main__":
    sample_news_text = ("بانک مرکزی نرخ سود سپرده‌ها را افزایش داد\n"
                        "پرسپولیس در دربی تهران استقلال را شکست داد\n"
                        "شرکت اپل از آیفون جدید خود رونمایی کرد\n"
                        "وزیر امور خارجه با همتای روس خود دیدار کرد\n"
                        "آلودگی هوای تهران مدارس را تعطیل کرد")
    print(summarize_news_posts(sample_news_text))
