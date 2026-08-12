from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import re
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def parse_avito(query):
    url = f"https://www.avito.ru/rossiya?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
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

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("👟 GreenTag — модный сканер цен!\n\nНапиши название вещи (например, 'кроссовки Nike') и я найду дешёвые варианты с рейтингом продавца.\n\nЗелёный 🟢 — можно доверять")

@dp.message_handler()
async def search(message: types.Message):
    query = message.text
    await message.answer("🔍 Ищу лучшие цены...")
    results = parse_avito(query)
    if not results:
        await message.answer("😕 Ничего не нашёл. Попробуй другое название.")
        return
    for item in results:
        text = f"{item['color']} *{item['name']}*\n💰 {item['price']}\n🔗 [Перейти к объявлению]({item['url']})"
        await message.answer(text, parse_mode="Markdown")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)