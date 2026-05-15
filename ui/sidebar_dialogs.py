"""
Diálogos para Sidebar (Acerca de, configuración).
Cumple máxima A1 (una responsabilidad).
"""
import sys
import customtkinter as ctk
from pathlib import Path
from core.constants import font, COLORS
from ui.theme_factory import (
    create_frame, create_label, create_primary_button, create_danger_button
)


def show_acerca_de(parent) -> None:
    """Muestra el diálogo Acerca de."""
    from ui.sidebar_helpers import make_circle_image
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Acerca de")
    dialog.geometry("480x700")
    
    dialog.transient(parent)
    parent.update_idletasks()
    
    screen_w = dialog.winfo_screenwidth()
    screen_h = dialog.winfo_screenheight()
    dialog_w, dialog_h = 480, 700
    x = (screen_w - dialog_w) // 2
    y = (screen_h - dialog_h) // 2
    dialog.geometry(f"+{x}+{y}")
    
    dialog.after(100, lambda: [dialog.grab_set(), dialog.focus_set()])
    dialog.bind("<Escape>", lambda e: dialog.destroy())

    from core.constants import COLORS
    dialog.configure(fg_color=COLORS.get("bg_dark"))

    main = create_frame(dialog)
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
    
    # Título y versión
    create_label(main, text="Herramientas", font=font("title", "bold")).pack(pady=(0, 2))
    create_label(main, text="Versión 1.0.0", font=font("small"), text_color="secondary").pack(pady=(0, 15))

    # Descripción
    create_label(
        main,
        text="Aplicación de escritorio con múltiples herramientas\nde productividad para procesamiento de archivos.",
        font=font("small"), justify="center"
    ).pack(pady=(0, 5))
    create_label(
        main,
        text="Construido con Python y CustomTkinter.",
        font=font("xsmall"), text_color="secondary"
    ).pack(pady=(0, 15))

    # Separator
    ctk.CTkFrame(main, height=1, fg_color=COLORS.get("border")).pack(fill="x", pady=10)

    # Filosofía
    create_label(main, text="📜 Filosofía", font=font("small", "bold"), text_color="primary").pack(pady=(5, 5))
    frase = "«Soy un desarrollador de software y analista de datos que busca\nsubordinar la técnica y las ciencias a la Verdad y la Sabiduría,\npara no ser esclavo de la máquina.»"
    create_label(main, text=frase, font=font("xsmall"), text_color="secondary", justify="center").pack(pady=(5, 15))

    # Separator
    ctk.CTkFrame(main, height=1, fg_color=COLORS.get("border")).pack(fill="x", pady=5)

    # Contacto
    create_label(main, text="📬 Contacto", font=font("small", "bold"), text_color="primary").pack(pady=(5, 5))
    create_label(main, text="Hatusil (Ewoc Logic)", font=font("small")).pack(pady=(2, 0))
    create_label(main, text="hatusil@proton.me", font=font("small"), text_color="secondary").pack(pady=(2, 0))
    create_label(main, text="github.com/Hatusil", font=font("small"), text_color="primary").pack(pady=(2, 0))
    create_label(main, text="☕ buymeacoffee.com/hatusil", font=font("small"), text_color="secondary").pack(pady=(2, 15))

    # Cerrar
    create_primary_button(main, text="Cerrar", command=dialog.destroy, width=150).pack(pady=(10, 20))


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

    # Bloquear padre y enfocar
    dialog.after(100, lambda: [dialog.grab_set(), dialog.focus_set()])
    dialog.bind("<Escape>", lambda e: dialog.destroy())

    from core.constants import COLORS
    dialog.configure(fg_color=COLORS.get("bg_dark"))

    create_label(dialog, text="¿Querés salir de la aplicación?", font=font("normal")).pack(pady=20)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=10)

    # parent es Sidebar, parent.master es la App (que sí tiene quit)
    create_danger_button(btn_frame, text="Sí", command=parent.master.quit, width=80).pack(side="left", padx=5)
    create_primary_button(btn_frame, text="No", command=dialog.destroy, width=80).pack(side="left", padx=5)