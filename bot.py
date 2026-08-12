import asyncio
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def parse_wildberries(query):
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="product-card", limit=3)
        results = []
        for item in items:
            name = item.find("span", class_="product-name")
            price = item.find("span", class_="price-currency")
            link = item.find("a", class_="product-card__link")
            if name and price and link:
                results.append({
                    "name": name.text.strip(),
                    "price": price.text.strip() + " ₽",
                    "url": "https://www.wildberries.ru" + link.get("href"),
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
    await msg.answer("🔍 Ищу на Wildberries...")
    items = parse_wildberries(query)
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




