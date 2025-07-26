import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
from deep_translator import GoogleTranslator
from datetime import datetime

# === FUNCTION: Check if text needs translation ===
def is_symbolic_only(text):
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r'\{[^}]+\}', '', text)
    cleaned = re.sub(r'[^\w]', '', cleaned)
    return len(cleaned.strip()) == 0

# === FUNCTION: Translate text while preserving placeholders like {a}, {b} ===
def translate_preserving_brackets(text, target_lang):
    if not isinstance(text, str) or is_symbolic_only(text):
        return text

    try:
        # Temporarily mask {a}, {b}, etc.
        placeholders = re.findall(r'\{[^}]+\}', text)
        masked_text = text
        for i, ph in enumerate(placeholders):
            masked_text = masked_text.replace(ph, f"___PLACEHOLDER_{i}___")

        # Translate
        translated = GoogleTranslator(source='en', target=target_lang).translate(masked_text)

        # Restore placeholders
        for i, ph in enumerate(placeholders):
            translated = translated.replace(f"___PLACEHOLDER_{i}___", ph)

        return translated
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text

# === FUNCTION: Perform Translation ===
def perform_translation(file_path, selected_langs, status_label):
    try:
        df = pd.read_excel(file_path)
        question_col = df.columns[0]  # Only first column is translated
        status_label.config(text="🔁 Translating...")

        for lang in selected_langs:
            translated_col_name = f"{question_col}_{lang}"
            df[translated_col_name] = df[question_col].apply(lambda text: translate_preserving_brackets(text, lang))

        output_file = f"translated_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False)

        status_label.config(text=f"✅ Saved: {output_file}")
        messagebox.showinfo("Success", f"Translated file saved as:\n{output_file}")
    except Exception as e:
        status_label.config(text="❌ Error")
        messagebox.showerror("Error", str(e))

# === GUI Launcher ===
def launch_gui():
    supported_langs = GoogleTranslator(source='en', target='hi').get_supported_languages(as_dict=True)

    def browse_file():
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, path)

    def start_translation():
        path = file_entry.get()
        selected = [lang_codes[i] for i in lang_listbox.curselection()]
        if not path or not selected:
            messagebox.showwarning("Input Needed", "Select a file and language(s).")
            return
        perform_translation(path, selected, status_label)

    root = tk.Tk()
    root.title("Excel Question Translator")

    tk.Label(root, text="Select Excel File:").pack()
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)
    file_entry = tk.Entry(file_frame, width=50)
    file_entry.pack(side=tk.LEFT)
    tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT, padx=5)

    tk.Label(root, text="Select Target Languages:").pack()
    lang_frame = tk.Frame(root)
    lang_frame.pack(pady=5)

    lang_listbox = tk.Listbox(lang_frame, selectmode=tk.MULTIPLE, height=12, width=40)
    lang_scrollbar = tk.Scrollbar(lang_frame, command=lang_listbox.yview)
    lang_listbox.config(yscrollcommand=lang_scrollbar.set)
    lang_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    lang_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    lang_codes = list(supported_langs.keys())
    for code in lang_codes:
        lang_listbox.insert(tk.END, f"{supported_langs[code]} ({code})")

    tk.Button(root, text="Translate", command=start_translation, bg="#4CAF50", fg="white").pack(pady=10)
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
