from telegram import Update
from telegram.ext import ContextTypes
from parsers.vodafone import last_calls_vodafone
from parsers.etisalat import last_calls_etisalat
from parsers.orange import last_calls_orange

async def last_calls_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    df = context.user_data.get("df")
    network_type = context.user_data.get("network_type")

    if df is None or network_type is None:
        await query.edit_message_text("❌ لا يوجد ملف محلل حالياً.")
        return

    if network_type == "vodafone":
        result = last_calls_vodafone(df)
    elif network_type == "etisalat":
        result = last_calls_etisalat(df)
    elif network_type == "orange":
        result = last_calls_orange(df)
    else:
        await query.edit_message_text("❌ نوع الشبكة غير معروف.")
        return

    await query.edit_message_text(result)