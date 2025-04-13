import os
import openai
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from collections import deque

# 设置环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 创建一个字典来存储每个用户的对话历史
user_context = {}

# 处理用户消息
def handle_message(update, context):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # 获取当前用户的对话历史，若没有则初始化
    if user_id not in user_context:
        user_context[user_id] = deque(maxlen=5)  # 保留最近 5 条消息

    # 将用户输入加入对话历史
    user_context[user_id].append({"role": "user", "content": user_input})

    # 获取当前的对话上下文
    messages = list(user_context[user_id])

    # 调用 OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 或 gpt-3.5-turbo
        messages=messages
    )

    reply = response['choices'][0]['message']['content']

    # 回复用户并将 Bot 的回复加入历史
    update.message.reply_text(reply)
    user_context[user_id].append({"role": "assistant", "content": reply})

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()

