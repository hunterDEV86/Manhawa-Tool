from telebot import *
from telebot.types import *
import io
import merged_code as mc
user_id_state = {}
save_path = ""
file_message = None
#------------------------------------------------------------------
token = "7553273593:AAFjVwuyZllmVrIw5KI1C8FBZnRA6wm7rg4"
bot = telebot.TeleBot(token)
#------------------------------------------------------------------
def change_user_state(user_id, state):
    user_id_state[user_id] = state
#------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Merged Manhwa", callback_data="merged"),
        InlineKeyboardButton("rename Manhwa", callback_data="rename"))
    bot.send_message(message.chat.id, "Salam be bot manhawa tool Khosh Amadid",reply_markup=keyboard)

#------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "merged":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "merged Manhwa selected")
        bot.send_message(call.message.chat.id, "Please send the zip file")
        change_user_state(call.message.chat.id, "get_zip_merged")
    if call.data == "rename":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "rename Manhwa selected")
        bot.send_message(call.message.chat.id, "Please send the zip file")
        change_user_state(call.message.chat.id, "get_zip_rename")

#------------------------------------------------------------------
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global save_path
    if user_id_state.get(message.chat.id) == "get_num_merged":
        a = mc.process_manhwa(save_path, int(message.text))
        bot.send_document(message.chat.id, open(a, 'rb'))
        os.remove(a)
        os.remove(save_path)
        change_user_state(message.chat.id, None)
    if user_id_state.get(message.chat.id) == "get_name_rename":
        a = file_downloader(file_message,False,message.text)
        bot.send_document(message.chat.id, open(a, 'rb'))
        os.remove(a)
        
#------------------------------------------------------------------
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    global save_path
    if message.document.mime_type == 'application/zip':
        if user_id_state.get(message.chat.id) == "get_zip_merged":
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            downloaded_file = bot.download_file(file_info.file_path)
            save_path = os.path.join('downloads', file_name)
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            change_user_state(message.chat.id, "get_num_merged")
            bot.send_message(message.chat.id, "Please enter the number of manhwa you want to merge")
        if user_id_state.get(message.chat.id) == "get_zip_rename":
            global file_message
            file_message = message
            change_user_state(message.chat.id, "get_name_rename")
            bot.send_message(message.chat.id, "Please enter the name of the manhwa (*.zip)")
#------------------------------------------------------------------
def file_downloader(message, is_default=True, name=None):
    file_info = bot.get_file(message.document.file_id)
    if is_default:
        file_name = message.document.file_name
    else:
        file_name = name
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = os.path.join('downloads', file_name)
        
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    return save_path
#------------------------------------------------------------------




bot.infinity_polling()

