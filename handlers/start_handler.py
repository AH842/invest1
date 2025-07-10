from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# دالة /start لعرض خيارات الشبكات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📶 Vodafone", callback_data="choose_vodafone")],
        [InlineKeyboardButton("🟠 Orange", callback_data="choose_orange")],
        [InlineKeyboardButton("🟢 Etisalat", callback_data="choose_etisalat")]
    ]
    await update.message.reply_text("اختر الشبكة المستخدمة:", reply_markup=InlineKeyboardMarkup(keyboard))

# دالة التعامل مع اختيار نوع الشبكة
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mapping = {
        "choose_vodafone": "vodafone",
        "choose_orange": "orange",
        "choose_etisalat": "etisalat"
    }

    selected = mapping.get(query.data)
    if selected:
        context.user_data["network_type"] = selected
        await query.edit_message_text(f"✅ تم اختيار: {selected.capitalize()}\nمن فضلك ارفع الآن ملف Excel الخاص بالشبكة.")
    else:
        await query.edit_message_text("⚠️ اختيار غير صالح.")