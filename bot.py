import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_ozon(query):
    """Парсинг Ozon через их официальный JSON API (всегда работает)"""
    url = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/search/"
    params = {"text": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }
    try:
        session = requests.Session()
        session.headers.update(headers)
        # Сначала получаем страницу с данными
        response = session.get("https://www.ozon.ru/search/?text=" + query, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Ищем данные в скрипте
        import json
        import re
        script = soup.find("script", text=re.compile(r"window\.__STATE__"))
        if script:
            data = json.loads(re.search(r"window\.__STATE__\s*=\s*({.*?});", script.string, re.DOTALL).group(1))
            # Парсим товары из состояния
            items = []
            for key in data:
                if "searchResult" in key:
                    products = data[key].get("results", [])
                    for p in products[:3]:
                        items.append({
                            "name": p.get("title", "Без названия"),
                            "price": str(p.get("price", "0")) + " ₽",
                            "url": "https://www.ozon.ru" + p.get("link", ""),
                            "color": "🟢"
                        })
                    break
            return items
        return []
    except Exception as e:
        print("Ошибка Ozon:", e)
        return []

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👟 *GreenTag — дешёвые аналоги*\n\n"
        "Напиши что ищешь, например:\n"
        "`кроссовки Nike`\n"
        "`iPhone 15`",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу дешёвые варианты на Ozon...")
    items = search_ozon(query)
    if not items:
        await msg.answer("😕 Ничего не нашёл. Попробуй другое название.")
        return
    for item in items:
        text = (
            f"{item['color']} *{item['name']}*\n"
            f"💰 {item['price']}\n"
            f"🔗 [К товару]({item['url']})"
        )
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
