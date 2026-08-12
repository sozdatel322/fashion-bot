import asyncio
import os
from urllib.parse import quote
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция генерации ссылок
def generate_links(query):
    encoded = quote(query)
    return {
        "avito": f"https://www.avito.ru/rossiya?q={encoded}",
        "wildberries": f"https://www.wildberries.ru/catalog/0/search.aspx?search={encoded}",
        "ozon": f"https://www.ozon.ru/search/?text={encoded}",
        "yandex": f"https://market.yandex.ru/search?text={encoded}"
    }

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👋 *GreenTag — умный поиск дешёвых аналогов!*\n\n"
        "📌 *Как я работаю:*\n"
        "1. Ты вводишь название вещи\n"
        "2. Я даю ссылки на поиск на 4 маркетплейсах\n"
        "3. Ты переходишь и выбираешь лучшую цену\n\n"
        "🔍 *Попробуй:*\n"
        "`кроссовки Nike`\n"
        "`iPhone 15`\n"
        "`пальто зимнее`",
        parse_mode="Markdown"
    )

@dp.message()
async def search(msg: types.Message):
    query = msg.text
    links = generate_links(query)
    
    text = (
        f"🔍 *Результаты по запросу:*\n"
        f"`{query}`\n\n"
        f"🛒 *Ссылки для поиска:*\n"
        f"• [Avito]({links['avito']})\n"
        f"• [Wildberries]({links['wildberries']})\n"
        f"• [Ozon]({links['ozon']})\n"
        f"• [Яндекс.Маркет]({links['yandex']})\n\n"
        f"💡 Нажми на ссылку → выбери самую дешёвую цену!"
    )
    
    await msg.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




