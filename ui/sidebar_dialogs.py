"""
Diálogos para Sidebar (Acerca de, configuración).
Cumple máxima A1 (una responsabilidad).
"""
import sys
import customtkinter as ctk
from pathlib import Path
from core import constants
from core.constants import font


def show_acerca_de(parent) -> None:
    """Muestra el diálogo Acerca de."""
    from ui.sidebar_helpers import make_circle_image
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Acerca de")
    dialog.geometry("450x620")
    
    dialog.transient(parent)
    parent.update_idletasks()
    
    screen_w = dialog.winfo_screenwidth()
    screen_h = dialog.winfo_screenheight()
    dialog_w, dialog_h = 450, 620
    x = (screen_w - dialog_w) // 2
    y = (screen_h - dialog_h) // 2
    dialog.geometry(f"+{x}+{y}")
    
    dialog.after(100, lambda: dialog.grab_set())
    dialog.bind("<Escape>", lambda e: dialog.destroy())

    # Colores del tema
    bg = constants.COLORS.get("bg_dark")
    fg = constants.COLORS.get("text_primary")
    fg_secondary = constants.COLORS.get("text_secondary")
    primary = constants.COLORS.get("primary")

    dialog.configure(fg_color=bg)

    main = ctk.CTkFrame(dialog, fg_color=bg)
    main.pack(fill="both", expand=True, padx=25, pady=25)
    
    # Logo
    base_paths = [Path(__file__).parent.parent, Path(sys.executable).parent]
    for base in base_paths:
        logo_path = base / "assets" / "logo.png"
        if logo_path.exists():
            try:
                circle_img = make_circle_image(str(logo_path), size=80)
                logo_ctk = ctk.CTkImage(light_image=circle_img, dark_image=circle_img, size=(80, 80))
                ctk.CTkLabel(main, image=logo_ctk, text="").pack(pady=(10, 5))
            except Exception:
                pass
            break
    
    # Título
    ctk.CTkLabel(main, text="Herramientas", font=font("title", "bold")).pack(pady=(0, 2))
    ctk.CTkLabel(main, text="Version 1.0.0", font=font("small"), text_color="gray").pack(pady=(0, 15))
    
    # Descripción
    desc = (
        "Aplicación de escritorio con múltiples herramientas\n"
        "de productividad para procesamiento de archivos.\n\n"
        "Construido con Python y CustomTkinter."
    )
    ctk.CTkLabel(main, text=desc, font=font("small"), justify="center").pack(pady=10)
    
    # Características
    features = [
        "🎵 Procesamiento de Audio",
        "🎬 Conversión de Video",
        "📄 Manipulación de PDF",
        "📊 Análisis de Texto",
        "🔍 Búsqueda de Archivos",
    ]
    for f in features:
        ctk.CTkLabel(main, text=f, font=font("small"), text_color="gray").pack(pady=2)
    
    # Tech stack
    ctk.CTkLabel(main, text="Stack: Python 3.11, CustomTkinter, PyInstaller",
                 font=font("xsmall"), text_color="gray").pack(pady=(20, 0))
    
    # Cerrar
    ctk.CTkButton(main, text="Cerrar", command=dialog.destroy, width=150).pack(pady=20)


def show_salir(parent) -> None:
    """Muestra diálogo de confirmación para salir."""
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Salir")
    dialog.geometry("300x150")
    dialog.transient(parent)
    parent.update_idletasks()

    # Centrar en pantalla
    screen_w = dialog.winfo_screenwidth()
    screen_h = dialog.winfo_screenheight()
    dialog_w, dialog_h = 300, 150
    x = (screen_w - dialog_w) // 2
    y = (screen_h - dialog_h) // 2
    dialog.geometry(f"+{x}+{y}")

    # Bloquear padre
    dialog.after(100, lambda: dialog.grab_set())
    dialog.bind("<Escape>", lambda e: dialog.destroy())

    bg = constants.COLORS.get("bg_dark")
    fg = constants.COLORS.get("text_primary")
    primary = constants.COLORS.get("primary")

    dialog.configure(fg_color=bg)

    ctk.CTkLabel(dialog, text="¿Querés salir de la aplicación?",
                 font=font("normal"), text_color=fg).pack(pady=20)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=10)

    ctk.CTkButton(btn_frame, text="Sí", command=parent.quit,
                  fg_color=constants.COLORS.get("error"), width=80).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="No", command=dialog.destroy,
                  fg_color=primary, width=80).pack(side="left", padx=5)