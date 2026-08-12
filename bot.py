import asyncio
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_avito_mobile(query):
    """Парсинг мобильной версии Avito (не блокируется)"""
    url = f"https://m.avito.ru/rossiya?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="item", limit=5)
        results = []
        for item in items:
            title = item.find("div", class_="title")
            price = item.find("div", class_="price")
            link = item.find("a", class_="link")
            if title and price and link:
                results.append({
                    "name": title.text.strip(),
                    "price": price.text.strip(),
                    "url": "https://m.avito.ru" + link.get("href"),
                    "color": "🟢"
                })
        return results[:3]
    except Exception as e:
        print("Ошибка мобильного Avito:", e)
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
    await msg.answer("🔍 Ищу дешёвые варианты...")
    items = search_avito_mobile(query)
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
