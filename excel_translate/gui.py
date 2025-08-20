from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# deep_translator is imported lazily inside launch_gui()

from .files import find_excel_files, scan_columns_from_first_file
from .translate import translate_dataframe_columns


__all__ = ["launch_gui"]


def launch_gui() -> None:
    root = tk.Tk()
    root.title("Excel Batch Translator")

    # State
    selected_files: list[str] = []
    selected_folder = tk.StringVar(value="")
    recursive_var = tk.BooleanVar(value=True)
    output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "translated"))

    # Languages
    try:
        from deep_translator import GoogleTranslator  # type: ignore

        supported_langs = GoogleTranslator(source="en", target="hi").get_supported_languages(as_dict=True)
    except Exception:
        supported_langs = {"hi": "Hindi", "ml": "Malayalam", "ta": "Tamil", "ar": "Arabic"}
    lang_codes = list(supported_langs.keys())

    # Files frame
    files_frame = ttk.LabelFrame(root, text="Input Selection")
    files_frame.pack(fill=tk.X, padx=10, pady=8)

    def browse_files():
        nonlocal selected_files
        files = filedialog.askopenfilenames(title="Select Excel files", filetypes=[("Excel", "*.xlsx")])
        if files:
            selected_files = list(files)
            files_list.delete(0, tk.END)
            for p in selected_files:
                files_list.insert(tk.END, p)

    def browse_folder():
        folder = filedialog.askdirectory(title="Select folder with Excel files")
        if folder:
            selected_folder.set(folder)

    files_btns = ttk.Frame(files_frame)
    files_btns.pack(fill=tk.X, pady=4)

    ttk.Button(files_btns, text="Browse Files…", command=browse_files).pack(side=tk.LEFT)
    ttk.Button(files_btns, text="Browse Folder…", command=browse_folder).pack(side=tk.LEFT, padx=6)
    ttk.Checkbutton(files_btns, text="Recursive", variable=recursive_var).pack(side=tk.LEFT)

    ttk.Label(files_frame, text="Selected Folder:").pack(anchor=tk.W)
    ttk.Entry(files_frame, textvariable=selected_folder).pack(fill=tk.X)

    ttk.Label(files_frame, text="Selected Files:").pack(anchor=tk.W, pady=(6, 0))
    files_list = tk.Listbox(files_frame, height=4)
    files_list.pack(fill=tk.BOTH)

    # Columns frame
    cols_frame = ttk.LabelFrame(root, text="Columns to Translate (default: all detected)")
    cols_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    columns_listbox = tk.Listbox(cols_frame, selectmode=tk.MULTIPLE, height=8)
    columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    cols_scroll = ttk.Scrollbar(cols_frame, command=columns_listbox.yview)
    cols_scroll.pack(side=tk.LEFT, fill=tk.Y)
    columns_listbox.config(yscrollcommand=cols_scroll.set)

    def scan_columns():
        files = find_excel_files(selected_files, selected_folder.get(), recursive_var.get())
        cols = scan_columns_from_first_file(files)
        columns_listbox.delete(0, tk.END)
        for c in cols:
            columns_listbox.insert(tk.END, c)
        # Select all by default
        columns_listbox.select_set(0, tk.END)
        status_var.set(f"Found {len(files)} file(s). Columns detected: {len(cols)}")

    btns_col = ttk.Frame(cols_frame)
    btns_col.pack(side=tk.LEFT, fill=tk.Y, padx=6)
    ttk.Button(btns_col, text="Scan Columns", command=scan_columns).pack(fill=tk.X)
    ttk.Button(btns_col, text="Select All", command=lambda: columns_listbox.select_set(0, tk.END)).pack(
        fill=tk.X, pady=4
    )
    ttk.Button(btns_col, text="Clear", command=lambda: columns_listbox.selection_clear(0, tk.END)).pack(fill=tk.X)

    # Languages frame
    langs_frame = ttk.LabelFrame(root, text="Target Languages")
    langs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    langs_listbox = tk.Listbox(langs_frame, selectmode=tk.MULTIPLE, height=10)
    langs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for code in lang_codes:
        langs_listbox.insert(tk.END, f"{supported_langs.get(code, code)} ({code})")

    langs_scroll = ttk.Scrollbar(langs_frame, command=langs_listbox.yview)
    langs_scroll.pack(side=tk.LEFT, fill=tk.Y)
    langs_listbox.config(yscrollcommand=langs_scroll.set)

    # Output frame
    out_frame = ttk.LabelFrame(root, text="Output")
    out_frame.pack(fill=tk.X, padx=10, pady=8)

    def browse_output_dir():
        d = filedialog.askdirectory(title="Select output directory")
        if d:
            output_dir.set(d)

    ttk.Label(out_frame, text="Output Directory:").pack(anchor=tk.W)
    od_row = ttk.Frame(out_frame)
    od_row.pack(fill=tk.X)
    ttk.Entry(od_row, textvariable=output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(od_row, text="Browse…", command=browse_output_dir).pack(side=tk.LEFT, padx=6)

    # Status and actions
    actions = ttk.Frame(root)
    actions.pack(fill=tk.X, padx=10, pady=6)

    status_var = tk.StringVar(value="")
    status_lbl = ttk.Label(actions, textvariable=status_var, foreground="blue")
    status_lbl.pack(side=tk.LEFT)

    def start_translation():
        files = find_excel_files(selected_files, selected_folder.get(), recursive_var.get())
        if not files:
            messagebox.showwarning("No input", "Please select files and/or a folder with .xlsx files.")
            return
        sel_idx = columns_listbox.curselection()
        cols = (
            [columns_listbox.get(i) for i in sel_idx]
            if sel_idx
            else [columns_listbox.get(i) for i in range(columns_listbox.size())]
        )
        if not cols:
            messagebox.showwarning("No columns", "Please scan and select at least one column.")
            return
        sel_lang_idx = langs_listbox.curselection()
        sel_langs = [lang_codes[i] for i in sel_lang_idx]
        if not sel_langs:
            messagebox.showwarning("No languages", "Please select at least one target language.")
            return
        os.makedirs(output_dir.get(), exist_ok=True)

        total_files = 0
        total_attempted = 0
        total_changed = 0
        errors: list[str] = []

        for fpath in files:
            try:
                sheets = pd.read_excel(fpath, sheet_name=None)  # dict of {sheet_name: df}
                for sname, df in sheets.items():
                    stats = translate_dataframe_columns(df, cols, sel_langs)
                    total_attempted += stats["attempted"]
                    total_changed += stats["changed"]
                # Save with sheets preserved
                base = os.path.splitext(os.path.basename(fpath))[0]
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = os.path.join(output_dir.get(), f"{base}_translated_{ts}.xlsx")
                with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                    for sname, df in sheets.items():
                        df.to_excel(writer, sheet_name=sname, index=False)
                total_files += 1
                status_var.set(f"Saved: {out_path}")
                root.update_idletasks()
            except Exception as e:
                errors.append(f"{os.path.basename(fpath)}: {e}")

        # Summary
        coverage = (total_changed / total_attempted * 100.0) if total_attempted else 0.0
        summary = [
            f"Files processed: {total_files}",
            f"Cells translated (attempted): {total_attempted}",
            f"Cells changed: {total_changed}",
            f"Change rate (proxy for translation coverage): {coverage:.1f}%",
        ]
        if errors:
            summary.append("\nErrors:")
            summary.extend(errors[:10])  # show up to 10 errors
        messagebox.showinfo("Done", "\n".join(summary))
        status_var.set("Done")

    ttk.Button(actions, text="Translate", command=start_translation).pack(side=tk.RIGHT)
    ttk.Button(actions, text="Scan Columns", command=scan_columns).pack(side=tk.RIGHT, padx=6)

    root.minsize(820, 600)
    root.mainloop()
