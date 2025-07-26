import pandas as pd
import re
from deep_translator import GoogleTranslator
from datetime import datetime

# === CONFIGURATION ===
INPUT_FILE = "input.xlsx"
TARGET_LANGS = {
    "ml": "Malayalam",
    "hi": "Hindi",
    "sa": "Sanskrit",
    "ta": "Tamil",
    "ar": "Arabic"
}

# === FUNCTION: Check if translation is needed ===
def is_symbolic_only(text):
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r'\{[^}]+\}', '', text)  # remove placeholders
    cleaned = re.sub(r'[^\w]', '', cleaned)   # remove punctuation/symbols
    return len(cleaned.strip()) == 0

# === FUNCTION: Translate text while preserving placeholders ===
def translate_preserving_curly_brackets(text, target_lang):
    if not isinstance(text, str) or is_symbolic_only(text):
        return text

    try:
        curly_items = re.findall(r'\{[^}]+\}', text)
        temp_text = text
        for idx, item in enumerate(curly_items):
            temp_text = temp_text.replace(item, f"<<{idx}>>")

        translated_temp = GoogleTranslator(source='en', target=target_lang).translate(temp_text)

        for idx, item in enumerate(curly_items):
            translated_temp = translated_temp.replace(f"<<{idx}>>", item)

        return translated_temp

    except Exception as e:
        print(f"❌ Error translating '{text}' to '{target_lang}': {e}")
        return text

# === MAIN FUNCTION ===
def main():
    try:
        df = pd.read_excel(INPUT_FILE)
        first_col = df.columns[0]
        df_translations = pd.DataFrame()
        df_translations[first_col] = df[first_col]

        print(f"🔁 Translating column '{first_col}' to multiple languages...")

        for lang_code, lang_name in TARGET_LANGS.items():
            print(f"🌐 Translating to {lang_name}...")
            df_translations[lang_name] = df[first_col].apply(lambda text: translate_preserving_curly_brackets(text, lang_code))

        output_file = f"translated_multilang_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df_translations.to_excel(output_file, index=False)
        print(f"✅ Translation completed! Output saved as: {output_file}")

    except Exception as err:
        print("❌ Main Error:", err)

# === RUN ===
if __name__ == "__main__":
    main()
