import os
import telebot
from flask import Flask, request
import threading
import json

TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(TOKEN)

# Загрузка базы данных
with open('database.json', 'r') as f:
    db = json.load(f)

all_keys = {key: item for item in db for key in item['keys']}

# Логика бота (та же)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me a keyword (e.g. 'appendix')")

@bot.message_handler(func=lambda m: True)
def handle_keywords(message):
    text = message.text.lower()
    if text in all_keys:
        op_data = all_keys[text]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Professional', 'Normal')
        msg = bot.send_message(message.chat.id, f"Mode for '{op_data['name']}'?", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: send_operation_info(m, op_data))
    else:
        bot.reply_to(message, "❌ Operation not found.")

def send_operation_info(message, operation):
    mode = message.text.lower()
    if mode not in ['professional', 'normal']:
        bot.reply_to(message, "❌ Invalid mode.")
        return

    name = operation['name']
    summary = operation['modes'][mode]
    steps = operation['steps']

    bot.send_message(message.chat.id, f"📋 *{name}* — {mode.capitalize()} mode:\n\n📝 {summary}", parse_mode='Markdown')
    for step in steps:
        bot.send_message(message.chat.id, f"🔹 *{step['name']}*\n{step['description'][mode]}", parse_mode='Markdown')

# Flask сервер для keep-alive
app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running.'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_bot():
    bot.polling()

# Запускаем Flask и бота параллельно
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_bot()
