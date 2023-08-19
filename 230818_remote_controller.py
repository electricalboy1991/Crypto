
# cmd_handler_bot.py
from telegram.ext import Updater
from telegram.ext import CommandHandler

BOT_TOKEN = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="작업을 시작합니다.")


def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="작업을 중단합니다.")


def zigbang(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="[{}] 주변 매물을 수집합니다.".format(context.args[0]))


start_handler = CommandHandler('start', start)
stop_handler = CommandHandler('stop', stop)
zigbang_handler = CommandHandler('zigbang', zigbang)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(zigbang_handler)

updater.start_polling()
updater.idle()
