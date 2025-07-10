def safe_extract(df, col):
    """استخراج آمن من أي عمود"""
    if col and col in df.columns and not df[col].dropna().empty:
        return str(df[col].dropna().iloc[0])
    return "غير متوفر"