
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
TOKEN = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'
# Initialize the bot token and create an Updater
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Global variable
AD_flag = 1

# Function to handle the /update_variable command
def update_variable(update, context):
    global AD_flag
    new_value = context.args[0]
    AD_flag = int(new_value)
    update.message.reply_text(f"AD_flag has been updated to {AD_flag}")

# Function to handle regular messages
def message_handler(update, context):
    message_text = update.message.text
    if message_text.startswith('/update_variable'):
        update_variable(update, context)
    else:
        update.message.reply_text("Invalid command")

# Register the command and message handlers
dispatcher.add_handler(CommandHandler('update_variable', update_variable))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

# Start the bot
updater.start_polling()

# Loop to print the value of AD_flag
while True:
    time.sleep(3)
    print(AD_flag)

    # Add any other code or conditions here if needed
