from telebot import *
from telebot.types import *
import io
import merged_code

user_id_state = {}
def change_user_state(user_id, state):
    user_id_state[user_id] = state

token = "7553273593:AAFjVwuyZllmVrIw5KI1C8FBZnRA6wm7rg4"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Merged Manhwa", callback_data="merged"),
        InlineKeyboardButton("Latest Updates", callback_data="latest"))
    bot.send_message(message.chat.id, "Salam be bot manhawa tool Khosh Amadid",reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "merged":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "merged Manhwa selected")
        bot.send_message(call.message.chat.id, "Please send the zip file")
        change_user_state(call.message.chat.id, "get_zip_merged")

#------------------------------------------------------------------
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/zip':
        if user_id_state.get(message.chat.id) == "get_zip_merged":
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
        
        # Create downloads directory if it doesn't exist
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
        # Download and save the file
            downloaded_file = bot.download_file(file_info.file_path)
            save_path = os.path.join('downloads', file_name)
        
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            merged_code.process_manhwa(save_path, 10)

def get_zip(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    zip_buffer = io.BytesIO(downloaded_file)




bot.infinity_polling()

