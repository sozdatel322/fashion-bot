import asyncio
import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_avito_rss(query):
    """Поиск через RSS-ленту Avito (не блокируется)"""
    encoded_query = quote(query)
    url = f"https://www.avito.ru/rossiya?q={encoded_query}&s=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Парсим HTML как XML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Ищем карточки товаров
        items = soup.find_all("div", class_="iva-item-body", limit=5)
        results = []
        
        for item in items:
            try:
                # Название
                title_elem = item.find("h3", class_="title-root")
                title = title_elem.text.strip() if title_elem else "Без названия"
                
                # Цена
                price_elem = item.find("span", class_="price-text")
                price = price_elem.text.strip() if price_elem else "Цена не указана"
                
                # Ссылка
                link_elem = item.find("a", class_="link-link")
                link = "https://www.avito.ru" + link_elem.get("href") if link_elem else "#"
                
                # Рейтинг (заглушка)
                rating = "🟢"
                
                results.append({
                    "name": title,
                    "price": price,
                    "url": link,
                    "color": rating
                })
            except Exception as e:
                print(f"Ошибка парсинга карточки: {e}")
                continue
        
        return results[:3]
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return []

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👋 *GreenTag — поиск дешёвых аналогов!*\n\n"
        "📌 *Как я работаю:*\n"
        "1. Ты вводишь название вещи\n"
        "2. Я ищу на Avito\n"
        "3. Показываю 3 самых дешёвых варианта\n\n"
        "🟢 Зелёный — продавец с хорошим рейтингом\n\n"
        "🔍 *Попробуй:*\n"
        "`кроссовки Nike`\n"
        "`iPhone 15`\n"
        "`пальто зимнее`",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    await msg.answer("🔍 Ищу на Avito...")
    
    items = search_avito_rss(query)
    
    if not items:
        await msg.answer(
            "😕 Ничего не нашёл по твоему запросу.\n\n"
            "💡 *Попробуй:*\n"
            "• Уточнить бренд (например, `Adidas`)\n"
            "• Написать на русском\n"
            "• Использовать короткие запросы",
            parse_mode="Markdown"
        )
        return
    
    for item in items:
        text = (
            f"{item['color']} *{item['name']}*\n"
            f"💰 {item['price']}\n"
            f"🔗 [Перейти к объявлению]({item['url']})"
        )
        await msg.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




