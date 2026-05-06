"""UI: Interfaz para crear GIFs animados."""
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import List, Callable

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI

logger = logging.getLogger(__name__)


class GifToolUI(BaseToolUI):
    """UI para crear GIFs animados."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__ which calls _setup_ui()
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific UI after base selector
        self._setup_options()
    
    def _get_file_label(self) -> str:
        """Override: Label for images section."""
        return "Imágenes para el GIF (orden importa):"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filters for image files."""
        return [
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"),
            ("Todos", "*.*")
        ]
    
    def _get_custom_buttons(self) -> List[tuple]:
        """Override: Custom buttons for sorting images."""
        return [
            ("Ordenar ↑", self._move_up, {"width": 70}),
            ("Ordenar ↓", self._move_down, {"width": 70}),
        ]
    
    def _setup_ui(self) -> None:
        # Title
        title = ctk.CTkLabel(
            self,
            text="Creador de GIFs",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Help panel
        help_panel = add_help(
            self,
            description="🎞️ Crea GIFs animados de secuencias de imágenes (PNG/JPG/BMP/WEBP). Controla duración y repeticiones",
            usage=[
                "1. 📥 Agregar imágenes en orden de animación",
                "2. ↕️ Reordenar frames si es necesario",
                "3. ⏱️ Configurar duración (100-1000ms)",
                "4. 🔄 Elegir repeticiones (infinito/1/3)",
                "5. ▶️ Click en 'Crear GIF'"
            ],
            warnings=[
                "⚠️ Se necesitan al menos 2 imágenes",
                "⚠️ Todas las imágenes deben tener mismo tamaño",
                "⚠️ GIFs ilimitados pueden ser muy grandes"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI sets self.status_label)
    
    def _move_up(self) -> None:
        """Move selected image up in list."""
        selection = self.file_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        self.files[idx], self.files[idx-1] = self.files[idx-1], self.files[idx]
        self._refresh_list()
        self.file_listbox.selection_set(idx-1)
    
    def _move_down(self) -> None:
        """Move selected image down in list."""
        selection = self.file_listbox.curselection()
        if not selection or selection[0] >= len(self.files) - 1:
            return
        
        idx = selection[0]
        self.files[idx], self.files[idx+1] = self.files[idx+1], self.files[idx]
        self._refresh_list()
        self.file_listbox.selection_set(idx+1)
    
    def _refresh_list(self) -> None:
        """Refresh the file listbox display."""
        self.file_listbox.delete(0, tk.END)
        for f in self.files:
            self.file_listbox.insert(tk.END, Path(f).name)
    
    def _setup_options(self) -> None:
        """Build GIF-specific options."""
        opts_frame = ctk.CTkFrame(self)
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        # Duración
        dur_frame = ctk.CTkFrame(opts_frame)
        dur_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dur_frame, text="Duración por frame (ms):").pack(side="left", padx=5)
        self.duration_var = ctk.StringVar(value="500")
        
        for val, label in [("100", "100ms (rápido)"), ("200", "200ms"), ("500", "500ms (normal)"), ("1000", "1s (lento)")]:
            RadioButton(dur_frame, text=label, variable=self.duration_var, value=val).pack(side="left", padx=5)
        
        # Loop
        loop_frame = ctk.CTkFrame(opts_frame)
        loop_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(loop_frame, text="Repeticiones:").pack(side="left", padx=5)
        self.loop_var = ctk.StringVar(value="0")
        
        RadioButton(loop_frame, text="Infinito", variable=self.loop_var, value="0").pack(side="left", padx=5)
        RadioButton(loop_frame, text="1 vez", variable=self.loop_var, value="1").pack(side="left", padx=5)
        RadioButton(loop_frame, text="3 veces", variable=self.loop_var, value="3").pack(side="left", padx=5)
        
        # Botón crear
        ctk.CTkButton(self, text="🎬 Crear GIF", command=self._create_gif, height=40, font=ctk.CTkFont(size=14)).pack(pady=10)
        
        # Info
        self.info_text = ctk.CTkTextbox(self, width=400, height=100)
        self.info_text.pack(padx=10, pady=10)
    
    def _create_gif(self) -> None:
        """Create the GIF from selected images."""
        if not self._check_files() or len(self.files) < 2:
            self.status_label.configure(text="Necesitas al menos 2 imágenes", text_color="#FFA500")
            return
        
        duration = int(self.duration_var.get())
        loop = int(self.loop_var.get())
        
        self.status_label.configure(text="Creando GIF...", text_color="#FFD700")
        
        from tools.gif_tool.processor import create_gif
        
        result = create_gif(self.files, duration=duration, loop=loop)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", f"✅ GIF creado exitosamente!\n\nArchivos: {len(self.files)}\nDuración: {duration}ms por frame\nLoop: {'infinito' if loop == 0 else loop}")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")