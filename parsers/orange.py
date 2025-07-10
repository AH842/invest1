import pandas as pd

def normalize_orange(df_raw):
    df = df_raw.copy()
    df.columns = df.iloc[4]
    df = df[5:].reset_index(drop=True)

    df_cleaned = pd.DataFrame()
    df_cleaned["A_NUMBER"] = df.get("MSISDN")
    df_cleaned["B_NUMBER"] = df.get("OTHER_MSISDN")
    df_cleaned["FULL_DATE"] = pd.to_datetime(df.get("EVENT_START_TIME"), errors='coerce')
    df_cleaned["ROUNDED_VOLUME"] = pd.to_numeric(df.get("CALL_DURATION"), errors='coerce')
    df_cleaned["B_NUMBER_FIRST_NAME"] = df.get("OTHER_NAME")
    df_cleaned["B_NUMBER_LAST_NAME"] = None
    df_cleaned["B_NUMBER_ADDRESS"] = df.get("STREET")
    df_cleaned["A_NUMBER_ADDRESS"] = df.get("CITY")
    return df_cleaned

def analyze_location_orange(df):
    if df.empty or "A_NUMBER" not in df.columns or "FULL_DATE" not in df.columns or "CELL_ADDRESS" not in df.columns:
        return "البيانات غير مكتملة لتحليل الموقع."

    df = df.copy()
    df["HOUR"] = df["FULL_DATE"].dt.hour

    main_number = df["A_NUMBER"].dropna().astype(str).value_counts().idxmax()
    df_user = df[df["A_NUMBER"] == main_number]

    overall = df_user["CELL_ADDRESS"].value_counts().idxmax()
    overall_count = df_user["CELL_ADDRESS"].value_counts().max()

    work_df = df_user[df_user["HOUR"].between(8, 17)]
    work_loc = work_df["CELL_ADDRESS"].value_counts().idxmax() if not work_df.empty else "لا يوجد"
    work_count = work_df["CELL_ADDRESS"].value_counts().max() if not work_df.empty else 0

    sleep_df = df_user[df_user["HOUR"].between(0, 8)]
    sleep_loc = sleep_df["CELL_ADDRESS"].value_counts().idxmax() if not sleep_df.empty else "لا يوجد"
    sleep_count = sleep_df["CELL_ADDRESS"].value_counts().max() if not sleep_df.empty else 0

    return (
        "تحليل الموقع لصاحب الخط:\n\n"
        f"1. الموست لوكيشن العام:\n   {overall} ({overall_count} مرة)\n\n"
        f"2. وقت العمل (8 ص - 5 م):\n   {work_loc} ({work_count} مرة)\n\n"
        f"3. وقت النوم (12 ص - 8 ص):\n   {sleep_loc} ({sleep_count} مرة)"
    )

from utils.helpers import safe_extract
import pandas as pd

def last_calls_orange(df):
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

        name = safe_extract(pd.DataFrame([row]), "OTHER_NAME") if direction == "صادرة" else "غير متوفر"
        nid = safe_extract(pd.DataFrame([row]), "OTHER_ID") if direction == "صادرة" else "غير متوفر"
        address = safe_extract(pd.DataFrame([row]), "OTHER_ADDRESS") if direction == "صادرة" else "غير متوفر"

        site_user = row.get("CELL_ADDRESS") or "غير متوفر"
        site_other = row.get("CELL_ADDRESS")  # Orange غالبًا ما بتستخدم نفس العمود
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