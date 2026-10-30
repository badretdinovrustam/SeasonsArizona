import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Sticker
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- НАСТРОЙКИ ---
TOKEN = "9253941606:AAFzh0TadtF8G5VwtN2rJpkSoVv13ibPmJA"
TIMEZONE = ZoneInfo("Europe/Moscow")  # Часовой пояс для расчета понедельника

# --- ДАННЫЕ ---
SEASONS = [
    {"name": "По инфе", "sticker_id": "CAACAgIAAxkBAAEB9Y5m-1Z3x8qXhYJ5mQY4v1J2x5e2LwACVgADVp29C1n6yXg5n8fZLgQ"}, # Замените на реальный file_id стикера
    {"name": "Скорострелы", "sticker_id": "CAACAgIAAxkBAAEB9ZJm-1aGx9Kp5YJ5mQY4v1J2x5e2LwACWgADVp29C1n6yXg5n8fZLgQ"}, # Замените на реальный file_id стикера
    {"name": "Автогонки", "sticker_id": "CAACAgIAAxkBAAEB9ZRm-1aKx9Kp5YJ5mQY4v1J2x5e2LwACXgADVp29C1n6yXg5n8fZLgQ"}, # Замените на реальный file_id стикера
    {"name": "По новому", "sticker_id": "CAACAgIAAxkBAAEB9Zhm-1aOx9Kp5YJ5mQY4v1J2x5e2LwACYgADVp29C1n6yXg5n8fZLgQ"}, # Замените на реальный file_id стикера
    {"name": "Мотогонки", "sticker_id": "CAACAgIAAxkBAAEB9Zpm-1aTx9Kp5YJ5mQY4v1J2x5e2LwACZgADVp29C1n6yXg5n8fZLgQ"}, # Замените на реальный file_id стикера
]

SERVERS = {
    1: {"name": "[Phoenix]", "season": "По новому"},
    2: {"name": "[Tucson]", "season": "По инфе"},
    3: {"name": "[Scottdale]", "season": "Скорострелы"},
    4: {"name": "[Chandler]", "season": "По инфе"},
    5: {"name": "[Brainburg]", "season": "По новому"},
    6: {"name": "[Saint Rose]", "season": "По новому"},
    7: {"name": "[Mesa]", "season": "Автогонки"},
    8: {"name": "[Red-Rock]", "season": "Скорострелы"},
    9: {"name": "[Yuma]", "season": "По новому"},
    10: {"name": "[Surprise]", "season": "Скорострелы"},
    11: {"name": "[Prescott]", "season": "По инфе"},
    12: {"name": "[Glendale]", "season": "Скорострелы"},
    13: {"name": "[Kingman]", "season": "Мотогонки"},
    14: {"name": "[Winslow]", "season": "Автогонки"},
    15: {"name": "[Payson]", "season": "Автогонки"},
    16: {"name": "[Gilbert]", "season": "Мотогонки"},
    17: {"name": "[Show Low]", "season": "Мотогонки"},
    18: {"name": "[Casa-Grande]", "season": "Мотогонки"},
    19: {"name": "[Page]", "season": "По инфе"},
    20: {"name": "[Sun-City]", "season": "Автогонки"},
    21: {"name": "[Queen-Creek]", "season": "Мотогонки"},
    22: {"name": "[Sedona]", "season": "По инфе"},
    23: {"name": "[Holiday]", "season": "По новому"},
    24: {"name": "[Wednesday]", "season": "Скорострелы"},
    25: {"name": "[Yava]", "season": "Скорострелы"},
    26: {"name": "[Faraway]", "season": "Скорострелы"},
    27: {"name": "[Bumble Bee]", "season": "Мотогонки"},
    28: {"name": "[Christmas]", "season": "Скорострелы"},
    29: {"name": "[Mirage]", "season": "Скорострелы"},
    30: {"name": "[Love]", "season": "Скорострелы"},
    31: {"name": "[Drake]", "season": "Скорострелы"},
    32: {"name": "[Space]", "season": "Мотогонки"},
    33: {"name": "[Home]", "season": "По инфе"},
}

# --- ЛОГИКА ОБНОВЛЕНИЯ СЕЗОНОВ ---

def get_next_monday_midnight(now: datetime) -> datetime:
    days_ahead = (7 - now.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
    return next_monday.astimezone(TIMEZONE)

def update_server_seasons():
    for server_id in SERVERS:
        current_season_name = SERVERS[server_id]["season"]
        current_index = next((i for i, s in enumerate(SEASONS) if s["name"] == current_season_name), None)
        
        if current_index is not None:
            next_index = (current_index + 1) % len(SEASONS)
            SERVERS[server_id]["season"] = SEASONS[next_index]["name"]
    logging.info("Сезоны на всех серверах успешно обновлены.")

async def schedule_season_update(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(TIMEZONE)
    next_run_time = get_next_monday_midnight(now)
    run_time_local = next_run_time.astimezone(TIMEZONE)
    
    await context.job_queue.run_daily(
        callback=job_update_seasons,
        time=run_time_local.time(),
        days=(0,),  # 0 - это понедельник
        name="season_updater"
    )
    logging.info(f"Следующее обновление сезонов запланировано на: {run_time_local}")

async def job_update_seasons(context: ContextTypes.DEFAULT_TYPE):
    update_server_seasons()
    logging.info("Еженедельная задача: сезоны обновлены.")

# --- КОМАНДЫ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Показать сезоны", callback_data="show_seasons")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Я бот для отслеживания сезонов Arizona RP.", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_seasons":
        message_lines = ["🗺️ *Текущие сезоны на серверах Arizona RP:*", ""]
        for server_id in sorted(SERVERS.keys()):
            server = SERVERS[server_id]
            season_name = server["season"]
            season_info = next(s for s in SEASONS if s["name"] == season_name)
            
            line = f"{server['name']} — {season_name} {season_info['sticker_id']}"
            message_lines.append(line)
        
        text = "\n".join(message_lines)
        await query.message.edit_text(text, parse_mode="Markdown")

# --- ЗАПУСК ---

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    app.job_queue.run_once(schedule_season_update, 1)

    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
