import asyncio
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
SCRAPINGBEE_KEY = "R2FMHBX7NRGR3TONYJIDQRVDP91CWRAKKDIHU29JETDH808SIVYZWY6ERXNLZ5IRFUF879HLV4XAMUNB"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_avito(query):
    """Парсинг Avito через ScrapingBee"""
    url = f"https://www.avito.ru/rossiya?q={query}"
    params = {
        "api_key": SCRAPINGBEE_KEY,
        "url": url,
        "render_js": "false",
        "wait": "2000"
    }
    try:
        r = requests.get("https://app.scrapingbee.com/api/v1/", params=params, timeout=30)
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
    except Exception as e:
        print("Ошибка ScrapingBee:", e)
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
    items = search_avito(query)
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
