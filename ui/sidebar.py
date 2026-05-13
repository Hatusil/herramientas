"""
Sidebar: Panel lateral de navegación de herramientas.
"""
import logging
import customtkinter as ctk
from typing import List, Dict, Callable, Any
from core import constants
from core.constants import font, FONT_SIZE_TITLE, FONT_SIZE_LARGE
from core import config
from ui.sidebar_helpers import create_tool_callback, make_circle_image, find_logo_path
from ui.sidebar_helpers import create_tool_button, update_tool_buttons, highlight_tool
from ui.sidebar_dialogs import show_acerca_de, show_salir
from ui.sidebar_setup import setup_logo, setup_title, setup_buttons

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Panel lateral con lista de herramientas."""
    
    def __init__(self, master, on_tool_select: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_tool_select = on_tool_select
        self.tool_buttons: Dict[str, ctk.CTkButton] = {}
        
        # Usar pack todo
        self.pack_propagate(False)
        
        # Logo y título
        logo_label = setup_logo(self)
        if logo_label:
            logo_label.pack(pady=(5, 0))
            setup_title(self)
        else:
            setup_title(self)
        
        # Botones
        setup_buttons(self, self._on_inicio, self._on_acerca_de)
        
        # Scrollable frame para tools
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="", fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)
        self._setup_scroll_binding(self.scroll_frame)
        except Exception as e:
            logger.warning(f"Error adding tooltip: {e}")
        
        # Botón de control (Salir + Theme Switch)
        self.control_frame = ctk.CTkFrame(
            self,
            fg_color=constants.COLORS.get("bg_medium", "#252525"),
            border_color=constants.COLORS.get("border", "#404040"),
            border_width=1
        )
        self.control_frame.pack(fill="x", padx=10, pady=10)
        
        # Título de sección
        config_label = ctk.CTkLabel(
            self.control_frame,
            text="CONFIGURACIÓN",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
            font=font("xsmall", "bold")
        )
        config_label.pack(fill="x", padx=12, pady=(10, 8))
        
        # Switch para cambio de tema
        self._theme_var = ctk.StringVar(value=constants.get_theme())
        self.theme_switch = ctk.CTkSwitch(
            self.control_frame,
            text="",
            command=self._on_toggle_theme,
            onvalue="light",
            offvalue="dark",
            variable=self._theme_var,
            text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
            fg_color=constants.COLORS.get("bg_hover", "#3d3d3d"),
            progress_color=constants.COLORS.get("primary", "#3b82f6")
        )
        self.theme_switch.pack(fill="x", padx=12, pady=(0, 8))
        
        # Label que muestra el estado actual
        self._theme_label = ctk.CTkLabel(
            self.control_frame,
            text=f"Modo: {'Claro' if constants.get_theme() == 'light' else 'Oscuro'}",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
            font=font("xsmall")
        )
        self._theme_label.pack(fill="x", padx=12, pady=(0, 8))
        
        # Divisor
        divisor = ctk.CTkFrame(
            self.control_frame,
            height=1,
            fg_color=constants.COLORS.get("border", "#404040")
        )
        divisor.pack(fill="x", padx=12, pady=8)
        
        # Botón Salir
        salir_btn = ctk.CTkButton(
            self.control_frame,
            text="Salir de la Aplicación",
            command=self._on_salir,
            fg_color=constants.COLORS.get("error", "#ef4444"),
            hover_color="#b91c1c",
            text_color="white",
            height=36,
            font=font("small", "bold")
        )
        salir_btn.pack(fill="x", padx=12, pady=(8, 12))
    
    def _setup_scroll_binding(self, scroll_frame) -> None:
        """Configura bindings de scroll."""
        from ui.sidebar_helpers import setup_scroll_binding
        setup_scroll_binding(scroll_frame, self._on_mousewheel)
    
    def _on_mousewheel(self, event) -> str:
        """Maneja scroll con mouse wheel."""
        from ui.sidebar_helpers import on_mousewheel
        canvas = None
        if hasattr(self.scroll_frame, '_parent_canvas'):
            canvas = self.scroll_frame._parent_canvas
        if not canvas:
            for child in self.scroll_frame.winfo_children():
                if hasattr(child, 'yview'):
                    canvas = child
                    break
        return on_mousewheel(event, canvas)
    
    def set_tools(self, tools: List[Dict[str, Any]]) -> None:
        """Configura las herramientas a mostrar."""
        for btn in self.tool_buttons.values():
            btn.destroy()
        self.tool_buttons.clear()
        
        # Crear botones de tools
        for tool in tools:
            name = tool['name']
            callback = create_tool_callback(name, self.on_tool_select)
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=f"{tool['icon']}  {tool['display_name']}",
                anchor="w",
                command=callback,
                height=50,
                fg_color=constants.COLORS["bg_light"],
                border_width=0,
                hover_color=constants.COLORS["primary_hover"],
                text_color=constants.COLORS["text_secondary"],
                font=ctk.CTkFont(size=constants.FONT_SIZE_LARGE)
            )
            btn.pack(fill="x", pady=4, padx=2)
            self.tool_buttons[name] = btn
        
        if tools:
            self._highlight_tool(tools[0]['name'])
    
    def update_theme(self) -> None:
        """Actualiza los colores del sidebar cuando cambia el tema."""
        from ui.sidebar_helpers import update_sidebar_theme
        update_sidebar_theme(self, self.scroll_frame, self.tool_buttons, getattr(self, '_selected_tool', None))
        
        # Botón Acerca de
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkButton) and child != self.inicio_btn:
                try:
                    child.configure(
                        fg_color=constants.COLORS.get("bg_medium", "#252525"),
                        text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
                        border_color=constants.COLORS.get("border", "#404040"),
                        hover_color=constants.COLORS.get("primary", "#3b82f6")
                    )
                except Exception:
                    pass
    
    def _highlight_tool(self, tool_name: str = None) -> None:
        """Resalta el botón seleccionado."""
        highlight_tool(self.tool_buttons, tool_name)
    
    def _on_salir(self) -> None:
        """Cierra la aplicación."""
        show_salir(self)
    
    def _on_inicio(self) -> None:
        """Vuelve a la pantalla de bienvenida."""
        # Notificar al app para que muestre la pantalla de inicio
        self.on_tool_select("__welcome__")
    
    def _on_toggle_theme(self) -> None:
        """Cambia entre tema oscuro y claro usando el switch."""
        new_theme = self.theme_switch.get()
        
        # Guardar en config (persistencia)
        config.save_theme(new_theme)
        
        # Actualizar constants
        constants.set_theme(new_theme)
        
        # Actualizar label con el modo actual
        self._theme_label.configure(
            text=f"Modo: {'Claro' if new_theme == 'light' else 'Oscuro'}",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        )
        
        # Notificar a la app principal para que refresque todos los widgets
        if hasattr(self.master, 'refresh_theme'):
            self.master.refresh_theme()
        
        # Forzar redibujado de la ventana
        self.master.update()
        
        logger.info(f"Tema cambiado a: {new_theme}")
    
    def _on_acerca_de(self) -> None:
        """Muestra diálogo Acerca de."""
        show_acerca_de(self)
        
        # Centrar en la pantalla (no relativo al padre)
        dialog.transient(self)
        self.update_idletasks()
        
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        
        dialog_w = 450
        dialog_h = 620
        
        x = (screen_w - dialog_w) // 2
        y = (screen_h - dialog_h) // 2
        
        dialog.geometry(f"+{x}+{y}")
        
        # Aplicar grab después de que renderice
        dialog.after(100, lambda: dialog.grab_set())
        
        # Cerrar con Escape
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        # Frame principal
        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Logo - buscar en varias ubicaciones
        base_paths = [
            Path(__file__).parent.parent,
            Path(sys.executable).parent,
        ]
        
        logo_ctk = None
        for base in base_paths:
            logo_path = base / "assets" / "logo.png"
            if logo_path.exists():
                try:
                    # make_circle_image está definida en este archivo
                    circle_img = make_circle_image(str(logo_path), size=80)
                    logo_ctk = ctk.CTkImage(
                        light_image=circle_img,
                        dark_image=circle_img,
                        size=(80, 80)
                    )
                except Exception as e:
                    logger.warning(f"Error creating logo: {e}")
                break
        
        if logo_ctk:
            ctk.CTkLabel(main, image=logo_ctk, text="").pack(pady=(10, 5))
        
        # Título
        ctk.CTkLabel(
            main,
            text="Herramientas",
            font=font("title", "bold")
        ).pack(pady=(0, 2))
        
        ctk.CTkLabel(
            main,
            text="Version 1.0.0",
            font=font("small"),
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        ).pack(pady=(0, 15))
        
        # Descripción personal
        desc_frame = ctk.CTkFrame(main, fg_color="transparent")
        desc_frame.pack(pady=5, padx=10)
        
        desc_text = """Soy un desarrollador de software y analista de datos que busca subordinar la técnica y las ciencias a la Verdad y la Sabiduría, para no ser esclavo de la máquina."""
        
        ctk.CTkLabel(
            desc_frame,
            text=desc_text,
            font=font("xsmall"),
            text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
            wraplength=380
        ).pack(pady=5)
        
        # Info contacto
        ctk.CTkLabel(
            main,
            text="Desarrollado por: Hatusil (Ewoc Logic)",
            font=font("small", "bold")
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            main,
            text="hatusil@proton.me",
            text_color=constants.COLORS.get("text_secondary", "#9ca3af"),
            font=font("xsmall")
        ).pack(pady=(2, 0))
        
        ctk.CTkLabel(
            main,
            text="github.com/Hatusil",
            text_color=constants.COLORS.get("primary", "#3b82f6")
        ).pack(pady=(2, 0))
        
        ctk.CTkLabel(
            main,
            text="☕ buymeacoffee.com/hatusil",
            text_color=constants.COLORS.get("warning", "#f59e0b")
        ).pack(pady=(2, 10))
        
        # Fecha de última actualización
        ahora = datetime.datetime.now()
        meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                  "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        ctk.CTkLabel(
            main,
            text=f"Última actualización: {meses[ahora.month-1]} {ahora.year}",
            font=font("xsmall"),
            text_color=constants.COLORS.get("text_secondary", "#9ca3af")
        ).pack(pady=(5, 0))
        
        # Copyright
        ctk.CTkLabel(
            main,
            text=f"© {datetime.datetime.now().year} - Todos los derechos reservados",
            font=font("small")
        ).pack(pady=(5, 0))
        
        # Separator
        sep = ctk.CTkFrame(main, height=1, fg_color="gray")
        sep.pack(fill="x", pady=12)
        
        # Herramientas título
        ctk.CTkLabel(
            main,
            text="Herramientas incluidas:",
            font=font("small", "bold")
        ).pack(pady=(5, 5))
        
        # Lista de tools
        tools_list = """Audio • Comprimir • Duplicados • GIF • Hash • Imagen
PDF • Renombrar • Scrubber • Search • Text Analyzer • Video"""
        
        ctk.CTkLabel(
            main,
            text=tools_list,
            font=font("small")
        ).pack(pady=5)
        
        # Separator
        sep2 = ctk.CTkFrame(main, height=1, fg_color="gray")
        sep2.pack(fill="x", pady=12)
        
        # Gracias
        ctk.CTkLabel(
            main,
            text="¡Gracias por usar esta herramienta!",
            text_color=constants.COLORS.get("success", "#22c55e")
        ).pack(pady=5)
        
        # Botón cerrar
        ctk.CTkButton(
            main,
            text="Cerrar",
            command=dialog.destroy,
            width=120,
            height=32
        ).pack(pady=10)