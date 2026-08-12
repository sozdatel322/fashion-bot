import asyncio
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def parse_avito(query):
    url = f"https://www.avito.ru/rossiya?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="iva-item-body", limit=3)
        results = []
        for item in items:
            title = item.find("h3", class_="title-root")
            price = item.find("span", class_="price-text")
            link = item.find("a", class_="link-link")
            if title and price and link:
                results.append({
                    "name": title.text.strip(),
                    "price": price.text.strip(),
                    "url": "https://www.avito.ru" + link.get("href"),
                    "color": "🟢"
                })
        return results
    except:
        return []

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("👟 GreenTag — ищу дешёвые аналоги!\nНапиши что ищешь, например: кроссовки Nike")

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу...")
    items = parse_avito(query)
    if not items:
        await msg.answer("😕 Ничего не нашёл. Попробуй другое.")
        return
    for item in items:
        text = f"{item['color']} *{item['name']}*\n💰 {item['price']}\n🔗 [Ссылка]({item['url']})"
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




