import requests
import telegram

telegram_token_Log = '5751723602:AAEjojgFOutl4ffbDghL_urHx10ijEwkBeU'
telegram_id_Log = '5781986806'

telegram_token_SP = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'
telegram_id_SP = '5781986806'

telegram_token_Summary1minute = '5462808910:AAGDKsBtsM4B5Lc93rdfS3wX_YjvBnl-tYg'
telegram_id_Summary1minute = '5781986806'

#메세지를 보냅니다.
def SendMessage_Trading(msg):
    try:

        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = 'sINSUIhAuhPg4hIq1lMgtVcswlx4PL22DTLspAwAvsh' #여러분의 값으로 변경

        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + TOKEN
            },
            data={
                'message': msg
            }
        )

    except Exception as ex:
        print(ex)

def SendMessage_Log(message):
    try:
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_Log)
        res = bot.sendMessage(chat_id=telegram_id_Log, text=message)

        return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

def SendMessage_SP(message):
    try:
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_SP)
        res = bot.sendMessage(chat_id=telegram_id_SP, text=message)

        return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise


def SendMessage_Summary1minute(message):
    try:
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_Summary1minute)
        res = bot.sendMessage(chat_id=telegram_id_Summary1minute, text=message)

        return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise