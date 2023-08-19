import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# 봇 토큰을 초기화하고 Updater를 생성합니다
TOKEN = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# 메시지를 처리할 함수를 정의합니다
def message_handler(update, context):
    message_text = update.message.text

    # 메시지가 변수를 업데이트하는 명령인지 확인합니다
    if message_text.startswith('/update_variable'):
        new_value = message_text.split()[1]  # 메시지에서 새 값을 추출합니다
        # 특정 변수를 new_value로 업데이트합니다

        update.message.reply_text(f"변수가 {new_value}로 업데이트되었습니다")

# 메시지 핸들러를 등록합니다
message_handler = MessageHandler(Filters.text & ~Filters.command, message_handler)
dispatcher.add_handler(message_handler)

# 봇을 시작합니다
updater.start_polling()
updater.idle()
