import asyncio
import os
import re
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
        
        # Универсальный поиск карточек
        items = []
        for div in soup.find_all("div", class_=re.compile("iva-item")):
            try:
                title = div.find("h3", class_=re.compile("title"))
                price = div.find("span", class_=re.compile("price"))
                link = div.find("a", class_=re.compile("link"))
                if title and price and link:
                    items.append({
                        "name": title.text.strip(),
                        "price": price.text.strip(),
                        "url": "https://www.avito.ru" + link.get("href"),
                        "color": "🟢"
                    })
            except:
                continue
        
        # Если ничего не нашли — пробуем запасной вариант
        if not items:
            for item in soup.find_all("div", attrs={"data-marker": "item"}):
                try:
                    title = item.find("h3", attrs={"itemprop": "name"})
                    price = item.find("span", attrs={"itemprop": "price"})
                    link = item.find("a", attrs={"itemprop": "url"})
                    if title and price and link:
                        items.append({
                            "name": title.text.strip(),
                            "price": price.get("content", price.text.strip()),
                            "url": "https://www.avito.ru" + link.get("href"),
                            "color": "🟢"
                        })
                except:
                    continue
        
        return items[:3]
    except Exception as e:
        print("Ошибка парсинга:", e)
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
        await msg.answer("😕 Ничего не нашёл. Попробуй другое название или добавь бренд.")
        return
    for item in items:
        text = f"{item['color']} *{item['name']}*\n💰 {item['price']}\n🔗 [Ссылка]({item['url']})"
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




