import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import re
from deep_translator import GoogleTranslator
from datetime import datetime

# === FUNCTION: Check if translation is needed ===
def is_symbolic_only(text):
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r'\{[^}]+\}', '', text)
    cleaned = re.sub(r'[^\w]', '', cleaned)
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

# === FUNCTION: Perform Translation ===
def perform_translation(file_path, selected_langs, status_label):
    try:
        df = pd.read_excel(file_path)
        first_col = df.columns[0]
        df_translations = pd.DataFrame()
        df_translations[first_col] = df[first_col]

        status_label.config(text="🔁 Translating...")

        for lang in selected_langs:
            lang_name = GoogleTranslator.get_supported_languages(as_dict=True).get(lang, lang)
            df_translations[lang_name] = df[first_col].apply(lambda text: translate_preserving_curly_brackets(text, lang))

        output_file = f"translated_gui_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df_translations.to_excel(output_file, index=False)
        status_label.config(text=f"✅ Translation complete. Saved to {output_file}")
        messagebox.showinfo("Success", f"Translated file saved as:\n{output_file}")

    except Exception as err:
        messagebox.showerror("Error", f"Translation failed:\n{err}")
        status_label.config(text="❌ Error during translation")

# === GUI FUNCTION ===
def launch_gui():
    supported_langs = GoogleTranslator.get_supported_languages(as_dict=True)

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    def start_translation():
        file_path = file_entry.get()
        selected_langs = [lang_codes[i] for i in lang_listbox.curselection()]
        if not file_path or not selected_langs:
            messagebox.showwarning("Input Needed", "Please select a file and at least one language.")
            return
        perform_translation(file_path, selected_langs, status_label)

    # Initialize GUI window
    root = tk.Tk()
    root.title("Excel Translator")

    # Layout
    tk.Label(root, text="Select Excel File:").pack(pady=5)
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)
    file_entry = tk.Entry(file_frame, width=50)
    file_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT)

    tk.Label(root, text="Select Target Languages:").pack(pady=5)
    lang_frame = tk.Frame(root)
    lang_frame.pack(pady=5)

    lang_listbox = tk.Listbox(lang_frame, selectmode=tk.MULTIPLE, height=15, width=40)
    lang_scrollbar = tk.Scrollbar(lang_frame, command=lang_listbox.yview)
    lang_listbox.config(yscrollcommand=lang_scrollbar.set)

    lang_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    lang_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    # Populate languages
    lang_codes = list(supported_langs.keys())
    for code in lang_codes:
        lang_listbox.insert(tk.END, f"{supported_langs[code]} ({code})")

    # Translate button
    tk.Button(root, text="Translate", command=start_translation, bg="#4CAF50", fg="white").pack(pady=10)

    # Status label
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=5)

    root.mainloop()
