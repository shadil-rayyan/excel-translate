import pandas as pd
import re
from deep_translator import GoogleTranslator

# === CONFIG ===
INPUT_FILE = "en.xlsx"
HINT_COLUMN = "hint"
MODE_COLUMN = "mode"
TARGET_LANGS = {
    "en": "English",
    "ml": "Malayalam",
    "hi": "Hindi",
    "sa": "Sanskrit",
    "ta": "Tamil",
    "ar": "Arabic"
}

# === Function: Skip if only symbols/placeholders ===
def is_symbolic_only(text):
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r'\{[^}]+\}', '', text)
    cleaned = re.sub(r'[^\w]', '', cleaned)
    return len(cleaned.strip()) == 0

# === Function: Translate with placeholders preserved ===
def translate_hint(text, lang_code):
    if not isinstance(text, str) or is_symbolic_only(text):
        return text
    try:
        placeholders = re.findall(r'\{[^}]+\}', text)
        temp = text
        for i, ph in enumerate(placeholders):
            temp = temp.replace(ph, f"<<{i}>>")
        translated = GoogleTranslator(source='en', target=lang_code).translate(temp)
        for i, ph in enumerate(placeholders):
            translated = translated.replace(f"<<{i}>>", ph)
        return translated
    except Exception as e:
        print(f"⚠️ Translation error ({lang_code}): {e}")
        return text

# === Main Function ===
def main():
    df = pd.read_excel(INPUT_FILE)
    if MODE_COLUMN not in df.columns or HINT_COLUMN not in df.columns:
        print("❌ Missing required columns.")
        return

    for code, lang in TARGET_LANGS.items():
        print(f"🌐 Translating to {lang} ({code})...")
        out_df = pd.DataFrame()
        out_df[MODE_COLUMN] = df[MODE_COLUMN]  # Leave unchanged

        if code == "en":
            out_df[HINT_COLUMN] = df[HINT_COLUMN]
        else:
            out_df[HINT_COLUMN] = df[HINT_COLUMN].apply(lambda x: translate_hint(x, code))

        out_df.to_excel(f"{code}.xlsx", index=False)
        print(f"✅ Saved: {code}.xlsx")

    print("🎉 Done!")

# === Run ===
if __name__ == "__main__":
    main()
