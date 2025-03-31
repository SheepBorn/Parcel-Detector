from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
import nest_asyncio
import time
import Settings

nest_asyncio.apply()
TOKEN:Final = Settings.settings["token"]
BOT_USERNAME:Final = Settings.settings["bot_username"]
chat_id = Settings.settings["chat_id"]
app = Application.builder().token(TOKEN).build()

# to let handler know a photo was requested
request = False 
# last notification time
last_notification = 0 
# minimum time between notifications
cooldown = Settings.settings["cooldown"] 

# allows bot to save chat_id for notifications
async def start_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    global chat_id
    chat_id = update.effective_chat.id
    await update.message.reply_text('Hello! This is Delivery Alert Bot')

# called when user send /pic to bot to request for live image
async def pic_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    global request
    request = True

# function to send an image notification to user with the image and caption as input
async def image_notification(image,caption = ""):
    global chat_id
    if chat_id:
        if check_cd():
            await app.bot.send_photo(chat_id, photo=open(image,'rb'),caption=caption, filename='Alert.png')

# function to send a gif notification to user with the video and caption as input
async def GIF_notification(video, caption = ""):
    global chat_id
    if chat_id:
        if check_cd():
            await app.bot.send_animation(chat_id, animation=open(video,'rb'),caption=caption)


# function handles messages outside of commands. only sends back whatever the user types
async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    message_type:str = update.message.chat.type
    text:str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text:str = text.replace(BOT_USERNAME, '').strip()
            response:str = handle_response(new_text)
        else:
            return
    else:
        response:str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def handle_response(text:str)->str:
    processed:str = text.lower()
    return text

async def run_bot():

    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('pic', pic_command))

    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #errorsC
    app.add_error_handler(error)

    await app.run_polling(poll_interval=3)

def check_cd():
    global last_notification
    curr = time.time()
    if curr - last_notification < cooldown:
        return False
    
    last_notification = curr
    return True