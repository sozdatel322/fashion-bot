import asyncio
import os
import requests
import json
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_ozon(query):
    """Поиск на Ozon через их открытый JSON-фид"""
    url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/search/?text={query}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        items = data.get("layout", [])
        results = []
        for block in items:
            if "searchResults" in str(block):
                products = block.get("searchResults", {}).get("items", [])[:3]
                for p in products:
                    results.append({
                        "name": p.get("title", "Без названия"),
                        "price": f"{p.get('price', '0')} ₽",
                        "url": "https://www.ozon.ru" + p.get("link", ""),
                        "color": "🟢"
                    })
                break
        return results
    except:
        return []

def search_yandex(query):
    """Поиск на Яндекс.Маркет через RSS"""
    url = f"https://market.yandex.ru/search?text={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="organic", limit=3)
        results = []
        for item in items:
            title = item.find("h3", class_="organic__title")
            price = item.find("span", class_="price")
            link = item.find("a", class_="organic__url")
            if title and price and link:
                results.append({
                    "name": title.text.strip(),
                    "price": price.text.strip(),
                    "url": link.get("href"),
                    "color": "🟢"
                })
        return results
    except:
        return []

def search_avito_rss(query):
    """Поиск на Avito через RSS"""
    url = f"https://www.avito.ru/rossiya?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
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
    await msg.answer(
        "👟 *GreenTag — поиск дешёвых аналогов!*\n\n"
        "Напиши название вещи, например:\n"
        "`кроссовки Nike`\n"
        "`iPhone 15`\n"
        "`пальто зимнее`\n\n"
        "Я покажу 3 самых дешёвых варианта с Ozon, Яндекс.Маркет и Avito.",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу на Ozon...")
    items = search_ozon(query)
    
    if not items:
        await msg.answer("🔍 Ищу на Яндекс.Маркет...")
        items = search_yandex(query)
    
    if not items:
        await msg.answer("🔍 Ищу на Avito...")
        items = search_avito_rss(query)
    
    if not items:
        await msg.answer(
            "😕 Ничего не нашёл. Попробуй другое название.\n"
            "Например: `Adidas кроссовки`",
            parse_mode="Markdown"
        )
        return
    
    for item in items:


text = (
            f"{item['color']} *{item['name']}*\n"
            f"💰 {item['price']}\n"
            f"🔗 [Перейти к товару]({item['url']})"
        )
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
