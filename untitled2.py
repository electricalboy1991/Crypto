import telegram
from telegram.ext import Updater, CommandHandler

# Telegram bot token
TOKEN = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handler function
def update_variable(update, context):
    # Change the variable value in your code here
    new_value = context.args[0]
    # Perform necessary actions with new_value

    update.message.reply_text(f"Variable updated to {new_value}")

# Register the command handler
dispatcher.add_handler(CommandHandler('update', update_variable))

# Start the bot
updater.start_polling()
updater.idle()
