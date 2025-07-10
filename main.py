from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)

from config import TOKEN

# === Handlers ===
from handlers.start_handler import start, handle_choice
from handlers.file_handler import handle_file
from handlers.extract_handler import extract_links_handler
from handlers.analyze_handler import analyze_towers_handler
from handlers.last_calls_handler import last_calls_handler

def main():
    app = Application.builder().token(TOKEN).build()

    # أوامر البداية
    app.add_handler(CommandHandler("start", start))

    # التعامل مع اختيارات الشبكة
    app.add_handler(CallbackQueryHandler(handle_choice, pattern="^choose_"))

    # استقبال ملفات Excel
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # استخراج أكثر 10 أرقام
    app.add_handler(CallbackQueryHandler(extract_links_handler, pattern="^extract_links$"))

    # تحليل الأبراج
    app.add_handler(CallbackQueryHandler(analyze_towers_handler, pattern="^analyze_towers$"))

    # آخر المكالمات
    app.add_handler(CallbackQueryHandler(last_calls_handler, pattern="^last_calls_alt$"))

    app.run_polling()

if __name__ == "__main__":
    main()