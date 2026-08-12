import asyncio
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция поиска на Wildberries
async def search_wildberries(query):
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("div", class_="product-card", limit=3)
                results = []
                for item in items:
                    name_tag = item.find("span", class_="product-name")
                    price_tag = item.find("span", class_="price-currency")
                    link_tag = item.find("a", class_="product-card__link")
                    if name_tag and price_tag and link_tag:
                        results.append({
                            "name": name_tag.text.strip(),
                            "price": price_tag.text.strip() + " ₽",
                            "url": "https://www.wildberries.ru" + link_tag.get("href"),
                            "color": "🟢"
                        })
                return results[:3]
    except Exception as e:
        print("Ошибка WB:", e)
        return []

# Функция поиска на Ozon (запасной вариант)
async def search_ozon(query):
    url = f"https://www.ozon.ru/search/?text={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("div", class_="tile-hover-target", limit=3)
                results = []
                for item in items:
                    name_tag = item.find("span", class_="tsBody500Medium")
                    price_tag = item.find("span", class_="price-currency")
                    link_tag = item.find("a", class_="tile-hover-target")
                    if name_tag and price_tag and link_tag:
                        results.append({
                            "name": name_tag.text.strip(),
                            "price": price_tag.text.strip() + " ₽",
                            "url": "https://www.ozon.ru" + link_tag.get("href"),
                            "color": "🟢"
                        })
                return results[:3]
    except Exception as e:
        print("Ошибка Ozon:", e)
        return []

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👟 *GreenTag — модный сканер цен!*\n\n"
        "Напиши название вещи, например:\n"
        "`кроссовки Nike`\n"
        "`пальто зимнее`\n"
        "`iPhone 15`\n\n"
        "🟢 Зелёный — проверенный продавец\n"
        "🟡 Жёлтый — средний рейтинг\n"
        "🔴 Красный — осторожно!",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу на Wildberries...")
    
    items = await search_wildberries(query)
    
    # Если на WB ничего нет — пробуем Ozon
    if not items:
        await msg.answer("🔍 Ищу на Ozon...")
        items = await search_ozon(query)
    
    if not items:
        await msg.answer("😕 Ничего не нашёл. Попробуй другое название или бренд.")
        return
    
    for item in items:
        te


xt = (
            f"{item['color']} *{item['name']}*\n"
            f"💰 {item['price']}\n"
            f"🔗 [Перейти к товару]({item['url']})"
        )
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



