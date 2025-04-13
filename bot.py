import os
import openai
import telegram
from telegram.ext import Updater, MessageHandler, Filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def handle_message(update, context):
    user_input = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 或 gpt-3.5-turbo
        messages=[{"role": "user", "content": user_input}]
    )
    reply = response['choices'][0]['message']['content']
    update.message.reply_text(reply)

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
