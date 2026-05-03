import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable
try:
    from ui.quick_selector import add_quick_buttons
except Exception as e:
    logger.warning(f"Could not import add_quick_buttons: {e}")
logger = logging.getLogger(__name__)


class GifToolUI(ctk.CTkFrame):
    """UI para crear GIFs animados."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.images: List[str] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(self, text="Creador de GIFs", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
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
        
        # Selector de imágenes
        self._setup_image_selector()
        
        # Opciones
        self._setup_options()
        
        # Botón crear
        ctk.CTkButton(self, text="🎬 Crear GIF", command=self._create_gif, height=40, font=ctk.CTkFont(size=14)).pack(pady=10)
        
        # Info
        self.info_text = ctk.CTkTextbox(self, width=400, height=100)
        self.info_text.pack(padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
    
    def _setup_image_selector(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(frame, text="Imágenes para el GIF (orden importa):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        list_cont = ctk.CTkFrame(frame, fg_color="transparent")
        list_cont.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.image_listbox = tk.Listbox(list_cont, height=5, selectmode=tk.EXTENDED)
        scroll = tk.Scrollbar(list_cont, orient="vertical")
        self.image_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.image_listbox.yview)
        self.image_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Agregar imágenes...", command=self._add_images).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Ordenar ↑", command=self._move_up).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Ordenar ↓", command=self._move_down).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Limpiar", command=self._clear_images).pack(side="left", padx=5)
    
    def _add_images(self) -> None:
        files = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"), ("Todos", "*.*")]
        )
        
        for f in files:
            if f not in self.images:
                self.images.append(f)
                self.image_listbox.insert(tk.END, Path(f).name)
    
    def _move_up(self) -> None:
        selection = self.image_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        self.images[idx], self.images[idx-1] = self.images[idx-1], self.images[idx]
        
        self._refresh_list()
        self.image_listbox.selection_set(idx-1)
    
    def _move_down(self) -> None:
        selection = self.image_listbox.curselection()
        if not selection or selection[0] >= len(self.images) - 1:
            return
        
        idx = selection[0]
        self.images[idx], self.images[idx+1] = self.images[idx+1], self.images[idx]
        
        self._refresh_list()
        self.image_listbox.selection_set(idx+1)
    
    def _refresh_list(self) -> None:
        self.image_listbox.delete(0, tk.END)
        for f in self.images:
            self.image_listbox.insert(tk.END, Path(f).name)
    
    def _clear_images(self) -> None:
        self.images.clear()
        self.image_listbox.delete(0, tk.END)
    
    def _setup_options(self) -> None:
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
    
    def _create_gif(self) -> None:
        if len(self.images) < 2:
            self.status_label.configure(text="Necesitas al menos 2 imágenes", text_color="#FFA500")
            return
        
        duration = int(self.duration_var.get())
        loop = int(self.loop_var.get())
        
        self.status_label.configure(text="Creando GIF...", text_color="blue")
        
        from tools.gif_tool.processor import create_gif
        
        result = create_gif(self.images, duration=duration, loop=loop)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", f"✅ GIF creado exitosamente!\n\nArchivos: {len(self.images)}\nDuración: {duration}ms por frame\nLoop: {'infinito' if loop == 0 else loop}")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")