"""UI: Interfaz para Search Tool."""
import os
import logging
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from core.help_panel import add_help
from typing import Callable, Dict, Any, List

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI

logger = logging.getLogger(__name__)


class SearchToolUI(BaseToolUI):
    """UI para búsqueda avanzada de archivos."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__ but we skip file selector
        super().__init__(master, on_process, **kwargs)
        
        # Inicializar variables necesarias para search_tool
        self.folder = None
        self.results = []
        
        # Status label para search_tool
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=5)
        
        # Build rest of tool UI
        self._build_search_ui()
    
    def _get_file_label(self) -> str:
        """Override: Label for folder section."""
        return "Carpeta:"
    
    def _add_folder_custom(self) -> bool:
        """Override: Use custom folder selector."""
        return True  # We use label + button instead
    
    def _setup_ui(self) -> None:
        # NOTE: No usamos super()._setup_ui() porque search_tool tiene UI completamente custom
        # Solo inicializamos las variables que necesitamos
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="🔍 Buscador Avanzado",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(10, 5))
        
        # Help panel
        help_panel = add_help(
            self,
            description="🔍 Busca archivos por nombre, contenido (DOCX/PDF/XLSX/PPTX), fecha y extensión.",
            usage=[
                "1. Elegir carpeta a buscar",
                "2. Escribir patrón (ej: *.pdf, informe)",
                "3. Elegir modo: Contiene / Exacta / Regex",
                "4. Opcional: filtrar por ext o fecha",
                "5. BUSCAR → resultados",
                "6. Exportar a CSV/TXT"
            ],
            warnings=[
                "⚠️ Buscar en contenido es muy lento",
                "💡 Use *.pdf para buscar PDFs"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # Custom folder selector (skip BaseToolUI file selector)
        folder_btn_frame = ctk.CTkFrame(self)
        folder_btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.folder_label = ctk.CTkLabel(
            folder_btn_frame,
            text="Ninguna carpeta seleccionada",
            text_color="gray"
        )
        self.folder_label.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(
            folder_btn_frame,
            text="Elegir",
            command=self._select_folder,
            width=60
        ).pack(side="right")
        
        # Status label (from BaseToolUI)
    
    def _select_folder(self) -> None:
        """Select folder to search."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.folder = folder
            self.folder_label.configure(text=os.path.basename(folder))
            self.status_label.configure(text=f"Carpeta: {folder}")
    
    def _build_search_ui(self) -> None:
        """Build search-specific UI."""
        # Panel de opciones - usando grid para mejor responsividad
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="x", padx=10, pady=5)
        options_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # Columna 1: Búsqueda por nombre
        name_col = ctk.CTkFrame(options_frame)
        name_col.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            name_col,
            text="Buscar por nombre:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 2))
        
        self.name_entry = ctk.CTkEntry(name_col, placeholder_text="Patrón de búsqueda")
        self.name_entry.pack(fill="x", pady=2)
        
        # Opciones de búsqueda
        opts_row = ctk.CTkFrame(name_col, fg_color="transparent")
        opts_row.pack(fill="x", pady=2)
        
        self.name_mode = ctk.StringVar(value="contains")
        ctk.CTkRadioButton(opts_row, text="Contiene", variable=self.name_mode, value="contains").pack(side="left")
        ctk.CTkRadioButton(opts_row, text="Exacta", variable=self.name_mode, value="exact").pack(side="left")
        ctk.CTkRadioButton(opts_row, text="Regex", variable=self.name_mode, value="regex").pack(side="left")
        
        self.case_sensitive = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts_row, text="Aa", variable=self.case_sensitive).pack(side="left", padx=5)
        
        # Columna 2: Filtros
        filter_col = ctk.CTkFrame(options_frame)
        filter_col.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            filter_col,
            text="Filtros:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 2))
        
        # Extensiones
        ext_frame = ctk.CTkFrame(filter_col, fg_color="transparent")
        ext_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(ext_frame, text="Extensiones:", font=ctk.CTkFont(size=14)).pack(side="left")
        self.ext_entry = ctk.CTkEntry(ext_frame, placeholder_text="pdf,docx,xlsx")
        self.ext_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Fecha
        date_frame = ctk.CTkFrame(filter_col, fg_color="transparent")
        date_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(date_frame, text="Desde:", font=ctk.CTkFont(size=14)).pack(side="left")
        self.date_from = ctk.CTkEntry(date_frame, placeholder_text="dd/mm/aaaa", width=70)
        self.date_from.pack(side="left", padx=2)
        
        ctk.CTkLabel(date_frame, text="Hasta:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.date_to = ctk.CTkEntry(date_frame, placeholder_text="dd/mm/aaaa", width=70)
        self.date_to.pack(side="left", padx=2)
        
        # Contenido
        content_frame = ctk.CTkFrame(filter_col, fg_color="transparent")
        content_frame.pack(fill="x", pady=2)
        
        self.search_content = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(content_frame, text="Buscar en contenido", variable=self.search_content).pack(side="left")
        
        self.content_entry = ctk.CTkEntry(content_frame, placeholder_text="Buscar en archivos...")
        self.content_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botón buscar
        self.search_btn = ctk.CTkButton(
            self,
            text="🔍 BUSCAR",
            command=self._do_search,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.search_btn.pack(fill="x", padx=10, pady=10)
        
        # Botón detener (oculto inicialmente)
        self.stop_btn = ctk.CTkButton(
            self,
            text="⏹ DETENER",
            command=self._stop_search,
            height=40,
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stop_btn.pack(fill="x", padx=10, pady=10)
        self.stop_btn.pack_forget()  # Oculto inicialmente
        
        # Flag para detener búsqueda
        self._search_cancelled = False
        
        # Resultados - no expandir, altura fija
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            results_frame,
            text="Resultados:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        # Lista de resultados - altura reducida
        list_cont = ctk.CTkFrame(results_frame, fg_color="transparent")
        list_cont.pack(fill="x", padx=10, pady=2)
        
        self.results_listbox = tk.Listbox(list_cont, height=8, selectmode=tk.EXTENDED)
        scroll = tk.Scrollbar(list_cont, orient="vertical")
        self.results_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.results_listbox.yview)
        self.results_listbox.pack(side="left", fill="x", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Info de resultados
        self.results_info = ctk.CTkLabel(results_frame, text="", text_color="gray")
        self.results_info.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Botones de exportar
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(export_frame, text="📊 CSV", command=self._export_csv).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="📝 TXT", command=self._export_txt).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="📂 Abrir", command=self._open_selected).pack(side="left", padx=5)
    
    def _do_search(self) -> None:
        """Execute the search."""
        # Asegurar que status_label existe
        if not hasattr(self, 'status_label') or self.status_label is None:
            self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
            self.status_label.pack(pady=5)
        
        if not hasattr(self, 'folder') or not self.folder:
            self.status_label.configure(text="Seleccione una carpeta", text_color="#FFA500")
            return
        
        # Preparar opciones
        options = {
            'name_pattern': self.name_entry.get().strip(),
            'name_mode': self.name_mode.get(),
            'case_sensitive': self.case_sensitive.get(),
            'date_from': self.date_from.get().strip() or None,
            'date_to': self.date_to.get().strip() or None,
            'search_content': self.search_content.get(),
            'content_pattern': self.content_entry.get().strip() if self.search_content.get() else None,
        }
        
        # Extensiones
        ext_text = self.ext_entry.get().strip()
        if ext_text:
            options['extensions'] = [e.strip() for e in ext_text.split(',')]
        
        # Deshabilitar botón y mostrar estado
        self.search_btn.configure(state="disabled")
        self.stop_btn.pack()  # Mostrar botón detener
        self._search_cancelled = False
        self.status_label.configure(text="Buscando...", text_color="#FFD700")
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=self._search_worker, args=(options,))
        thread.daemon = True
        thread.start()
    
    def _stop_search(self) -> None:
        """Detiene la búsqueda en curso."""
        self._search_cancelled = True
        # También llamar a la función del processor para interrumpir el background worker
        from tools.search_tool.processor import cancel_search
        cancel_search()
        self.status_label.configure(text="Deteniendo...", text_color="#FFA500")
    
    def _search_worker(self, options: Dict[str, Any]) -> None:
        """Worker que ejecuta la búsqueda en background."""
        try:
            from tools.search_tool.processor import search_all
            result = search_all(self.folder, options)
            
            # Actualizar UI en thread principal
            self.after(0, lambda: self._search_complete(result))
        except Exception as e:
            self.after(0, lambda: self._search_error(str(e)))
    
    def _search_complete(self, result: Dict[str, Any]) -> None:
        """Called when search completes."""
        from tools.search_tool.processor import reset_search
        reset_search()
        
        self.search_btn.configure(state="normal")
        self.stop_btn.pack_forget()  # Ocultar botón detener
        self._search_cancelled = False
        
        # Verificar si fue cancelado
        if result.get('cancelled'):
            self.status_label.configure(text="Búsqueda cancelada", text_color="#FFA500")
            return
        
        if result['success']:
            self.results = result['results']
            self._show_results()
            count = result['count']
            content_count = len(result.get('content_matches', {}))
            
            msg = f"Encontrados: {count} archivos"
            if content_count > 0:
                msg += f" ({content_count} con contenido)"
            
            self.status_label.configure(text=msg, text_color="green")
        else:
            self.status_label.configure(
                text=result.get('error', 'Error'),
                text_color="red"
            )
    
    def _search_error(self, error: str) -> None:
        """Called when search fails."""
        from tools.search_tool.processor import reset_search
        reset_search()
        
        self.search_btn.configure(state="normal")
        self.stop_btn.pack_forget()  # Ocultar botón detener
        self.status_label.configure(text=f"Error: {error}", text_color="red")
    
    def _show_results(self) -> None:
        """Show search results."""
        self.results_listbox.delete(0, tk.END)
        
        for r in self.results:
            text = f"{r['name']} ({r['size']:,} bytes) - {r['modified']}"
            if r['matches'] > 0:
                text += f" [{r['matches']} matches]"
            self.results_listbox.insert(tk.END, text)
        
        self.results_info.configure(text=f"Total: {len(self.results)} archivos")
    
    def _export_csv(self) -> None:
        """Export results to CSV."""
        if not self.results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Guardar como CSV"
        )
        
        if file_path:
            from tools.search_tool.processor import export_to_csv
            if export_to_csv(self.results, file_path):
                messagebox.showinfo("Éxito", f"Resultados exportados a {file_path}")
            else:
                messagebox.showerror("Error", "No se pudo exportar")
    
    def _export_txt(self) -> None:
        """Export results to TXT."""
        if not self.results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("TXT", "*.txt")],
            title="Guardar como TXT"
        )
        
        if file_path:
            from tools.search_tool.processor import export_to_txt
            if export_to_txt(self.results, file_path):
                messagebox.showinfo("Éxito", f"Resultados exportados a {file_path}")
            else:
                messagebox.showerror("Error", "No se pudo exportar")
    
    def _open_selected(self) -> None:
        """Abre el archivo/directorio seleccionado con la app por defecto."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if 0 <= idx < len(self.results):
            file_path = self.results[idx]['path']
            
            if not os.path.exists(file_path):
                return
            
            # Cross-platform: abrir con app por defecto
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux/Mac
                import subprocess
                try:
                    if os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', file_path], check=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', file_path], check=True)
                except Exception as e:
                    logger.warning(f"Error opening file with default app: {e}")
                    try:
                        subprocess.run(['gio', 'open', file_path], check=True)
                    except Exception as e:
                        logger.warning(f"Error opening with gio: {e}")