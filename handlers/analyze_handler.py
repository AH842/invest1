from telegram import Update
from telegram.ext import ContextTypes
from parsers.vodafone import analyze_location_vodafone
from parsers.etisalat import analyze_location_etisalat
from parsers.orange import analyze_location_orange

async def analyze_towers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    df = context.user_data.get("df")
    network_type = context.user_data.get("network_type")

    if df is None or network_type is None:
        await query.edit_message_text("❌ لا يوجد ملف محلل حالياً.")
        return

    # اختيار الدالة المناسبة حسب الشبكة
    if network_type == "vodafone":
        result = analyze_location_vodafone(df)
    elif network_type == "etisalat":
        result = analyze_location_etisalat(df)
    elif network_type == "orange":
        result = analyze_location_orange(df)
    else:
        await query.edit_message_text("❌ نوع الشبكة غير معروف.")
        return

    await query.edit_message_text(result)