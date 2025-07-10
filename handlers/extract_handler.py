from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import safe_extract

async def extract_links_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    df = context.user_data.get("df")
    network_type = context.user_data.get("network_type")

    if df is None or network_type is None:
        await query.edit_message_text("لا يوجد ملف محلل حالياً.")
        return

    try:
        if network_type == "vodafone":
            user_col = "A_NUMBER"
            target_col = "B_NUMBER"
            fname_col = "B_NUMBER_FIRST_NAME"
            lname_col = "B_NUMBER_LAST_NAME"
            nid_col = "B_NUMBER_NATIONAL_ID"
            address_col = "B_NUMBER_ADDRESS"
        elif network_type == "etisalat":
            user_col = "A_NUMBER"
            target_col = "B_NUMBER"
            fname_col = "B_NUMBER_FIRSTNAME"
            lname_col = "B_NUMBER_LASTNAME"
            nid_col = "ID Number"
            address_col = "B_Number_Address"
        elif network_type == "orange":
            user_col = "A_NUMBER"
            target_col = "OTHER_MSISDN"
            fname_col = "OTHER_NAME"
            lname_col = "NONE"
            nid_col = "OTHER_ID"
            address_col = "OTHER_ADDRESS"
        else:
            await query.edit_message_text("نوع الشبكة غير معروف.")
            return

        # تأكد من وجود بيانات للرقم الأساسي
        if user_col not in df.columns or df[user_col].dropna().empty:
            await query.edit_message_text("الملف لا يحتوي على بيانات صالحة لصاحب الخط.")
            return

        main_number = df[user_col].dropna().astype(str).value_counts().idxmax()
        df_filtered = df[df[user_col] == main_number]

        top_numbers = (
            df_filtered[target_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )

        results = []
        for number, count in top_numbers.items():
            rows = df[df[target_col].astype(str) == number]
            fname = safe_extract(rows, fname_col)
            lname = safe_extract(rows, lname_col) if lname_col else ""
            name = f"{fname} {lname}".strip() if fname != "غير متوفر" else "غير متوفر"
            nid = safe_extract(rows, nid_col)
            address = safe_extract(rows, address_col)

            result = (
                f"رقم الهاتف      : {number}\n"
                f"عدد المكالمات   : {count}\n"
                f"الاسم           : {name}\n"
                f"الرقم القومي    : {nid}\n"
                f"العنوان         : {address}\n"
                f"{'-' * 40}"
            )
            results.append(result)

        final_text = "\n\n".join(results)

        if len(final_text) > 4000:
            file_path = f"top_10_summary_{network_type}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            await query.message.reply_document(document=open(file_path, "rb"), filename=file_path)
        else:
            await query.message.reply_text(final_text)

    except Exception as e:
        await query.edit_message_text(f"حدث خطأ أثناء تحليل البيانات:\n{e}")