import os
import openai
import telegram
from telegram.ext import Updater, MessageHandler, Filters

TELEGRAM_TOKEN = os.getenv(7841546368:AAHw8uNBJAb2BqOb9Rq1b9v7xO2659VeG1I)
OPENAI_API_KEY = os.getenv(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)

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
