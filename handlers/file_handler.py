import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from parsers.vodafone import normalize_vodafone
from parsers.orange import normalize_orange
from parsers.etisalat import normalize_etisalat

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file.file_name.endswith(('.xlsx', '.xls')):
        await update.message.reply_text("❌ يرجى إرسال ملف Excel فقط.")
        return

    network_type = context.user_data.get("network_type")
    if not network_type:
        await update.message.reply_text("⚠️ من فضلك اختر نوع الشبكة أولاً باستخدام /start.")
        return

    file_path = os.path.join(os.getcwd(), file.file_name)
    telegram_file = await file.get_file()
    await telegram_file.download_to_drive(file_path)

    try:
        excel = pd.ExcelFile(file_path)
        df = excel.parse(excel.sheet_names[0])

        if network_type == "vodafone":
            df_cleaned = normalize_vodafone(df)
        elif network_type == "orange":
            df_cleaned = normalize_orange(df)
        elif network_type == "etisalat":
            df_cleaned = normalize_etisalat(df)
        else:
            await update.message.reply_text("⚠️ نوع الشبكة غير معروف.")
            return

        context.user_data["df"] = df_cleaned

        await update.message.reply_text(f"📄 تم رفع الملف بنجاح.\nنوع الشبكة: {network_type.capitalize()}")

        keyboard_extra = [
            [InlineKeyboardButton("📎 استخراج الروابط", callback_data="extract_links")],
            [InlineKeyboardButton("📡 تحليل الأبراج", callback_data="analyze_towers")],
            [InlineKeyboardButton("📞 آخر المكالمات", callback_data="last_calls_alt")]
        ]
        await update.message.reply_text(
            "*القائمة الرئيسية:*",
            reply_markup=InlineKeyboardMarkup(keyboard_extra),
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ حصل خطأ أثناء قراءة الملف:\n{e}")