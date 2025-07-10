import pandas as pd

def normalize_vodafone(df):
    df = df[df['CALL_TYPE'].str.lower() == 'voice']
    df_cleaned = pd.DataFrame()
    df_cleaned["A_NUMBER"] = df.get("A_NUMBER")
    df_cleaned["B_NUMBER"] = df.get("B_NUMBER")
    df_cleaned["FULL_DATE"] = pd.to_datetime(df.get("FULL_DATE"), errors='coerce')
    df_cleaned["ROUNDED_VOLUME"] = pd.to_numeric(df.get("ROUNDED_VOLUME"), errors='coerce')
    df_cleaned["B_NUMBER_FIRST_NAME"] = df.get("B_NUMBER_FIRST_NAME")
    df_cleaned["B_NUMBER_LAST_NAME"] = df.get("B_NUMBER_LAST_NAME")
    df_cleaned["B_NUMBER_ADDRESS"] = df.get("B_NUMBER_ADDRESS")
    df_cleaned["A_NUMBER_ADDRESS"] = df.get("A_NUMBER_ADDRESS")
    return df_cleaned

def analyze_location_vodafone(df):
    if df.empty or "A_NUMBER" not in df.columns or "FULL_DATE" not in df.columns or "SITE_ADDRESS" not in df.columns:
        return "البيانات غير مكتملة لتحليل الموقع."

    df = df.copy()
    df["HOUR"] = df["FULL_DATE"].dt.hour

    # تحديد صاحب الخط الأساسي
    main_number = df["A_NUMBER"].dropna().astype(str).value_counts().idxmax()
    df_user = df[df["A_NUMBER"] == main_number]

    # الموست لوكيشن العام
    overall = df_user["SITE_ADDRESS"].value_counts().idxmax()
    overall_count = df_user["SITE_ADDRESS"].value_counts().max()

    # وقت العمل: من 8 إلى 17
    work_df = df_user[df_user["HOUR"].between(8, 17)]
    work_loc = work_df["SITE_ADDRESS"].value_counts().idxmax() if not work_df.empty else "لا يوجد"
    work_count = work_df["SITE_ADDRESS"].value_counts().max() if not work_df.empty else 0

    # وقت النوم: من 0 إلى 8
    sleep_df = df_user[df_user["HOUR"].between(0, 8)]
    sleep_loc = sleep_df["SITE_ADDRESS"].value_counts().idxmax() if not sleep_df.empty else "لا يوجد"
    sleep_count = sleep_df["SITE_ADDRESS"].value_counts().max() if not sleep_df.empty else 0

    return (
        "تحليل الموقع لصاحب الخط:\n\n"
        f"1. الموست لوكيشن العام:\n   {overall} ({overall_count} مرة)\n\n"
        f"2. وقت العمل (8 ص - 5 م):\n   {work_loc} ({work_count} مرة)\n\n"
        f"3. وقت النوم (12 ص - 8 ص):\n   {sleep_loc} ({sleep_count} مرة)"
    )

from utils.helpers import safe_extract

def last_calls_vodafone(df):
    if df.empty or "A_NUMBER" not in df.columns or "FULL_DATE" not in df.columns:
        return "لا يمكن عرض المكالمات. البيانات غير مكتملة."

    df = df.copy()
    df["FULL_DATE"] = pd.to_datetime(df["FULL_DATE"], errors='coerce')
    df = df.sort_values(by="FULL_DATE", ascending=False)

    main_number = df["A_NUMBER"].dropna().astype(str).value_counts().idxmax()

    df_filtered = df[
        (df["A_NUMBER"] == main_number) | (df["B_NUMBER"] == main_number)
    ].copy()

    if df_filtered.empty:
        return "لا يوجد مكالمات مرتبطة برقم المستخدم."

    results = []
    for _, row in df_filtered.head(10).iterrows():
        direction = "صادرة" if row["A_NUMBER"] == main_number else "واردة"
        other_number = row["B_NUMBER"] if direction == "صادرة" else row["A_NUMBER"]

        fname = safe_extract(pd.DataFrame([row]), "B_NUMBER_FIRST_NAME") if direction == "صادرة" else "غير متوفر"
        lname = safe_extract(pd.DataFrame([row]), "B_NUMBER_LAST_NAME") if direction == "صادرة" else ""
        name = f"{fname} {lname}".strip() if fname != "غير متوفر" else "غير متوفر"
        nid = safe_extract(pd.DataFrame([row]), "B_NUMBER_NATIONAL_ID") if direction == "صادرة" else "غير متوفر"
        address = safe_extract(pd.DataFrame([row]), "B_NUMBER_ADDRESS") if direction == "صادرة" else "غير متوفر"

        site_user = row.get("SITE_ADDRESS") or "غير متوفر"
        site_other = row.get("B_NUMBER_SITE_ADDRESS") if direction == "صادرة" else row.get("SITE_ADDRESS")
        site_other = site_other or "غير متوفر"

        result = (
            f"النوع            : {direction}\n"
            f"التاريخ والوقت   : {row['FULL_DATE']}\n"
            f"الطرف الآخر      : {other_number}\n"
            f"الاسم            : {name}\n"
            f"الرقم القومي     : {nid}\n"
            f"العنوان          : {address}\n"
            f"موقع المستخدم    : {site_user}\n"
            f"موقع الطرف الآخر : {site_other}\n"
            f"{'-'*40}"
        )
        results.append(result)

    return "\n\n".join(results)