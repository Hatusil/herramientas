"""tool_builder — Factory para UI estándar de herramientas."""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk

from core.help_panel import add_help
from core.constants import font


def create_standard_tool_ui(
    parent,
    icon_and_name,
    description,
    selector_type="file",
    tab_configs=None,
    help_config=None,
    file_types=None,
):
    """Crea y retorna los widgets estándar de una tool."""
    icon, name = icon_and_name
    hc = help_config or {}

    ctk.CTkLabel(
        parent, text=name, font=font("header", "bold")
    ).pack(pady=(0, 10))

    # Usar description del help_config si no viene como parámetro
    desc = description if description else hc.get("description", "")

    help_btn = None
    if desc or hc:
        help_btn = add_help(
            parent,
            title=hc.get("title", f"Ayuda - {name}"),
            description=desc,
            usage=hc.get("usage", []),
            tips=hc.get("tips", []),
            warnings=hc.get("warnings", []),
        )
        help_btn.pack(fill="x", padx=10, pady=5)

    file_selector = None
    files = []
    listbox = None
    status_label = None
    btn_frame = None
    add_folder = None
    get_selected = None

    if selector_type != "none":
        fs = _build_file_selector(
            parent,
            file_types,
            hc.get("custom_buttons"),
            hc.get("file_label"),
            hc.get("dialog_title"),
        )
        file_selector = fs["frame"]
        files = fs["files"]
        listbox = fs["listbox"]
        status_label = fs["status_label"]
        btn_frame = fs.get("btn_frame")
        add_folder = fs.get("add_folder")
        get_selected = fs.get("get_selected")

    tabview = None
    tabs = {}
    if tab_configs:
        tabview = ctk.CTkTabview(parent)
        tabview.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        for tc in tab_configs:
            tabs[tc["name"]] = tabview.add(tc["name"])

    return {
        "frame": parent,
        "file_selector": file_selector,
        "tabs": tabs,
        "help_button": help_btn,
        "tabview": tabview,
        "files": files,
        "listbox": listbox,
        "status_label": status_label,
        "btn_frame": btn_frame,
        "add_folder": add_folder,
        "get_selected": get_selected,
    }


def _build_file_selector(parent, file_types=None, custom_buttons=None,
                         file_label=None, dialog_title=None):
    """Crea el selector de archivos estándar."""
    if file_label is None:
        file_label = "Archivos:"
    if dialog_title is None:
        dialog_title = "Seleccionar archivos"

    files: List[str] = []
    ft = file_types or [("Todos los archivos", "*.*")]

    frame = ctk.CTkFrame(parent)
    frame.pack(fill="x", pady=(0, 10), padx=10)

    ctk.CTkLabel(
        frame, text=file_label, font=font("normal", "bold")
    ).pack(anchor="w", padx=10, pady=(10, 5))

    list_cont = ctk.CTkFrame(frame, fg_color="transparent")
    list_cont.pack(fill="both", expand=True, padx=10, pady=5)

    listbox = tk.Listbox(list_cont, height=3, selectmode=tk.EXTENDED)
    scrollbar = tk.Scrollbar(list_cont, orient="vertical")
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _add_files():
        selected = filedialog.askopenfilenames(title=dialog_title, filetypes=ft)
        for f in selected:
            if f not in files:
                files.append(f)
                listbox.insert(tk.END, Path(f).name)
        if selected:
            _update_status()

    def _add_folder():
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder and folder not in files:
            files.append(folder)
            listbox.insert(tk.END, f"\U0001F4C1 {Path(folder).name}")
            _update_status()

    def _clear_all():
        files.clear()
        listbox.delete(0, tk.END)
        status_label.configure(text="Lista vacía", text_color="gray")

    def _select_all():
        listbox.select_set(0, tk.END)
        _update_status()

    def _deselect_all():
        listbox.select_clear(0, tk.END)
        _update_status()

    def _get_selected():
        sel = listbox.curselection()
        return [files[i] for i in sel] if sel else []

    def _update_status():
        selected = _get_selected()
        total = len(files)
        if not selected:
            status_label.configure(text=f"{total} archivos (ninguno seleccionado)", text_color="gray")
        elif len(selected) == total:
            status_label.configure(text=f"{total} seleccionados", text_color="blue")
        else:
            status_label.configure(text=f"{len(selected)}/{total} seleccionados", text_color="blue")

    ctk.CTkButton(btn_frame, text="Agregar...", command=_add_files, height=35).pack(side="left", padx=2)
    ctk.CTkButton(btn_frame, text="\u2713 Todos", command=_select_all, height=35).pack(side="left", padx=2)
    ctk.CTkButton(btn_frame, text="\u2717 Ninguno", command=_deselect_all, height=35).pack(side="left", padx=2)
    ctk.CTkButton(btn_frame, text="\U0001F5D1\ufe0f", command=_clear_all, fg_color="#dc2626", width=40, height=35).pack(side="left", padx=2)

    if custom_buttons:
        for text, cmd, opts in custom_buttons:
            ctk.CTkButton(btn_frame, text=text, command=cmd, **opts).pack(side="left", padx=5)

    listbox.bind("<<ListboxSelect>>", lambda e: _update_status())

    status_label = ctk.CTkLabel(parent, text="", text_color="gray")
    status_label.pack(pady=5)

    _get_selected_ref = _get_selected

    return {
        "frame": frame, "files": files, "listbox": listbox,
        "status_label": status_label, "btn_frame": btn_frame,
        "add_folder": _add_folder, "get_selected": _get_selected_ref,
    }
