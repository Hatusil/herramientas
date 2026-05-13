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
from ui.sidebar_helpers import create_tool_button, update_tool_buttons
from ui.sidebar_dialogs import show_acerca_de, show_salir

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Panel lateral con lista de herramientas."""
    
    def __init__(self, master, on_tool_select: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_tool_select = on_tool_select
        self.tool_buttons: Dict[str, ctk.CTkButton] = {}
        
        # Usar pack todo
        self.pack_propagate(False)
        
        # Logo (circular)
        logo_path = find_logo_path()
        logo = None
        if logo_path:
            try:
                circle_img = make_circle_image(logo_path, size=50)
                logo = ctk.CTkImage(light_image=circle_img, dark_image=circle_img, size=(50, 50))
            except Exception as e:
                logger.warning(f"Error cargando logo: {e}")
        
        if logo:
            logo_label = ctk.CTkLabel(self, image=logo, text="")
            logo_label.pack(pady=(5, 0))
            
            # Title debajo del logo
            title = ctk.CTkLabel(
                self, 
                text="Herramientas",
                font=ctk.CTkFont(size=constants.FONT_SIZE_TITLE, weight="bold")
            )
            title.pack(pady=(0, 2))
        else:
            # Sin logo, título al inicio
            title = ctk.CTkLabel(
                self, 
                text="Herramientas",
                font=ctk.CTkFont(size=constants.FONT_SIZE_TITLE, weight="bold")
            )
            title.pack(pady=(5, 2))
        
        # Botón Inicio para volver a pantalla de bienvenida
        self.inicio_btn = ctk.CTkButton(
            self,
            text="🏠 Inicio",
            command=self._on_inicio,
            fg_color=constants.COLORS.get("bg_medium", "#252525"),
            hover_color=constants.COLORS.get("primary", "#3b82f6"),
            text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
            height=30
        )
        self.inicio_btn.pack(fill="x", padx=10, pady=(8, 5))
        
        
        
        # Scrollable frame para las tools - expande
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            label_text="",
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Bindings para scroll
        self._setup_scroll_binding(self.scroll_frame)
        
        # Botón Acerca de - con mejor contraste
        acerca_btn = ctk.CTkButton(
            self,
            text="ℹ️ Acerca de",
            command=self._on_acerca_de,
            fg_color=constants.COLORS.get("bg_medium", "#252525"),
            text_color=constants.COLORS.get("text_primary", "#e0e0e0"),
            border_width=1,
            border_color=constants.COLORS.get("border", "#404040"),
            hover_color=constants.COLORS.get("primary", "#3b82f6"),
            height=36,
            font=font("small")
        )
        acerca_btn.pack(fill="x", padx=10, pady=(8, 0))
        try:
            from ui.tooltip import add_tooltip
            add_tooltip(acerca_btn, "Informacion sobre la aplicacion", 400)
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
        """Configura bindings de scroll con mouse wheel."""
        # Intentar obtener el canvas interno de forma robusta
        canvas = None
        
        # Método 1: attribute directo (CTkinter 4.x)
        try:
            canvas = getattr(scroll_frame, '_parent_canvas', None)
        except Exception:
            pass
        
        # Método 2: buscar en children (CTkinter 5.x compatibility)
        if not canvas:
            try:
                for child in scroll_frame.winfo_children():
                    if hasattr(child, 'yview'):
                        canvas = child
                        break
            except Exception:
                pass
        
        if not canvas:
            # Fallback: crear un binding directo
            try:
                scroll_frame.bind("<MouseWheel>", self._on_mousewheel)
                scroll_frame.bind("<Button-4>", self._on_mousewheel)
                scroll_frame.bind("<Button-5>", self._on_mousewheel)
            except Exception:
                pass
            return
        
        def on_wheel(event):
            if hasattr(event, 'num'):  # Linux
                direction = -1 if event.num == 4 else 1
            else:  # Windows
                direction = -1 if event.delta < 0 else 1
            # Scroll más rápido (3 líneas)
            for _ in range(3):
                canvas.yview("scroll", direction, "units")
            return "break"
        
        # Bind directo - funcionan en todo el sidebar
        scroll_frame.bind("<MouseWheel>", on_wheel)
        scroll_frame.bind("<Button-4>", on_wheel)
        scroll_frame.bind("<Button-5>", on_wheel)
    
    def _on_mousewheel(self, event) -> str:
        """Maneja scroll con la rueda del mouse - fallback."""
        try:
            # Obtener canvas de forma robusta
            canvas = None
            
            # Método 1: attribute directo
            if hasattr(self.scroll_frame, '_parent_canvas'):
                canvas = self.scroll_frame._parent_canvas
            
            # Método 2: buscar en children
            if not canvas:
                for child in self.scroll_frame.winfo_children():
                    if hasattr(child, 'yview'):
                        canvas = child
                        break
            
            if canvas:
                if hasattr(event, 'delta'):
                    direction = -1 if event.delta < 0 else 1
                else:
                    direction = -1 if event.num == 4 else 1
                canvas.yview("scroll", direction, "units")
        except Exception:
            pass
        return "break"
    
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
        # Actualizar sidebar principal
        if hasattr(self, 'master'):
            try:
                self.configure(fg_color=constants.COLORS.get("bg_medium", "#252525"))
            except Exception:
                pass
        
        # Actualizar scroll frame
        if hasattr(self, 'scroll_frame'):
            try:
                self.scroll_frame.configure(fg_color="transparent")
            except Exception:
                pass
        
        # Actualizar tool buttons
        update_tool_buttons(self.tool_buttons, getattr(self, '_selected_tool', None))
        
        # Actualizar control_frame (configuración)
        if hasattr(self, 'control_frame'):
            self.control_frame.configure(
                fg_color=constants.COLORS.get("bg_medium", "#252525"),
                border_color=constants.COLORS.get("border", "#404040")
            )
        
        # Actualizar label de configuración
        if hasattr(self, '_theme_label'):
            self._theme_label.configure(
                text=f"Modo: {'Claro' if constants.get_theme() == 'light' else 'Oscuro'}",
                text_color=constants.COLORS.get("text_secondary", "#9ca3af")
            )
        
        # Actualizar botón de inicio
        if hasattr(self, 'inicio_btn'):
            self.inicio_btn.configure(
                fg_color=constants.COLORS.get("bg_medium", "#252525"),
                hover_color=constants.COLORS.get("primary", "#3b82f6"),
                text_color=constants.COLORS.get("text_primary", "#e0e0e0")
            )
        
        # Actualizar botón Acerca de
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
        """Resalta el botón seleccionado. Si tool_name es None, deselecciona todos."""
        selected_color = constants.COLORS["primary"]
        normal_color = constants.COLORS["bg_light"]
        
        for name, btn in self.tool_buttons.items():
            if tool_name is not None and name == tool_name:
                btn.configure(fg_color=selected_color, text_color="white")
            else:
                btn.configure(fg_color=normal_color, text_color=constants.COLORS["text_secondary"])
    
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