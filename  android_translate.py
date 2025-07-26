import os
import xml.etree.ElementTree as ET
import requests
import glob
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

API_URL = "https://libretranslate.com/translate"

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def translate_text(text, source_lang, target_lang):
    if not text.strip():
        return text
    try:
        response = requests.post(API_URL, data={
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        })
        response.raise_for_status()
        return response.json()['translatedText']
    except Exception as e:
        print(f"Translation failed for '{text}': {e}")
        return text

def process_string_elements(root, source_lang, target_lang):
    for elem in root.findall('string'):
        if elem.get('translatable') == 'false':
            continue
        if elem.text:
            elem.text = translate_text(elem.text, source_lang, target_lang)

    for array in root.findall('string-array'):
        for item in array.findall('item'):
            if item.get('translatable') == 'false':
                continue
            if item.text:
                item.text = translate_text(item.text, source_lang, target_lang)

def translate_file(input_file_path, output_file_path, source_lang, target_lang):
    tree = ET.parse(input_file_path)
    root = tree.getroot()
    process_string_elements(root, source_lang, target_lang)
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Select folder", "Please select the 'values' folder to translate.")
    input_folder = filedialog.askdirectory(title="Select values folder")

    if not input_folder:
        messagebox.showwarning("No folder selected", "You must select a folder. Exiting.")
        return

    source_lang = simpledialog.askstring("Source Language", "Enter source language code (e.g., en):")
    if not source_lang:
        return

    target_lang = simpledialog.askstring("Target Language", "Enter target language code (e.g., ml):")
    if not target_lang:
        return

    output_folder = os.path.join("translated", f"values-{target_lang}")
    create_directory(output_folder)

    xml_files = glob.glob(os.path.join(input_folder, "*.xml"))

    for xml_file in xml_files:
        filename = os.path.basename(xml_file)
        output_file_path = os.path.join(output_folder, filename)
        print(f"Translating {filename} -> {target_lang}")
        translate_file(xml_file, output_file_path, source_lang, target_lang)

    messagebox.showinfo("Done", f"✅ Translation complete!\nCheck folder: {output_folder}/")

if __name__ == "__main__":
    main()
