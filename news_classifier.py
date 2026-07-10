from model import NewsCategory

from open_ai_client_provider import open_ai_client, OPEN_AI_MODEL_NAME

# پرامپت سیستمی (بهینه برای مدل‌های ضعیف)
# نکته: برای مدل‌های ضعیف، پرامپت باید کوتاه، ساختارمند و با مثال باشد
SYSTEM_PROMPT = """You are a news classifier. Read the Persian news text and output EXACTLY ONE category label from the list below. Output the label in English, exactly as written.

STEP 1 — Check war first:
If the text mentions war, military attack, missile/drone strike, bombing, armed clash, invasion, or military operation → answer: war_conflict
(This rule wins over ALL other categories, even if the news is about a foreign country or politics.)

STEP 2 — Check advertisement:
If the text is promotional content, an ad, or marketing material — e.g., promoting a product/service/brand, discount and sale announcements, calls to buy or register, promotional links or contact numbers, sponsored content (رپورتاژ آگهی) → answer: advertisement
(Note: news *about* the advertising industry or a company's marketing news is NOT advertisement — classify it by its actual topic, e.g., economy.)

STEP 3 — If neither, pick one:
- politics: government, elections, parliament, diplomacy, officials
- economy: money, market, stocks, currency, gold, oil, inflation, trade
- social: health, education, family, environment, accidents, crime
- sports: football, athletes, matches, tournaments
- culture_art: cinema, music, books, art, tourism, celebrities
- science_tech: technology, AI, phones, internet, space, science
- unknown: none of the above

OUTPUT FORMAT:
- Output ONLY the English label. No explanation. No extra words. No punctuation.

Examples:

Text: قیمت دلار امروز کاهش یافت
Answer: economy

Text: فیلم جدید اصغر فرهادی اکران شد
Answer: culture_art

Text: حمله موشکی به شهر باعث تخریب ساختمان‌ها شد
Answer: war_conflict

Text: درگیری مسلحانه در مرز دو کشور همسایه شدت گرفت
Answer: war_conflict

Text: یک مقام آمریکایی به CNN گفته است که ایالات متحده در حال حاضر مشغول انجام حملات نظامی نیست
Answer: war_conflict

Text: وزیر بهداشت از افزایش ظرفیت بیمارستان‌ها خبر داد
Answer: social

Text: فروش ویژه لوازم خانگی با ۵۰ درصد تخفیف! همین حالا خرید کنید
Answer: advertisement

Text: بهترین دوره آموزش زبان انگلیسی؛ برای ثبت‌نام با شماره زیر تماس بگیرید
Answer: advertisement

Text: با بیمه عمر شرکت ما، آینده خانواده‌تان را تضمین کنید
Answer: advertisement"""


def classify_news(news_text: str) -> NewsCategory | None:
    news_text_strip = news_text.strip()
    if not news_text_strip:
        return None

    """متن خبر را دریافت و دسته‌بندی آن را برمی‌گرداند."""
    response = open_ai_client.chat.completions.create(
        model=OPEN_AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Text: {news_text_strip}\nAnswer:"},
        ],
        temperature=0.0,  # حداکثر قطعیت، مهم برای classification
        max_tokens=10,  # فقط نام دسته لازم است
    )

    raw_output = response.choices[0].message.content.strip()
    return _parse_category(raw_output)


def _parse_category(raw_output: str) -> NewsCategory:
    """خروجی خام مدل را به Enum تبدیل می‌کند (با تحمل خطای مدل‌های ضعیف)."""
    # تطابق دقیق
    for category in NewsCategory:
        if category.value == raw_output:
            return category

    # تطابق جزئی (مدل‌های ضعیف گاهی کلمه اضافه می‌گویند)
    for category in NewsCategory:
        if category == NewsCategory.UNKNOWN:
            continue
        if category.value in raw_output:
            return category

    return NewsCategory.UNKNOWN


# تست
if __name__ == "__main__":
    sample_news = [
        "بانک مرکزی نرخ سود سپرده‌ها را افزایش داد",
        "پرسپولیس در دربی تهران استقلال را شکست داد",
        "شرکت اپل از آیفون جدید خود رونمایی کرد",
        "وزیر امور خارجه با همتای روس خود دیدار کرد",
        "آلودگی هوای تهران مدارس را تعطیل کرد",
    ]

    for news in sample_news:
        category = classify_news(news)
        print(f"📰 {news}\n   ➜ دسته: {category.value}\n")
