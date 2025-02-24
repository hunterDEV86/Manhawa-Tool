import telebot
from telebot import types
import zipfile
import os
from PIL import Image
from io import BytesIO

# توکن ربات تلگرام خودت رو وارد کن
TOKEN = '7264390282:AAGbnTa8u6SRqxJpaiyhnMBpTYVc5KvrC7s'
bot = telebot.TeleBot(TOKEN)

# ذخیره‌سازی فایل‌های آپلود شده
UPLOAD_DIR = 'uploaded_files/'

# بررسی و ایجاد پوشه در صورت نبودن
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# تابعی برای ترکیب کردن تصاویر به صورت عمودی (تومار)
def merge_images(image_list, output_path):
    images = [Image.open(image) for image in image_list]
    
    # محاسبه عرض و ارتفاع تصاویر
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights)
    max_width = max(widths)
    
    # ایجاد تصویر جدید برای چسباندن تصاویر
    new_image = Image.new('RGB', (max_width, total_height))
    
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    new_image.save(output_path)

# دریافت فایل zip و پردازش
@bot.message_handler(content_types=['document'])
def handle_zip_file(message):
    if message.document.mime_type == 'application/zip':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ذخیره فایل zip
        zip_path = os.path.join(UPLOAD_DIR, message.document.file_name)
        with open(zip_path, 'wb') as f:
            f.write(downloaded_file)
        
        # استخراج فایل‌های zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(UPLOAD_DIR)
        
        # فهرست کردن فایل‌های تصویری
        image_files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
        
        # پرسیدن تعداد تصاویر در هر مرحله
        bot.send_message(message.chat.id, "چند تصویر را می‌خواهید با هم ترکیب کنم؟")

        bot.register_next_step_handler(message, process_image_count, image_files)

# پردازش تعداد تصاویر برای ترکیب
def process_image_count(message, image_files):
    try:
        count = int(message.text)
        if count <= 0 or count > len(image_files):
            bot.send_message(message.chat.id, "لطفا یک عدد صحیح معتبر وارد کنید.")
            return
        
        # تقسیم تصاویر به گروه‌ها
        grouped_images = [image_files[i:i+count] for i in range(0, len(image_files), count)]
        
        # پردازش تصاویر
        output_images = []
        for idx, group in enumerate(grouped_images):
            output_path = os.path.join(UPLOAD_DIR, f"merged_{idx+1}.jpg")
            merge_images(group, output_path)
            output_images.append(output_path)

        # فشرده‌سازی خروجی‌ها
        zip_output_path = os.path.join(UPLOAD_DIR, "merged_images.zip")
        with zipfile.ZipFile(zip_output_path, 'w') as zipf:
            for img in output_images:
                zipf.write(img, os.path.basename(img))

        # ارسال فایل زیپ
        with open(zip_output_path, 'rb') as zip_file:
            bot.send_document(message.chat.id, zip_file)
        
        # حذف فایل‌های موقتی
        for file in image_files + output_images:
            os.remove(file)
        os.remove(zip_output_path)
        
    except ValueError:
        bot.send_message(message.chat.id, "لطفا یک عدد صحیح وارد کنید.")

# راه‌اندازی ربات
bot.polling(none_stop=True)
