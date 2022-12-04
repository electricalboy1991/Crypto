import time, datetime
import telepot
from telepot.loop import MessageLoop

now = datetime.datetime.now()

def action(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print('Received: %s' % command)

    if command=='on':

        message = "김프 매매"
        message = message + "  On"

        telegram_bot.sendMessage(chat_id, message)

    if command=='off':
        message = "김프 매매"
        message = message + "  Off"

        telegram_bot.sendMessage(chat_id, message)


telegram_bot = telepot.Bot('5642937839:AAH3rKf99gR4cBHjtKIEUhkWm9wWt8LRX7o')

print(telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()

print('RemoteController is Running....')

while 1:
    time.sleep(10)