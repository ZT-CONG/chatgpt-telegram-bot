import os
import openai
from collections import deque
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update

# 设置环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 存储每个用户的对话历史
user_context = {}

# 存储用户角色的字典（管理员 / 普通用户）
user_roles = {}

# 初始化 Updater
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# 处理用户消息（包括文本消息）
def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # 如果用户没有上下文，初始化对话历史
    if user_id not in user_context:
        user_context[user_id] = deque(maxlen=5)  # 保留最近的 5 条消息

    # 将用户输入加入对话历史
    user_context[user_id].append({"role": "user", "content": user_input})

    # 获取当前的对话上下文
    messages = list(user_context[user_id])

    # 调用 OpenAI API 获取回复
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 或 gpt-3.5-turbo
        messages=messages
    )

    reply = response['choices'][0]['message']['content']

    # 回复用户并将 Bot 的回复加入历史
    update.message.reply_text(reply)
    user_context[user_id].append({"role": "assistant", "content": reply})

# 处理语音消息
def handle_voice(update: Update, context):
    user_id = update.message.from_user.id
    voice_file = update.message.voice.get_file()

    # 下载语音文件
    voice_file.download('voice.ogg')

    # 使用 OpenAI Whisper 进行语音转文字
    with open('voice.ogg', 'rb') as f:
        transcription = openai.Audio.transcribe(model="whisper-1", file=f)
    
    # 获取转写的文本
    user_input = transcription['text']

    # 生成 ChatGPT 回复
    reply = get_chatgpt_reply(user_input)

    # 回复用户
    update.message.reply_text(reply)

# 处理图片消息
def handle_photo(update: Update, context):
    user_id = update.message.from_user.id
    photo_file = update.message.photo[-1].get_file()

    # 下载图片文件
    photo_file.download('photo.jpg')

    # 使用 OpenAI Vision 或其他 API 来处理图片（此处假设 OpenAI Vision）
    with open('photo.jpg', 'rb') as f:
        image_description = openai.Image.create(
            model="dall-e-2",  # 适用的图像分析模型
            prompt="Describe the content of this image",
            file=f
        )

    # 获取图片分析的结果
    image_caption = image_description['choices'][0]['text']
    
    # 回复用户图片分析结果
    update.message.reply_text(image_caption)

# 生成 ChatGPT 回复
def get_chatgpt_reply(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 或 gpt-3.5-turbo
        messages=[{"role": "user", "content": user_input}]
    )
    return response['choices'][0]['message']['content']

# 设置用户角色（管理员或普通用户）
def set_role(update: Update, context):
    user_id = update.message.from_user.id
    role = context.args[0]  # 从命令参数中获取角色
    user_roles[user_id] = role
    update.message.reply_text(f"你的角色已设置为 {role}")

# 判断是否为管理员
def is_admin(user_id):
    return user_roles.get(user_id) == "admin"

# 处理命令（例如管理员可以发送特定指令）
def handle_admin_commands(update: Update, context):
    user_id = update.message.from_user.id

    if is_admin(user_id):
        update.message.reply_text("你好，管理员！")
    else:
        update.message.reply_text("你好，普通用户！")

# 添加角色设置命令
dispatcher.add_handler(CommandHandler("setrole", set_role))

# 添加处理文本消息
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# 添加处理语音消息
dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))

# 添加处理图片消息
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

# 添加处理管理员命令
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_admin_commands))

# 启动 Bot
updater.start_polling()
