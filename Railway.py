import os
from telegram.ext import Updater

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

# 获取 Railway 提供的端口
port = os.getenv('PORT', 5000)  # 如果没有 PORT 环境变量，则使用默认端口 5000

# 启动 bot
updater.start_polling()
