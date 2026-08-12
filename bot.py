import asyncio
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_google_shopping(query):
    """Поиск товаров через Google Shopping (не блокируется)"""
    url = f"https://www.google.com/search?q={query}&tbm=shop"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="sh-dgr__grid-result", limit=5)
        results = []
        for item in items:
            title = item.find("h3", class_="tAxDx")
            price = item.find("span", class_="a8Pemb")
            link = item.find("a", class_="Lq5OHe")
            if title and price and link:
                results.append({
                    "name": title.text.strip(),
                    "price": price.text.strip(),
                    "url": link.get("href"),
                    "color": "🟢"
                })
        return results[:3]
    except Exception as e:
        print("Ошибка Google:", e)
        return []

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👟 *GreenTag — дешёвые аналоги*\n\n"
        "Напиши что ищешь, например:\n"
        "`кроссовки Nike`\n"
        "`iPhone 15`\n"
        "`пальто зимнее`",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу дешёвые варианты...")
    items = search_google_shopping(query)
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
