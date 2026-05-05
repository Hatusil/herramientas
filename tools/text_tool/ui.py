import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, Any
import time

logger = logging.getLogger(__name__)
class TextAnalyzerUI(ctk.CTkFrame):
    """UI para análisis de texto."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.text_content: str = ""
        self.sources: Dict[str, Any] = {"text": [], "files": [], "urls": []}
        
        # Phase 1: Centralized state management
        self._state: Dict[str, Any] = {
            'text': "",
            'file_path': None,
            'last_analysis': None,
            'progress': None,
            'thread_running': False,
            'has_text': False,
            'current_tab': "📥 Entrada"
        }
        
        # Phase 2: Threading and progress
        self.executor = ThreadPoolExecutor(max_workers=1)  # Single analysis at a time
        self._progress_start_time: float = 0
        self._progress_threshold = 2.0  # 2-second threshold
        
        self._setup_ui()
    
    # ============ STATE MANAGEMENT (Phase 1) ============
    def _update_state(self, **kwargs) -> None:
        """Update state dictionary with provided key-value pairs."""
        for key, value in kwargs.items():
            self._state[key] = value
    
    def _get_state(self, key: str, default: Any = None) -> Any:
        """Get state value with optional default."""
        return self._state.get(key, default)
    
    def _check_has_text(self) -> bool:
        """Check if text content is available."""
        return bool(self.text_content and self.text_content.strip())
    
    def _on_tab_change(self, tab_name: str) -> None:
        """Track current tab."""
        self._state['current_tab'] = tab_name
    
    # ============ PROGRESS BAR + THREADING (Phase 2) ============
    # Progress callback for long-running operations
    def _progress_callback(self, progress: float) -> None:
        """Callback for progress updates from analysis functions.
        
        Args:
            progress: Progress value 0.0 to 1.0
        """
        if self._get_state('thread_running'):
            # Schedule UI update on main thread
            self.after(0, lambda p=progress: self._update_progress_value(p))
    
    def _update_progress_value(self, progress: float) -> None:
        """Update progress bar value on main thread."""
        if self._get_state('thread_running'):
            self.progress_bar.set(min(max(progress, 0), 1))
            self._update_state(progress=int(progress * 100))
    
    def _show_progress(self) -> None:
        """Show progress bar widget."""
        self.progress_bar.pack(pady=(0, 5))
        self.progress_bar.configure(progress_color="blue")
    
    def _hide_progress(self) -> None:
        """Hide progress bar widget."""
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()
    
    def _update_progress_indeterminate(self) -> None:
        """Show indeterminate progress animation."""
        self.progress_bar.configure(progress_color="blue")
        # Animate indeterminate mode (oscillating)
        def animate():
            if self._get_state('thread_running'):
                # Oscillate between 0.2 and 0.8
                import random
                self.progress_bar.set(0.2 + random.random() * 0.6)
                self.after(200, animate)
        animate()
    
    def _run_in_thread(self, analysis_fn: Callable, *args, **kwargs) -> None:
        """Execute analysis function in background thread with progress tracking.
        
        Args:
            analysis_fn: The analysis function to run
            *args: Positional arguments for analysis_fn
            **kwargs: Keyword arguments for analysis_fn
            
        Returns:
            None: Result handled via callback pattern
        """
        # Check if thread already running
        if self._get_state('thread_running'):
            self.status_label.configure(text="Análisis en progreso...", text_color="orange")
            return
        
        # Mark thread as running
        self._update_state(thread_running=True)
        
        # Record start time for threshold check
        start_time = time.time()
        self._progress_start_time = start_time
        
        # Schedule progress bar after threshold (2 seconds)
        self.after(int(self._progress_threshold * 1000), lambda: self._check_show_progress(start_time))
        
        def worker():
            """Background worker function."""
            try:
                # Execute analysis
                result = analysis_fn(*args, **kwargs)
                
                # Calculate elapsed time
                elapsed = time.time() - start_time
                
                # Schedule result handling on main thread
                self.after(0, lambda r=result, e=elapsed: self._handle_thread_result(r, e))
            except Exception as e:
                import traceback
                logger.error(f"Thread error: {e}")
                traceback.print_exc()
                self.after(0, lambda: self._handle_thread_error(str(e)))
        
        # Submit to thread pool
        self.executor.submit(worker)
    
    def _check_show_progress(self, start_time: float) -> None:
        """Check if operation is taking longer than threshold - show progress bar."""
        if self._get_state('thread_running') and start_time == self._progress_start_time:
            elapsed = time.time() - start_time
            if elapsed >= self._progress_threshold:
                self._show_progress()
                self._update_progress_indeterminate()
    
    def _handle_thread_result(self, result: Dict[str, Any], elapsed: float) -> None:
        """Handle analysis result from background thread."""
        # Hide progress bar
        self._hide_progress()
        
        # Reset thread state
        self._update_state(thread_running=False, progress=None)
        
        # Process result
        if result:
            self._process_analysis_result(result)
        
        # Update status
        self.status_label.configure(text=f"Análisis completado en {elapsed:.1f}s", text_color="green")
    
    def _handle_thread_error(self, error_msg: str) -> None:
        """Handle error from background thread."""
        self._hide_progress()
        self._update_state(thread_running=False, progress=None)
        self.status_label.configure(text=f"Error: {error_msg}", text_color="red")
    
    def _process_analysis_result(self, result: Dict[str, Any]) -> None:
        """Process and display analysis result based on type."""
        # This is a placeholder - actual display logic is in individual methods
        # The calling code determines what result to display
        pass
    
    def _cleanup_thread(self) -> None:
        """Clean up thread state on completion or error."""
        self._hide_progress()
        self._update_state(thread_running=False, progress=None)
    
    # ============ PHASE 3: KEYBOARD SHORTCUTS + DRAG-DROP ============
    def _on_paste(self, event=None):
        """Handle Ctrl+V paste from clipboard into text area."""
        try:
            # Get clipboard content
            clipboard_text = self.clipboard_get()
            if clipboard_text and clipboard_text.strip():
                # Insert at cursor position
                self.text_input_area.insert(tk.INSERT, clipboard_text)
                # Update state
                current_text = self.text_input_area.get("1.0", tk.END).strip()
                self._update_state(text=current_text, has_text=bool(current_text))
                self.status_label.configure(text=f"Pegado: {len(clipboard_text)} caracteres", text_color="green")
        except tk.TclError:
            # Clipboard is empty or contains non-text data
            self.status_label.configure(text="Clipboard vacío o no texto", text_color="orange")
        return "break"  # Prevent default paste behavior
    
    def _on_open_file(self, event=None):
        """Handle Ctrl+O to open file dialog."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Texto", "*.txt *.md"),
                ("Documentos", "*.pdf *.docx *.doc"),
                ("Todos", "*.*")
            ]
        )
        if files:
            self._load_files(files)
        return "break"
    
    def _on_save_file(self, event=None):
        """Handle Ctrl+S to save current text to file."""
        # Get current text to save (prefer cleaned content if available)
        text_to_save = self.cleaned_content if self.cleaned_content else self.text_content
        
        if not text_to_save:
            self.status_label.configure(text="No hay texto para guardar", text_color="orange")
            return "break"
        
        # Get initial directory from current file_path if exists
        initial_dir = ""
        initial_file = "texto_guardado.txt"
        
        current_path = self._get_state('file_path')
        if current_path:
            initial_dir = os.path.dirname(current_path)
            initial_file = os.path.basename(current_path)
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".txt",
            filetypes=[
                ("Texto", "*.txt"),
                ("Markdown", "*.md"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_to_save)
                
                # Update state with new file path
                self._update_state(file_path=file_path)
                
                self.status_label.configure(
                    text=f"Guardado: {len(text_to_save)} caracteres en {os.path.basename(file_path)}",
                    text_color="green"
                )
            except Exception as e:
                logger.error(f"Error guardando archivo: {e}")
                self.status_label.configure(text=f"Error al guardar: {e}", text_color="red")
        
        return "break"
    
    def _load_files(self, files: tuple) -> None:
        """Load files and update state. Called by Ctrl+O and drag-drop."""
        try:
            from tools.text_tool.processor import extract_text_from_file
            
            all_text = []
            for f in files:
                result = extract_text_from_file(f)
                if result.get('success'):
                    all_text.append(result['text'])
            
            if all_text:
                new_text = '\n\n'.join(all_text)
                if self.text_content:
                    self.text_content += '\n\n' + new_text
                else:
                    self.text_content = new_text
                
                self.sources["files"].extend(files)
                self.cleaned_content = None
                self._update_sources_summary()
                self._update_files_display()
                
                # State update
                self._update_state(
                    text=self.text_content,
                    file_path=files[0] if files else None,
                    has_text=bool(self.text_content)
                )
                self.status_label.configure(
                    text=f"{len(files)} archivos: {len(self.text_content)} caracteres",
                    text_color="green"
                )
                # Switch to text mode to show loaded content
                self.input_type.set("text")
                self._on_input_type_change()
        except ImportError:
            self.status_label.configure(
                text="Installa dependencias: pip install wordcloud nltk pdfplumber",
                text_color="red"
            )
    
    def _on_run_analysis(self, event=None):
        """Handle Ctrl+Enter to run analysis on current tab."""
        current_tab = self._get_state('current_tab')
        
        # Check if on input tab - run load
        if current_tab == "📥 Entrada":
            self._load_and_analyze()
        # Check if on clean tab - run all analysis
        elif current_tab == "⚙️ Limpieza":
            if self._check_text_size(show_warning=True):
                self._apply_clean()
                self._run_all_analysis()
        else:
            # Try to run analysis on current tab
            self.status_label.configure(text=f"Ejecutando análisis en {current_tab}...", text_color="blue")
        
        return "break"
    
    def _on_cancel_analysis(self, event=None):
        """Handle Escape to cancel running analysis."""
        if self._get_state('thread_running'):
            self._update_state(thread_running=False, progress=None)
            self._hide_progress()
            self.status_label.configure(text="Análisis cancelado", text_color="orange")
            # Note: Thread continues in background but UI state is reset
        else:
            # If no analysis running, maybe close popup or clear input
            pass
        return "break"
    
    def _on_file_drop(self, event):
        """Handle file drop on text input area (drag-drop support)."""
        # Get dropped files from event data
        files = self.tk.splitlist(event.data) if hasattr(event, 'data') else ()
        
        if files:
            # Filter for supported file types
            supported_exts = {'.txt', '.md', '.pdf', '.docx', '.doc'}
            valid_files = [f for f in files if Path(f).suffix.lower() in supported_exts]
            
            if valid_files:
                self._load_files(tuple(valid_files))
            else:
                # Show error for unsupported files
                if files:
                    ext = Path(files[0]).suffix.lower()
                    self.status_label.configure(
                        text=f"Tipo de archivo no soportado: {ext}",
                        text_color="red"
                    )
        return "break"
    
    def _on_url_drop(self, event):
        """Handle URL drop on text input area (drag-drop support)."""
        # URL drops come as text data
        try:
            url_text = event.data if hasattr(event, 'data') else ""
            if url_text and url_text.startswith(('http://', 'https://')):
                # Add to URL entry
                self.input_type.set("url")
                self._on_input_type_change()
                
                # Clear existing and add the URL
                for row, entry in self.url_entries:
                    entry.delete(0, tk.END)
                self.url_entries = []
                self._add_url_field()
                self.url_entries[0][1].insert(0, url_text)
                
                self.status_label.configure(
                    text=f"URL detectada: {url_text[:50]}...",
                    text_color="green"
                )
        except Exception as e:
            logger.error(f"URL drop error: {e}")
        return "break"
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Bind keyboard shortcuts to text input area."""
        # Ctrl+V - paste
        self.text_input_area.bind('<Control-v>', self._on_paste)
        
        # Ctrl+O - open file
        self.text_input_area.bind('<Control-o>', self._on_open_file)
        
        # Ctrl+S - save file
        self.text_input_area.bind('<Control-s>', self._on_save_file)
        
        # Ctrl+Enter - run analysis
        self.bind('<Control-Return>', self._on_run_analysis)
        
        # Escape - cancel analysis
        self.bind('<Escape>', self._on_cancel_analysis)
        
        # For drag-drop, try to register as drop target (Tkinter dnd)
        # Note: CTkTextbox doesn't support Tkinter dnd, so we skip this silently
        try:
            if hasattr(self.text_input_area, 'drop_target_register'):
                # Register for file drops
                self.text_input_area.drop_target_register('DND_Files')
                self.text_input_area.dnd_bind('<<Drop>>', self._on_file_drop)
        except (tk.TclError, AttributeError):
            # CTkTextbox doesn't support Tkinter dnd, or TclError
            pass
    
    def _update_help_with_shortcuts(self) -> None:
        """Update help panel description with new keyboard shortcuts."""
        # This updates the help panel text at initialization
        new_tips = [
            "💡 WordCloud: usá los controles para cambiar cantidad de palabras, colormap, márgenes y forma",
            "💡 Frequency/N-grams: usá los sliders para ver más resultados",
            "💡 Gráficos: click para abrir en ventana grande, usá scroll para zoom",
            "💡 Atajos: Ctrl+V=paste, Ctrl+O=abrir, Ctrl+S=guardar, Ctrl+Enter=analizar, Escape=cancelar"
        ]
        
        # Update the help panel if it exists
        if hasattr(self, '_help_panel'):
            # Help panel is set up in _setup_ui - we can modify tips there
            pass  # Tips are passed in add_help call
    
    def _setup_ui(self) -> None:
        # Título
        title = ctk.CTkLabel(
            self, 
            text="📊 Text Analyzer", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(10, 5))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="📊 Analiza texto: WordCloud, frecuencia, estadísticas, n-grams, Trends, Correlaciones, Scatter. Soporta texto, archivos (TXT/MD/PDF/DOCX) o URLs",
            usage=[
                "1. Elegir tipo: Texto/Archivo/URL",
                "2. Ingresar o seleccionar contenido",
                "3. Click en 'Cargar y Analizar'",
                "4. Ver resultados en las solapas:",
                "   ☁️ WordCloud - nube de palabras personalizable",
                "   📈 Frecuencia - palabras más usadas (slider 20-100)",
                "   📉 Stats - estadísticas del texto",
                "   🔗 N-grams - frases repetidas (slider 20-100)",
                "   📊 Trends - frecuencia por secciones",
                "   🔥 Correlaciones - palabras que van juntas",
                "   ⬡ Scatter - distribución de términos",
                "5. Click en cualquier gráfico para ver en ventana emergente",
                "   - Scroll = zoom (0.5x a 5x)",
                "   - Arrastrar = mover imagen",
                "   - Exportar como PNG o PDF"
            ],
            tips=[
                "💡 WordCloud: usá los controles para cambiar cantidad de palabras, colormap, márgenes y forma",
                "💡 Frequency/N-grams: usá los sliders para ver más resultados",
                "💡 Gráficos: click para abrir en ventana grande, usá scroll para zoom",
                "💡 Atajos: Ctrl+V=paste, Ctrl+O=abrir, Ctrl+S=guardar, Ctrl+Enter=analizar, Escape=cancelar",
                "💡 Arrastrá archivos .txt/.md/.pdf sobre el área de texto para cargarlos"
            ],
            warnings=[
                "⚠️ Trends/Correlations/Scatter requieren texto largo (>200 palabras)",
                "⚠️ URL scraping puede fallar con anti-bot",
                "⚠️ Textos muy grandes (>100KB) son lentos"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab: Entrada
        self.tab_input = self.tabview.add("📥 Entrada")
        
        # Tab: Limpieza (move UP to be second)
        self.tab_clean = self.tabview.add("⚙️ Limpieza")
        
        # Tab: WordCloud
        self.tab_wc = self.tabview.add("☁️ WordCloud")
        
        # Tab: Frecuencia  
        self.tab_freq = self.tabview.add("📈 Frecuencia")
        
        # Tab: stats
        self.tab_stats = self.tabview.add("📉 Stats")
        
        # Tab: N-grams
        self.tab_ngram = self.tabview.add("🔗 N-grams")
        
        # Tab: Trends
        self.tab_trends = self.tabview.add("📊 Trends")
        
        # Tab: Correlations
        self.tab_corr = self.tabview.add("🔥 Correlaciones")
        
        # Tab: Scatter
        self.tab_scatter = self.tabview.add("⬡ Scatter")
        
        # Tab: KWIC (Contexts)
        self.tab_kwic = self.tabview.add("🔍 Contextos (KWIC)")
        
        # Tab: Topics (LDA)
        self.tab_topics = self.tabview.add("📚 Temas (LDA)")
        
        # Tab: WordTree (Árbol de Palabras)
        self.tab_wordtree = self.tabview.add("🌳 Árbol de Palabras")
        
        # Set up cada tab
        self._setup_input_tab()
        self._setup_clean_tab()
        self._setup_wc_tab()
        self._setup_freq_tab()
        self._setup_stats_tab()
        self._setup_ngram_tab()
        self._setup_trends_tab()
        self._setup_corr_tab()
        self._setup_scatter_tab()
        self._setup_kwic_tab()
        self._setup_topics_tab()
        self._setup_wordtree_tab()
    
    # ============ TAB: LIMPIEZA ============
    def _setup_clean_tab(self) -> None:
        frame = self.tab_clean
        
        # ==================== SECCIÓN: FUENTES ====================
        self.sources_summary = ctk.CTkLabel(
            frame,
            text="📁 Sin contenido cargado",
            font=ctk.CTkFont(size=14)
        )
        self.sources_summary.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Botones para quitar fuentes
        remove_frame = ctk.CTkFrame(frame)
        remove_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar Textos",
            command=lambda: self._remove_source("text"),
            fg_color="#c44"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar Archivos",
            command=lambda: self._remove_source("files"),
            fg_color="#c44"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            remove_frame,
            text="❌ Quitar URLs",
            command=lambda: self._remove_source("urls"),
            fg_color="#c44"
        ).pack(side="left", padx=2)
        
        # ==================== SECCIÓN: OPCIONES DE LIMPIEZA ====================
        opts_section = ctk.CTkLabel(frame, text="⚙️ OPCIONES DE LIMPIEZA", font=ctk.CTkFont(size=14, weight="bold"))
        opts_section.pack(anchor="w", padx=10, pady=(15, 5))
        
        opts_frame = ctk.CTkFrame(frame)
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        # Checkbox stopwords
        self.remove_stopwords = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts_frame, text="Quitar conectores (stopwords)", variable=self.remove_stopwords).pack(anchor="w", padx=5, pady=3)
        
        # Entry excluir palabras
        ctk.CTkLabel(opts_frame, text="Excluir palabras (separadas por coma):").pack(anchor="w", padx=5, pady=(5, 0))
        self.exclude_entry = ctk.CTkEntry(opts_frame, placeholder_text="ej: palabra1, palabra2, palabra3")
        self.exclude_entry.pack(fill="x", padx=5, pady=5)
        
        # Botones de acción - alternables
        action_frame = ctk.CTkFrame(frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        # Botón Preview Texto Bruto (sin filtros)
        self.preview_raw_btn = ctk.CTkButton(
            action_frame,
            text="👁 Preview Texto Bruto",
            command=self._preview_raw_text,
            width=180,
            fg_color="#888",
            hover_color="#666"
        )
        self.preview_raw_btn.pack(side="left", padx=5)
        
        # Botón Aplicar Limpieza (con filtros)
        self.apply_clean_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Aplicar Limpieza",
            command=self._apply_clean,
            width=180,
            fg_color="#48a",
            hover_color="#386"
        )
        self.apply_clean_btn.pack(side="left", padx=5)
        
        # ==================== SECCIÓN: RESULTADOS ====================
        results_section = ctk.CTkLabel(frame, text="✅ RESULTADOS", font=ctk.CTkFont(size=14, weight="bold"))
        results_section.pack(anchor="w", padx=10, pady=(15, 5))
        
        # Preview texto limpio
        clean_label = ctk.CTkLabel(frame, text="Texto limpio (preview):", font=ctk.CTkFont(size=12))
        clean_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.clean_text = ctk.CTkTextbox(frame, wrap="word")
        self.clean_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top 20 palabras
        top_words_label = ctk.CTkLabel(frame, text="Top 20 palabras:", font=ctk.CTkFont(size=12))
        top_words_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.clean_freq_text = ctk.CTkTextbox(frame, wrap="word", font=("Courier New", 11))
        self.clean_freq_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ==================== BOTÓN PRINCIPAL ====================
        # Destacado y visible
        ctk.CTkButton(
            frame,
            text="📊 GENERAR VISUALIZACIONES Y ANÁLISIS",
            command=self._run_all_analysis,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#e62",
            hover_color="#c50"
        ).pack(fill="x", padx=10, pady=(20, 10))
    
    def _preview_raw_text(self) -> None:
        """Muestra preview del texto en bruto (sin aplicar filtros)."""
        if not self.text_content:
            self.status_label.configure(text="Primero cargá texto", text_color="orange")
            return
        
        # Mostrar texto en bruto
        self.clean_text.delete("1.0", tk.END)
        self.clean_text.insert("1.0", self.text_content[:2000])
        
        # Top 20 palabras del texto original (sin filtros)
        from collections import Counter
        words = self.text_content.lower().split()
        word_freq = Counter(words)
        top_20 = word_freq.most_common(20)
        
        max_count = top_20[0][1] if top_20 else 1
        # Calculate dynamic width for proper alignment
        max_word_len = max(len(word) for word, _ in top_20) if top_20 else 10
        text_width = max(15, max_word_len + 2)
        
        texto = "📊 Top 20 palabras (texto bruto - sin filtros):\n"
        texto += "=" * (text_width + 10) + "\n\n"
        
        for i, (word, count) in enumerate(top_20, 1):
            bar = "█" * min(int(count / max_count * 20), 20)
            texto += f"{i:2}. {word:<{text_width}} {count:>4} {bar}\n"
        
        self.clean_freq_text.delete("1.0", tk.END)
        self.clean_freq_text.insert("1.0", texto)
        
        # Activar botón (indicar estado activo)
        self.preview_raw_btn.configure(fg_color="#4a4", hover_color="#383")
        self.apply_clean_btn.configure(fg_color="#48a", hover_color="#386")
        
        self.status_label.configure(text="Preview: texto en bruto (sin filtros)", text_color="green")
    
    def _apply_clean(self) -> None:
        """Aplica limpieza y muestra preview."""
        if not self.text_content:
            self.status_label.configure(text="Primero cargá texto", text_color="orange")
            return
        
        from tools.text_tool.processor import clean_text
        
        exclude_text = self.exclude_entry.get().strip()
        exclude_words = [w.strip().lower() for w in exclude_text.split(',')] if exclude_text else []
        
        cleaned = clean_text(
            self.text_content,
            remove_stopwords=self.remove_stopwords.get(),
            exclude_words=exclude_words
        )
        
        # Mostrar texto limpio
        self.clean_text.delete("1.0", tk.END)
        self.clean_text.insert("1.0", cleaned[:2000])  # Preview primeros 2000 chars
        
        from collections import Counter
        words = cleaned.lower().split()
        word_freq = Counter(words)
        top_20 = word_freq.most_common(20)
        
        # Calculate dynamic width for proper alignment
        max_word_len = max(len(word) for word, _ in top_20) if top_20 else 10
        text_width = max(12, max_word_len + 2)
        
        preview = "Top 20 palabras:\n" + "=" * (text_width + 8) + "\n"
        for i, (word, count) in enumerate(top_20, 1):
            preview += f"{i:2}. {word:<{text_width}} {count:>4}\n"
        
        self.clean_freq_text.delete("1.0", tk.END)
        self.clean_freq_text.insert("1.0", preview)
        
        self.cleaned_content = cleaned
        
        # Activar botón "Aplicar Limpieza" (indicar estado activo)
        self.preview_raw_btn.configure(fg_color="#888", hover_color="#666")
        self.apply_clean_btn.configure(fg_color="#4a4", hover_color="#383")
        
        self.status_label.configure(text=f"Limpieza aplicada: {len(cleaned.split())} palabras", text_color="green")
        
        # State update (Phase 1) - track last analysis
        self._update_state(last_analysis="limpieza")
        
        # Auto-update all analysis tabs when cleaning is applied
        self._update_frequency_display()
        self._update_ngrams_display()
    
    def _remove_source(self, source_type: str) -> None:
        """Quita un tipo de fuente y resetea todo el contenido."""
        if not self.text_content and not self.sources[source_type]:
            return
        
        self.text_content = ""
        self.cleaned_content = None
        self.clean_text.delete("1.0", tk.END)
        self.clean_freq_text.delete("1.0", tk.END)
        self.sources = {"text": [], "files": [], "urls": []}
        
        # State reset (Phase 1)
        self._update_state(text="", file_path=None, last_analysis=None, has_text=False)
        
        self._update_sources_summary()
        self._update_files_display()
        self.status_label.configure(text=f"Contenido reseteado", text_color="gray")
    
    def _update_sources_summary(self) -> None:
        """Actualiza el label de resumen de fuentes."""
        text_count = len(self.sources.get("text", []))
        file_count = len(self.sources.get("files", []))
        url_count = len(self.sources.get("urls", []))
        
        if not text_count and not file_count and not url_count:
            self.sources_summary.configure(text="📁 Sin contenido cargado")
            return
        
        total = text_count + file_count + url_count
        
        parts = []
        if text_count:
            parts.append(f"📝 Txt({text_count})")
        if file_count:
            parts.append(f"📁 Arch({file_count})")
        if url_count:
            parts.append(f"🌐 URLs({url_count})")
        
        summary = " + ".join(parts) + f" = {total} total"
        self.sources_summary.configure(text=summary)
    
    def _update_files_display(self) -> None:
        """Actualiza el label de archivos seleccionados."""
        if not hasattr(self, 'files_label'):
            return
            
        files = self.sources.get("files", [])
        
        if not files:
            self.files_label.configure(text="No hay archivos seleccionados", text_color="gray")
            return
        
        # Show file names (just the filenames, not full path)
        file_names = [f.split('/')[-1].split('\\')[-1] for f in files]
        
        if len(file_names) <= 5:
            text = "📄 " + " • ".join(file_names)
        else:
            text = f"📄 {len(file_names)} archivos:\n• " + "\n• ".join(file_names[:5])
            if len(file_names) > 5:
                text += f"\n... y {len(file_names) - 5} más"
        
        self.files_label.configure(text=text, text_color="white")
    
    def _check_text_size(self, show_warning: bool = True) -> bool:
        """
        Verifica el tamaño del texto y muestra warnings si es necesario.
        
        Returns:
            bool: True si el texto es aceptable, False si es muy grande
        """
        # State check (Phase 1) - use state lookup instead of direct hasattr
        if not self._get_state('has_text'):
            self.status_label.configure(text="Primero cargá texto", text_color="orange")
            return False
        
        try:
            from tools.text_tool.processor import check_text_size
            size_info = check_text_size(self.text_content)
            
            if size_info['is_too_large']:
                self.status_label.configure(
                    text=f"⚠️ Texto muy grande ({size_info['size_mb']}MB). Máximo 0.5MB.",
                    text_color="red"
                )
                return False
            
            if show_warning and size_info['needs_warning']:
                self.status_label.configure(
                    text=f"⚠️ Texto grande ({size_info['size_mb']}MB). Tiempo: {size_info['estimated_time']}",
                    text_color="yellow"
                )
                return True
            
            return True
        except Exception as e:
            logger.warning(f"Error checking text size: {e}")
            return True  # Allow processing if check fails
    
    # ============ TAB: ENTRADA ============
    def _setup_input_tab(self) -> None:
        frame = self.tab_input
        
        # Input tipo selector
        tipo_frame = ctk.CTkFrame(frame)
        tipo_frame.pack(fill="x", padx=10, pady=10)
        
        self.input_type = ctk.StringVar(value="text")
        
        ctk.CTkRadioButton(tipo_frame, text="📝 Texto", variable=self.input_type, value="text", command=self._on_input_type_change).pack(side="left", padx=5)
        ctk.CTkRadioButton(tipo_frame, text="📄 Archivos", variable=self.input_type, value="files", command=self._on_input_type_change).pack(side="left", padx=5)
        ctk.CTkRadioButton(tipo_frame, text="🌐 URLs", variable=self.input_type, value="url", command=self._on_input_type_change).pack(side="left", padx=5)
        
        # Área de texto (para input directo)
        self.text_input_area = ctk.CTkTextbox(frame, wrap="word")
        self.text_input_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para archivo (oculto por defecto)
        self.file_frame = ctk.CTkFrame(frame)
        self.file_frame.pack(fill="x", padx=10, pady=10)
        self.file_frame.pack_forget()
        
        ctk.CTkLabel(self.file_frame, text="📄 Archivos Seleccionados:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
        # Label to show selected files
        self.files_label = ctk.CTkLabel(
            self.file_frame,
            text="No hay archivos seleccionados",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left"
        )
        self.files_label.pack(fill="x", padx=5, pady=5)
        
        # Frame para URLs (dinámico)
        self.url_frame = ctk.CTkFrame(frame)
        self.url_frame.pack(fill="x", padx=10, pady=10)
        self.url_frame.pack_forget()
        
        # Título
        ctk.CTkLabel(self.url_frame, text="URLs:").pack(anchor="w")
        
        # Contenedor de URLs
        self.urls_container = ctk.CTkFrame(self.url_frame)
        self.urls_container.pack(fill="both", expand=True, pady=5)
        
        # Botones para agregar/quitar
        url_btns = ctk.CTkFrame(self.url_frame, fg_color="transparent")
        url_btns.pack(fill="x", pady=5)
        ctk.CTkButton(url_btns, text="➕ Agregar URL", command=self._add_url_field).pack(side="left", padx=5)
        self.url_count_label = ctk.CTkLabel(url_btns, text="1 URL", text_color="gray")
        self.url_count_label.pack(side="left", padx=10)
        
        # Primer campo URL
        self.url_entries = []
        self._add_url_field()
        
        # Botón cargar/procesar
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.load_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Cargar y Analizar",
            command=self._load_and_analyze,
            height=40
        )
        self.load_btn.pack(fill="x")
        
        # Initialize input view (después de crear botón)
        self._on_input_type_change()
        
        # Phase 3: Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="Cargá texto o archivo para analizar",
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        # Phase 2: Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            height=8
        )
        self.progress_bar.set(0)  # Start at 0
        self.progress_bar.pack(pady=(0, 5))
        self.progress_bar.pack_forget()  # Hide initially
        
        # Texto limpio para visualizaciones
        self.cleaned_content = None
    
    def _on_input_type_change(self) -> None:
        """Cambia visibilidad según tipo de input."""
        tipo = self.input_type.get()
        
        self.text_input_area.pack_forget()
        self.file_frame.pack_forget()
        self.url_frame.pack_forget()
        
        if tipo == "text":
            self.text_input_area.pack(fill="both", expand=True, padx=10, pady=10)
            self.load_btn.configure(text="📥 Agregar Texto")
        elif tipo == "files":
            self.file_frame.pack(fill="x", padx=10, pady=10)
            self.load_btn.configure(text="📄 Agregar Archivos")
        elif tipo == "url":
            self.url_frame.pack(fill="x", padx=10, pady=10)
            self.load_btn.configure(text="🌐 Agregar URLs")
    
    def _add_url_field(self) -> None:
        """Agrega un nuevo campo de URL."""
        row = ctk.CTkFrame(self.urls_container, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        entry = ctk.CTkEntry(row, placeholder_text="https://...")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn = ctk.CTkButton(row, text="❌", width=30, command=lambda: self._remove_url_field(row, entry))
        btn.pack(side="left")
        
        self.url_entries.append((row, entry))
        self.url_count_label.configure(text=f"{len(self.url_entries)} URLs")
    
    def _remove_url_field(self, row, entry) -> None:
        """Elimina un campo de URL."""
        if len(self.url_entries) > 1:
            row.pack_forget()
            self.url_entries = [(r, e) for r, e in self.url_entries if r != row]
            self.url_count_label.configure(text=f"{len(self.url_entries)} URLs")
        else:
            # Si es el único, limpiar el contenido
            entry.delete(0, tk.END)
    
    def _load_and_analyze(self) -> None:
        """Carga texto y ejecuta análisis."""
        tipo = self.input_type.get()
        
        try:
            from tools.text_tool.processor import (
                extract_text_from_file,
                extract_text_from_url,
                analyze_wordcloud,
                analyze_frequency,
                analyze_stats,
                analyze_ngrams
            )
            
            if tipo == "text":
                text = self.text_input_area.get("1.0", tk.END).strip()
                if not text:
                    self.status_label.configure(text="Ingresá texto", text_color="orange")
                    return
                if self.text_content:
                    self.text_content += '\n\n' + text
                else:
                    self.text_content = text
                self.sources["text"].append(text[:100])
                self.cleaned_content = None
                self._update_sources_summary()
                # State update (Phase 1)
                self._update_state(text=self.text_content, has_text=bool(self.text_content))
                self.status_label.configure(text=f"Texto cargado: {len(self.text_content)} caracteres", text_color="green")
            
            elif tipo == "files":
                files = filedialog.askopenfilenames(
                    title="Seleccionar archivos",
                    filetypes=[
                        ("Documentos", "*.pdf *.docx *.doc"),
                        ("Texto", "*.txt *.md"),
                        ("Todos", "*.*")
                    ]
                )
                if not files:
                    self.status_label.configure(text="Seleccioná archivos", text_color="orange")
                    return
                self.status_label.configure(text=f"Procesando {len(files)} archivos...", text_color="yellow")
                self.update()
                all_text = []
                for f in files:
                    result = extract_text_from_file(f)
                    if result.get('success'):
                        all_text.append(result['text'])
                
                new_text = '\n\n'.join(all_text)
                if self.text_content:
                    self.text_content += '\n\n' + new_text
                else:
                    self.text_content = new_text
                self.sources["files"].extend(files)
                self.cleaned_content = None
                self._update_sources_summary()
                self._update_files_display()
                # State update (Phase 1)
                self._update_state(text=self.text_content, file_path=files[0] if files else None, has_text=bool(self.text_content))
                self.status_label.configure(text=f"{len(files)} archivos: {len(self.text_content)} caracteres", text_color="green")
            
            elif tipo == "url":
                urls = [e.get().strip() for r, e in self.url_entries if e.get().strip()]
                if not urls:
                    self.status_label.configure(text="Agregá al menos una URL", text_color="#FFA500")
                    return
                
                logger.info(f"URL SCRAPER: Found {len(urls)} URLs to process: {urls}")
                self.status_label.configure(text=f"Procesando {len(urls)} URLs...", text_color="#FFD700")
                self.update_idletasks()
                
                all_text = []
                for idx, url in enumerate(urls, 1):
                    logger.info(f"URL SCRAPER: Processing {idx}/{len(urls)}: {url}")
                    self.status_label.configure(text=f"Procesando {idx}/{len(urls)}: {url[:30]}...", text_color="#FFD700")
                    self.update_idletasks()
                    
                    try:
                        result = extract_text_from_url(url)
                        if result.get('success'):
                            all_text.append(result['text'])
                            logger.info(f"URL SCRAPER: Success - {len(result['text'])} chars from {url}")
                        else:
                            logger.warning(f"URL SCRAPER: Failed - {result.get('error')} for {url}")
                    except Exception as e:
                        logger.error(f"URL SCRAPER: Error - {e} for {url}")
                    
                    self.status_label.configure(text=f"Listo {idx}/{len(urls)}", text_color="#FFD700")
                    self.update_idletasks()
                
                new_text = '\n\n'.join(all_text)
                logger.info(f"URL SCRAPER: Total collected {len(new_text)} chars")
                
                if self.text_content:
                    self.text_content += '\n\n' + new_text
                else:
                    self.text_content = new_text
                
                self.sources["urls"].extend(urls)
                self.cleaned_content = None
                self._update_sources_summary()
                # State update (Phase 1)
                self._update_state(text=self.text_content, has_text=bool(self.text_content))
                self.status_label.configure(
                    text=f"{len(urls)} URLs: {len(self.text_content)} caracteres - andá a Limpieza",
                    text_color="green"
                )
                
                logger.info(f"URL SCRAPER: Done - final text_content is {len(self.text_content)} chars")
            
            # No ejecutar análisis automáticamente - usuario debe ir a Limpieza
        
        except ImportError:
            self.status_label.configure(
                text="Installa dependencias: pip install wordcloud nltk pdfplumber requests beautifulsoup4",
                text_color="red"
            )
    
    def _run_all_analysis(self) -> None:
        """Ejecuta todos los análisis."""
        # Check text size first
        if not self._check_text_size(show_warning=True):
            return
        
        try:
            from tools.text_tool.processor import (
                analyze_wordcloud,
                analyze_frequency,
                analyze_stats,
                analyze_ngrams,
                analyze_trends,
                analyze_correlations,
                analyze_scatter,
                clean_text,
                check_text_size
            )
            
            # Show progress feedback
            self.status_label.configure(text="🔄 Procesando... (puede tomar unos segundos)", text_color="blue")
            self.update()
            
            # Obtener opciones de limpieza
            exclude_text = self.exclude_entry.get().strip()
            exclude_words = [w.strip().lower() for w in exclude_text.split(',')] if exclude_text else []
            
            # Limpiar texto con opciones
            cleaned = clean_text(
                self.text_content,
                remove_stopwords=self.remove_stopwords.get(),
                exclude_words=exclude_words
            )
            
            if not cleaned.strip():
                # Verificar si hay texto antes de limpiar
                if self.text_content.strip():
                    self.status_label.configure(text="Solo stopwords después de limpiar", text_color="orange")
                else:
                    self.status_label.configure(text="PDF sin texto o vacío", text_color="orange")
                return
            
            # Guardar texto limpio para visualizaciones
            self.cleaned_content = cleaned
            
            # WordCloud with customization params
            wc_n_words = int(self.wc_count_slider.get()) if hasattr(self, 'wc_count_slider') else 100
            wc_colormap = self.wc_colormap.get() if hasattr(self, 'wc_colormap') else 'viridis'
            wc_margin = int(self.wc_margin_slider.get()) if hasattr(self, 'wc_margin_slider') else 10
            wc_shape = self.wc_shape.get() if hasattr(self, 'wc_shape') else 'rectangle'
            
            wc_result = analyze_wordcloud(
                cleaned,
                n_words=wc_n_words,
                colormap=wc_colormap,
                margin=wc_margin,
                shape=wc_shape
            )
            if wc_result.get('success') and wc_result.get('image_data'):
                self._show_wordcloud(wc_result['image_data'])
            
            # Frecuencia - get slider value
            freq_n = int(self.freq_slider.get()) if hasattr(self, 'freq_slider') else 20
            freq_result = analyze_frequency(cleaned, n=freq_n, already_cleaned=True)
            if freq_result.get('success'):
                self._show_frequency(freq_result['frequencies'], n=freq_n)
            
            # Stats
            stats_result = analyze_stats(cleaned)
            if stats_result.get('success'):
                self._show_stats(stats_result)
            
            # N-grams - get slider value
            ngram_top_k = int(self.ngram_slider.get()) if hasattr(self, 'ngram_slider') else 20
            ngram_n = self.ngram_size.get()
            ngram_result = analyze_ngrams(cleaned, n=ngram_n, top_k=ngram_top_k)
            if ngram_result.get('success'):
                self._show_ngrams(ngram_result['ngrams'], top_k=ngram_top_k)
            
            # Trends
            trends_result = analyze_trends(cleaned)
            if trends_result.get('success') and trends_result.get('image_data'):
                self._show_trends(trends_result['image_data'])
            
            # Correlations
            corr_result = analyze_correlations(cleaned)
            if corr_result.get('success') and corr_result.get('image_data'):
                self._show_correlations(corr_result['image_data'])
            
            # Scatter
            scatter_result = analyze_scatter(cleaned)
            if scatter_result.get('success') and scatter_result.get('image_data'):
                self._show_scatter(scatter_result['image_data'])
            
            # State update (Phase 1) - track completed analysis
            self._update_state(last_analysis="full_analysis")
            
            self.status_label.configure(text="Análisis completo!", text_color="green")
            
        except Exception as e:
            import traceback
            logger.error(f"Error analysis: {e}")
            traceback.print_exc()
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    # ============ TAB: WORDCLOUD ============
    def _setup_wc_tab(self) -> None:
        frame = self.tab_wc
        
        # === Personalization Controls Frame ===
        customize_frame = ctk.CTkFrame(frame)
        customize_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(customize_frame, text="Personalización:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=(5, 10))
        
        # Row 1: Word count slider
        wc_count_row = ctk.CTkFrame(customize_frame)
        wc_count_row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(wc_count_row, text="Palabras:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wc_count_slider = ctk.CTkSlider(
            wc_count_row,
            from_=50,
            to=200,
            number_of_steps=150,
            command=self._on_wc_count_change
        )
        self.wc_count_slider.set(100)
        self.wc_count_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.wc_count_label = ctk.CTkLabel(wc_count_row, text="100", width=40)
        self.wc_count_label.pack(side="left", padx=5)
        
        # Row 2: Colormap dropdown
        wc_colormap_row = ctk.CTkFrame(customize_frame)
        wc_colormap_row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(wc_colormap_row, text="Colormap:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wc_colormap = ctk.CTkComboBox(
            wc_colormap_row,
            values=['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                   'blues', 'greens', 'reds', 'oranges', 'purples',
                   'coolwarm', 'RdYlGn', 'seismic', 'terrain', 'ocean'],
            state="readonly"
        )
        self.wc_colormap.set('viridis')
        self.wc_colormap.pack(side="left", fill="x", expand=True, padx=5)
        
        # Row 3: Margin slider
        wc_margin_row = ctk.CTkFrame(customize_frame)
        wc_margin_row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(wc_margin_row, text="Márgenes:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wc_margin_slider = ctk.CTkSlider(
            wc_margin_row,
            from_=0,
            to=50,
            number_of_steps=50,
            command=self._on_wc_margin_change
        )
        self.wc_margin_slider.set(10)
        self.wc_margin_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.wc_margin_label = ctk.CTkLabel(wc_margin_row, text="10px", width=40)
        self.wc_margin_label.pack(side="left", padx=5)
        
        # Row 4: Shape selector
        wc_shape_row = ctk.CTkFrame(customize_frame)
        wc_shape_row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(wc_shape_row, text="Forma:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wc_shape = ctk.CTkComboBox(
            wc_shape_row,
            values=['rectangle', 'circle', 'heart', 'star'],
            state="readonly"
        )
        self.wc_shape.set('rectangle')
        self.wc_shape.pack(side="left", fill="x", expand=True, padx=5)
        
        # Row 5: Exclude words entry
        wc_exclude_row = ctk.CTkFrame(customize_frame)
        wc_exclude_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(wc_exclude_row, text="Excluir:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wc_exclude_entry = ctk.CTkEntry(wc_exclude_row, placeholder_text="palabra1, palabra2, ...")
        self.wc_exclude_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            customize_frame,
            text="Generar WordCloud",
            command=self._regenerate_wc,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_btn.pack(pady=10)
        
        # WordCloud display area
        self.wc_label = ctk.CTkLabel(
            frame,
            text="WordCloud aparecerá aquí",
            text_color="gray"
        )
        self.wc_label.pack(expand=True)
    
    def _on_wc_count_change(self, value: float) -> None:
        """Handle word count slider change."""
        n = int(value)
        self.wc_count_label.configure(text=str(n))
    
    def _on_wc_margin_change(self, value: float) -> None:
        """Handle margin slider change."""
        m = int(value)
        self.wc_margin_label.configure(text=f"{m}px")
    
    def _show_wordcloud(self, image_data) -> None:
        """Muestra WordCloud."""
        try:
            from PIL import Image
            from io import BytesIO
            
            # Debug: log image_data type and size
            logger.info(f"WordCloud: image_data type={type(image_data)}, len={len(image_data) if isinstance(image_data, (bytes, bytearray)) else 'N/A'}")
            
            # Validate input
            if not isinstance(image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(image_data)}")
            
            # Abrir imagen desde bytes
            img = Image.open(BytesIO(image_data))
            
            # Resize para display (más pequeño) - reducido 5%
            img.thumbnail((570, 285))
            
            # Convertir a formato que CTkImage pueda usar
            # Asegurar modo correcto
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Crear CTkImage
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            # Actualizar label
            self.wc_label.configure(image=ctk_img, text="")
            self.wc_label.image = ctk_img
            
            # Add click binding to open modal (unbind first to prevent duplicates)
            self.wc_label.unbind("<Button-1>")
            self.wc_label.bind("<Button-1>", lambda e: self._open_chart_modal(image_data, "WordCloud"))
            
            # Add tooltip
            self.wc_label.configure(cursor="hand2")
            
        except Exception as e:
            import traceback
            logger.error(f"WordCloud error: {e}")
            logger.debug(traceback.format_exc())
            self.wc_label.configure(text=f"Error: {e}")
    
    def _regenerate_wc(self) -> None:
        """Regenera WordCloud con opciones de personalización."""
        # Check text size first
        if not self._check_text_size(show_warning=True):
            return
        
        # Get text content - check if cleaned content exists
        if not self.cleaned_content:
            self.status_label.configure(text="Cargue y analice el texto primero", text_color="orange")
            return
        
        # Get customization values
        n_words = int(self.wc_count_slider.get()) if hasattr(self, 'wc_count_slider') else 100
        colormap = self.wc_colormap.get() if hasattr(self, 'wc_colormap') else 'viridis'
        margin = int(self.wc_margin_slider.get()) if hasattr(self, 'wc_margin_slider') else 10
        shape = self.wc_shape.get() if hasattr(self, 'wc_shape') else 'rectangle'
        
        # Get exclude words
        exclude_text = self.wc_exclude_entry.get().strip()
        exclude_words = [w.strip().lower() for w in exclude_text.split(',')] if exclude_text else []
        
        from tools.text_tool.processor import analyze_wordcloud, clean_text
        
        # Clean with exclude words (using original text to apply new exclusions)
        cleaned = clean_text(self.text_content, remove_stopwords=True, exclude_words=exclude_words)
        
        # Check for empty text after cleaning
        if not cleaned or not cleaned.strip():
            word_count = len(self.text_content.split()) if self.text_content else 0
            if word_count < 5:
                self.status_label.configure(text="Texto muy corto para WordCloud", text_color="orange")
            else:
                self.status_label.configure(text="Solo stopwords después de excluir", text_color="orange")
            return
        
        # Get actual word count for display
        actual_words = len(cleaned.split())
        
        # Warn if requested words > available
        if n_words > actual_words:
            self.status_label.configure(
                text=f"Solo {actual_words} palabras disponibles (solicitadas: {n_words})",
                text_color="orange"
            )
        
        # Generate WordCloud with all customization params
        try:
            logger.info(f"WordCloud params: n_words={n_words}, colormap={colormap}, margin={margin}, shape={shape}")
            result = analyze_wordcloud(
                cleaned,
                n_words=n_words,
                colormap=colormap,
                margin=margin,
                shape=shape
            )
            
            if result.get('success') and result.get('image_data'):
                self._show_wordcloud(result['image_data'])
                self.status_label.configure(
                    text=f"WordCloud: {actual_words} palabras, {colormap}, {shape}",
                    text_color="green"
                )
            elif 'memoria' in result.get('error', '').lower() or 'memory' in result.get('error', '').lower():
                # Handle memory error - reduce word count and try again
                self.status_label.configure(
                    text="Memoria insuficiente. Reduzca el número de palabras.",
                    text_color="red"
                )
            else:
                self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
        except Exception as e:
            logger.error(f"WordCloud generation error: {e}")
            self.status_label.configure(text=f"Error: {str(e)[:50]}", text_color="red")
    
    # ============ TAB: FRECUENCIA ============
    def _setup_freq_tab(self) -> None:
        frame = self.tab_freq
        
        # Frame contenedor que ocupa todo el espacio del tab
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Slider frame - en la parte superior
        slider_frame = ctk.CTkFrame(container, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(slider_frame, text="Palabras a mostrar:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        
        # Slider for word count (range 20-100, default 20)
        self.freq_slider = ctk.CTkSlider(
            slider_frame,
            from_=20,
            to=100,
            number_of_steps=80,
            command=self._on_freq_slider_change
        )
        self.freq_slider.set(20)
        self.freq_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        # Label showing current value
        self.freq_label = ctk.CTkLabel(slider_frame, text="20 palabras", font=ctk.CTkFont(size=12))
        self.freq_label.pack(side="left", padx=10)
        
        # Text view - ocupa el resto del espacio, con altura mínima
        self.freq_text = ctk.CTkTextbox(
            container, 
            font=("Courier New", 14), 
            wrap="word",
            height=441  # Aumentado 5%
        )
        self.freq_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def _on_freq_slider_change(self, value: float) -> None:
        """Handle frequency slider change - update display after release."""
        n = int(value)
        self.freq_label.configure(text=f"{n} palabras")
        
        # Regenerate frequency display when slider changes
        self._update_frequency_display(n)
    
    def _update_frequency_display(self, n: int = None) -> None:
        """Update frequency display with specified n value."""
        if n is None:
            n = int(self.freq_slider.get())
        
        if not self.cleaned_content:
            return
        
        try:
            from tools.text_tool.processor import analyze_frequency
            
            result = analyze_frequency(self.cleaned_content, n=n, already_cleaned=True)
            if result.get('success'):
                self._show_frequency(result['frequencies'])
        except Exception as e:
            logger.error(f"Error updating frequency: {e}")
    
    def _show_frequency(self, frequencies: Dict[str, int], n: int = None) -> None:
        """Muestra frecuencia de palabras."""
        self.freq_text.delete("1.0", tk.END)
        
        actual_count = len(frequencies)
        slider_n = n if n is not None else int(self.freq_slider.get())
        
        # Update label to show actual count
        if actual_count < slider_n:
            self.freq_label.configure(text=f"{actual_count} palabras (máx disponible)")
        else:
            self.freq_label.configure(text=f"{slider_n} palabras")
        
        # Calculate max word length for proper alignment
        max_word_len = max(len(word) for word in frequencies) if frequencies else 10
        text_width = max(20, max_word_len + 2)
        
        # Header with aligned columns
        texto = "📈 Palabras más frecuentes\n"
        texto += "=" * (text_width + 10) + "\n"
        texto += f"{'#':>3} {'Palabra':<{text_width}} {'Count':>5}\n"
        texto += "-" * (text_width + 10) + "\n"
        
        for i, (word, count) in enumerate(frequencies.items(), 1):
            texto += f"{i:>3}. {word:<{text_width}} {count:>5}\n"
        
        self.freq_text.insert("1.0", texto)
    
    # ============ TAB: ESTADÍSTICAS ============
    def _setup_stats_tab(self) -> None:
        frame = self.tab_stats
        
        # Frame contenedor que ocupa todo el espacio del tab
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Configurar container para grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Stats text - usar grid para que se expanda
        self.stats_text = ctk.CTkTextbox(container, font=("Courier New", 15), height=270)
        self.stats_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _show_stats(self, stats: Dict[str, Any]) -> None:
        """Muestra estadísticas."""
        self.stats_text.delete("1.0", tk.END)
        
        # Define fixed width for labels to align values
        label_width = 25
        
        texto = "📉 Estadísticas del Texto\n"
        texto += "=" * (label_width + 12) + "\n"
        texto += f"{'Métrica':<{label_width}} {'Valor':>10}\n"
        texto += "-" * (label_width + 12) + "\n"
        
        texto += f"{'Caracteres totales':<{label_width}} {stats.get('total_chars', 0):>10,}\n"
        texto += f"{'Palabras totales':<{label_width}} {stats.get('total_words', 0):>10,}\n"
        texto += f"{'Palabras únicas':<{label_width}} {stats.get('unique_words', 0):>10,}\n"
        texto += f"{'Oraciones':<{label_width}} {stats.get('total_sentences', 0):>10,}\n"
        texto += "\n"
        texto += f"{'Promedio palabra':<{label_width}} {stats.get('avg_word_length', 0):>10.2f}\n"
        texto += f"{'Promedio oración':<{label_width}} {stats.get('avg_sentence_length', 0):>10.2f}\n"
        texto += f"{'Type-Token Ratio':<{label_width}} {stats.get('type_token_ratio', 0):>10.4f}\n"
        
        self.stats_text.insert("1.0", texto)
    
    # ============ TAB: N-GRAMS ============
    def _setup_ngram_tab(self) -> None:
        frame = self.tab_ngram
        
        # Frame contenedor que ocupa todo el espacio del tab
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Configurar container para grid
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        opts = ctk.CTkFrame(container)
        opts.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(opts, text="N-gram size:").pack(side="left", padx=10)
        
        self.ngram_size = ctk.IntVar(value=2)
        
        # Add trace to update display when n-gram size changes
        self.ngram_size.trace_add("write", self._on_ngram_size_change)
        
        for n in [2, 3]:
            ctk.CTkRadioButton(
                opts, 
                text=f"{n}-grams", 
                variable=self.ngram_size, 
                value=n
            ).pack(side="left", padx=10)
        
        # Slider frame for top_k - usar grid para mejor control
        slider_frame = ctk.CTkFrame(container, fg_color="transparent")
        slider_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(slider_frame, text="Top resultados:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        
        # Slider for top_k (range 20-100, default 20)
        self.ngram_slider = ctk.CTkSlider(
            slider_frame,
            from_=20,
            to=100,
            number_of_steps=80,
            command=self._on_ngram_slider_change
        )
        self.ngram_slider.set(20)
        self.ngram_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        # Label showing current value
        self.ngram_label = ctk.CTkLabel(slider_frame, text="20 resultados", font=ctk.CTkFont(size=12))
        self.ngram_label.pack(side="left", padx=10)
        
        # Text view - usar grid para que se expanda
        self.ngram_text = ctk.CTkTextbox(container, font=("Courier New", 14), height=345)
        self.ngram_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
    
    def _on_ngram_slider_change(self, value: float) -> None:
        """Handle n-gram slider change - update label and display."""
        top_k = int(value)
        self.ngram_label.configure(text=f"{top_k} resultados")
        
        # Regenerate n-grams display when slider changes
        self._update_ngrams_display(top_k)
    
    def _on_ngram_size_change(self, *args) -> None:
        """Handle n-gram size (2 vs 3) change - regenerate display."""
        self._update_ngrams_display()
    
    def _update_ngrams_display(self, top_k: int = None) -> None:
        """Update n-grams display with specified top_k value."""
        if top_k is None:
            top_k = int(self.ngram_slider.get())
        
        if not self.cleaned_content:
            return
        
        try:
            from tools.text_tool.processor import analyze_ngrams
            
            n = self.ngram_size.get()
            result = analyze_ngrams(self.cleaned_content, n=n, top_k=top_k)
            if result.get('success'):
                self._show_ngrams(result['ngrams'], top_k=top_k)
            else:
                self.status_label.configure(text=result.get('error', 'Error'), text_color="orange")
        except Exception as e:
            logger.error(f"Error updating ngrams: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    def _show_ngrams(self, ngrams: Dict[str, int], top_k: int = None) -> None:
        """Muestra n-grams."""
        self.ngram_text.delete("1.0", tk.END)
        
        actual_count = len(ngrams)
        slider_top_k = top_k if top_k is not None else int(self.ngram_slider.get())
        
        # Update label to show actual count
        if actual_count < slider_top_k:
            self.ngram_label.configure(text=f"{actual_count} resultados (máx disponible)")
        else:
            self.ngram_label.configure(text=f"{slider_top_k} resultados")
        
        n = self.ngram_size.get()
        
        # Calculate max n-gram length for proper alignment
        max_ng_len = max(len(ng) for ng in ngrams) if ngrams else 10
        # Use larger width for 3-grams (more words = longer text)
        # Minimum width of 25, plus extra space based on n-gram size
        text_width = max(25, max_ng_len + 2)
        
        # Header
        texto = f"🔗 N-grams ({n})\n"
        texto += "=" * (text_width + 8) + "\n"
        # Header line with aligned numbers
        texto += f"{'#':>3} {'N-gram':<{text_width}} {'Count':>4}\n"
        texto += "-" * (text_width + 8) + "\n"
        
        for i, (ng, count) in enumerate(ngrams.items(), 1):
            texto += f"{i:>3}. {ng:<{text_width}} {count:>4}\n"
        
        self.ngram_text.insert("1.0", texto)
    
    # ============ TAB: TRENDS ============
    def _setup_trends_tab(self) -> None:
        frame = self.tab_trends
        
        self.trends_label = ctk.CTkLabel(
            frame,
            text="Tendencias aparecerá aquí",
            text_color="gray"
        )
        self.trends_label.pack(expand=True)
    
    def _show_trends(self, image_data) -> None:
        """Muestra gráfico de tendencias."""
        try:
            from PIL import Image
            from io import BytesIO
            
            # Debug
            logger.info(f"Trends: image_data type={type(image_data)}, len={len(image_data) if isinstance(image_data, (bytes, bytearray)) else 'N/A'}")
            
            if not isinstance(image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(image_data)}")
            
            img = Image.open(BytesIO(image_data))
            img.thumbnail((700, 350))
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            self.trends_label.configure(image=ctk_img, text="")
            self.trends_label.image = ctk_img
            
            # Add click binding to open modal (unbind first to prevent duplicates)
            self.trends_label.unbind("<Button-1>")
            self.trends_label.bind("<Button-1>", lambda e: self._open_chart_modal(image_data, "Tendencias"))
            
            # Add tooltip
            self.trends_label.configure(cursor="hand2")
            
        except Exception as e:
            self.trends_label.configure(text=f"Error: {e}")
    
    # ============ TAB: CORRELATIONS ============
    def _setup_corr_tab(self) -> None:
        frame = self.tab_corr
        
        self.corr_label = ctk.CTkLabel(
            frame,
            text="Correlaciones aparezca aquí",
            text_color="gray"
        )
        self.corr_label.pack(expand=True)
    
    def _show_correlations(self, image_data) -> None:
        """Muestra heatmap de correlaciones."""
        try:
            from PIL import Image
            from io import BytesIO
            
            # Debug
            logger.info(f"Correlations: image_data type={type(image_data)}, len={len(image_data) if isinstance(image_data, (bytes, bytearray)) else 'N/A'}")
            
            if not isinstance(image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(image_data)}")
            
            img = Image.open(BytesIO(image_data))
            img.thumbnail((700, 500))
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            self.corr_label.configure(image=ctk_img, text="")
            self.corr_label.image = ctk_img
            
            # Add click binding to open modal (unbind first to prevent duplicates)
            self.corr_label.unbind("<Button-1>")
            self.corr_label.bind("<Button-1>", lambda e: self._open_chart_modal(image_data, "Correlaciones"))
            
            # Add tooltip
            self.corr_label.configure(cursor="hand2")
            
        except Exception as e:
            self.corr_label.configure(text=f"Error: {e}")
    
    # ============ TAB: SCATTER ============
    def _setup_scatter_tab(self) -> None:
        frame = self.tab_scatter
        
        self.scatter_label = ctk.CTkLabel(
            frame,
            text="Scatter plot aparecerá aquí",
            text_color="gray"
        )
        self.scatter_label.pack(expand=True)
    
    def _show_scatter(self, image_data) -> None:
        """Muestra scatter plot."""
        try:
            from PIL import Image
            from io import BytesIO
            
            # Debug
            logger.info(f"Scatter: image_data type={type(image_data)}, len={len(image_data) if isinstance(image_data, (bytes, bytearray)) else 'N/A'}")
            
            if not isinstance(image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(image_data)}")
            
            img = Image.open(BytesIO(image_data))
            img.thumbnail((700, 400))
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            self.scatter_label.configure(image=ctk_img, text="")
            self.scatter_label.image = ctk_img
            
            # Add click binding to open modal (unbind first to prevent duplicates)
            self.scatter_label.unbind("<Button-1>")
            self.scatter_label.bind("<Button-1>", lambda e: self._open_chart_modal(image_data, "Scatter Plot"))
            
            # Add tooltip
            self.scatter_label.configure(cursor="hand2")
            
        except Exception as e:
            self.scatter_label.configure(text=f"Error: {e}")
    
    # ============ TAB: KWIC (CONTEXTOS) ============
    def _setup_kwic_tab(self) -> None:
        frame = self.tab_kwic
        
        # Frame contenedor que ocupa todo el espacio del tab
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Configurar container para grid
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # === Search Controls Frame - usar grid ===
        search_frame = ctk.CTkFrame(container, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar palabra clave en contexto:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 10))
        
        # Keyword input
        keyword_row = ctk.CTkFrame(search_frame)
        keyword_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(keyword_row, text="Palabra:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.kwic_keyword = ctk.CTkEntry(keyword_row, placeholder_text="palabra a buscar...")
        self.kwic_keyword.pack(side="left", fill="x", expand=True, padx=5)
        
        # Bind Enter key to search
        self.kwic_keyword.bind("<Return>", lambda e: self._run_kwic_search())
        
        # Context window slider
        context_row = ctk.CTkFrame(search_frame)
        context_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(context_row, text="Contexto (±palabras):", width=120, anchor="w").pack(side="left", padx=5)
        
        self.kwic_context_slider = ctk.CTkSlider(
            context_row,
            from_=1,
            to=15,
            number_of_steps=14,
            command=self._on_kwic_context_change
        )
        self.kwic_context_slider.set(5)
        self.kwic_context_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.kwic_context_label = ctk.CTkLabel(context_row, text="5", width=30)
        self.kwic_context_label.pack(side="left", padx=5)
        
        # Max results slider
        results_row = ctk.CTkFrame(search_frame)
        results_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(results_row, text="Máx resultados:", width=120, anchor="w").pack(side="left", padx=5)
        
        self.kwic_results_slider = ctk.CTkSlider(
            results_row,
            from_=5,
            to=50,
            number_of_steps=45,
            command=self._on_kwic_results_change
        )
        self.kwic_results_slider.set(20)
        self.kwic_results_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.kwic_results_label = ctk.CTkLabel(results_row, text="20", width=30)
        self.kwic_results_label.pack(side="left", padx=5)
        
        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self._run_kwic_search,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_btn.pack(pady=10)
        
        # Labels
        ctk.CTkLabel(
            container,
            text="Resultados:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Results display - usar grid para que se expanda
        self.kwic_results_text = ctk.CTkTextbox(
            container,
            font=("Courier New", 12),
            height=180  # Reducido 5%
        )
        self.kwic_results_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
    
    def _on_kwic_context_change(self, value: float) -> None:
        """Handle context slider change."""
        n = int(value)
        self.kwic_context_label.configure(text=str(n))
    
    def _on_kwic_results_change(self, value: float) -> None:
        """Handle results slider change."""
        n = int(value)
        self.kwic_results_label.configure(text=str(n))
    
    def _run_kwic_search(self) -> None:
        """Run KWIC search."""
        # Check text size first
        if not self._check_text_size(show_warning=True):
            return
        
        if not self.text_content:
            self.status_label.configure(text="No hay texto cargado", text_color="orange")
            return
        
        keyword = self.kwic_keyword.get().strip()
        if not keyword:
            self.status_label.configure(text="Ingrese una palabra clave", text_color="orange")
            return
        
        context = int(self.kwic_context_slider.get())
        max_results = int(self.kwic_results_slider.get())
        
        try:
            from tools.text_tool.processor import analyze_kwic
            
            result = analyze_kwic(self.text_content, keyword, context=context, max_results=max_results)
            
            if result.get('success'):
                self._show_kwic_results(result.get('data', []), keyword)
                if not result.get('data'):
                    self.status_label.configure(
                        text=result.get('error', 'No se encontraron ocurrencias'),
                        text_color="orange"
                    )
                else:
                    self.status_label.configure(
                        text=f"{len(result.get('data', []))} ocurrencias encontradas",
                        text_color="green"
                    )
            else:
                self.status_label.configure(
                    text=result.get('error', 'Error'),
                    text_color="red"
                )
        except Exception as e:
            logger.error(f"KWIC error: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    def _show_kwic_results(self, concordances: list, keyword: str) -> None:
        """Display KWIC concordance results."""
        self.kwic_results_text.delete("1.0", tk.END)
        
        if not concordances:
            self.kwic_results_text.insert("1.0", "No se encontraron ocurrencias")
            return
        
        # Header
        texto = f"🔍 Contextos para '{keyword}'\n"
        texto += "=" * 70 + "\n\n"
        
        # Calculate max widths
        max_before = max(len(c.get('before', '')) for c in concordances) if concordances else 20
        max_after = max(len(c.get('after', '')) for c in concordances) if concordances else 20
        
        before_width = min(max_before, 40)  # Limit display width
        after_width = min(max_after, 40)
        
        # Each concordance entry
        for i, conc in enumerate(concordances, 1):
            before = conc.get('before', '')[:before_width]
            keyword_disp = conc.get('keyword', '')
            after = conc.get('after', '')[:after_width]
            
            # Format: before | keyword | after
            texto += f"{i:>3}. {before:<{before_width}} | {keyword_disp} | {after}\n"
        
        self.kwic_results_text.insert("1.0", texto)
    
    # ============ TAB: TOPICS (LDA) ============
    def _setup_topics_tab(self) -> None:
        frame = self.tab_topics
        
        # Frame contenedor que ocupa todo el espacio del tab
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Configurar container para grid
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # === Controls Frame - usar grid ===
        controls_frame = ctk.CTkFrame(container, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            controls_frame,
            text="Extracción de tópicos usando LDA (Latent Dirichlet Allocation):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 10))
        
        # Topic count slider
        topic_count_row = ctk.CTkFrame(controls_frame)
        topic_count_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(topic_count_row, text="Número de temas:", width=120, anchor="w").pack(side="left", padx=5)
        
        self.topics_count_slider = ctk.CTkSlider(
            topic_count_row,
            from_=3,
            to=10,
            number_of_steps=7,
            command=self._on_topics_count_change
        )
        self.topics_count_slider.set(5)
        self.topics_count_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.topics_count_label = ctk.CTkLabel(topic_count_row, text="5", width=30)
        self.topics_count_label.pack(side="left", padx=5)
        
        # Run button
        analyze_btn = ctk.CTkButton(
            controls_frame,
            text="📚 Analizar Temas",
            command=self._run_topics_analysis,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        analyze_btn.pack(pady=10)
        
        # Labels
        ctk.CTkLabel(
            container,
            text="Resultados:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Results display - usar grid para que se expanda
        self.topics_results_text = ctk.CTkTextbox(
            container,
            font=("Courier New", 12),
            height=230
        )
        self.topics_results_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
    
    def _on_topics_count_change(self, value: float) -> None:
        """Handle topic count slider change."""
        n = int(value)
        self.topics_count_label.configure(text=str(n))
    
    def _run_topics_analysis(self) -> None:
        """Run LDA topics analysis."""
        # Check text size first
        if not self._check_text_size(show_warning=True):
            return
        
        if not self.text_content:
            self.status_label.configure(text="No hay texto cargado", text_color="orange")
            return
        
        n_topics = int(self.topics_count_slider.get())
        
        try:
            from tools.text_tool.processor import analyze_topics, clean_text
            
            # Show "Analizando" status
            self.status_label.configure(text="🔄 Analizando temas con LDA...", text_color="blue")
            self.update()
            
            # Get cleaning options from Clean tab
            exclude_text = self.exclude_entry.get().strip()
            exclude_words = [w.strip().lower() for w in exclude_text.split(',')] if exclude_text else []
            remove_stopwords = self.remove_stopwords.get()
            
            # Apply cleaning to text
            cleaned = clean_text(
                self.text_content,
                remove_stopwords=remove_stopwords,
                exclude_words=exclude_words if exclude_words else None
            )
            
            result = analyze_topics(
                cleaned,
                n_topics=n_topics,
                already_cleaned=True
            )
            
            if result.get('success'):
                self._show_topics_results(result.get('data', []))
                if result.get('data'):
                    self.status_label.configure(
                        text=f"Análisis de temas completado: {len(result.get('data', []))} tópicos",
                        text_color="green"
                    )
                else:
                    self.status_label.configure(
                        text=result.get('error', 'No se encontraron suficientes tópicos'),
                        text_color="orange"
                    )
            else:
                self.status_label.configure(
                    text=result.get('error', 'Error'),
                    text_color="red"
                )
        except Exception as e:
            logger.error(f"Topics error: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    def _show_topics_results(self, topics: list) -> None:
        """Display LDA topics results."""
        self.topics_results_text.delete("1.0", tk.END)
        
        if not topics:
            self.topics_results_text.insert("1.0", "No se pudieron extraer temas del texto.")
            return
        
        # Header
        texto = "📚 Temas extraídos con LDA\n"
        texto += "=" * 60 + "\n\n"
        
        # Each topic
        for topic in topics:
            topic_id = topic.get('topic_id', 0)
            words = topic.get('words', [])
            
            texto += f"--- Tema {topic_id + 1} ---\n"
            
            if not words:
                texto += "  (Sin palabras)\n"
            else:
                # Find max weight for normalization display
                max_weight = max(w.get('weight', 0) for w in words) if words else 1
                
                # Calculate dynamic width for proper alignment
                max_word_len = max(len(word_data.get('word', '')) for word_data in words) if words else 10
                text_width = max(15, max_word_len + 2)
                
                for word_data in words:
                    word = word_data.get('word', '')
                    weight = word_data.get('weight', 0)
                    
                    # Normalize weight for display (0-20 bars)
                    normalized = int((weight / max_weight) * 20) if max_weight > 0 else 0
                    bar = "▓" * normalized + "░" * (20 - normalized)
                    
                    texto += f"  {word:<{text_width}} {bar} {weight:.3f}\n"
            
            texto += "\n"
        
        self.topics_results_text.insert("1.0", texto)
    
    # ============ TAB: WORDTREE (ÁRBOL DE PALABRAS) ============
    def _setup_wordtree_tab(self) -> None:
        frame = self.tab_wordtree
        
        # === Controls Frame ===
        controls_frame = ctk.CTkFrame(frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            controls_frame,
            text="Visualización de relaciones de palabras en estructura de árbol:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 10))
        
        # Phrase input
        phrase_row = ctk.CTkFrame(controls_frame)
        phrase_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(phrase_row, text="Frase raíz:", width=80, anchor="w").pack(side="left", padx=5)
        
        self.wordtree_phrase = ctk.CTkEntry(phrase_row, placeholder_text="palabra o frase a buscar...")
        self.wordtree_phrase.pack(side="left", fill="x", expand=True, padx=5)
        
        # Bind Enter key to run
        self.wordtree_phrase.bind("<Return>", lambda e: self._run_wordtree_analysis())
        
        # Max depth slider
        depth_row = ctk.CTkFrame(controls_frame)
        depth_row.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(depth_row, text="Profundidad máx:", width=120, anchor="w").pack(side="left", padx=5)
        
        self.wordtree_depth_slider = ctk.CTkSlider(
            depth_row,
            from_=2,
            to=5,
            number_of_steps=3,
            command=self._on_wordtree_depth_change
        )
        self.wordtree_depth_slider.set(3)
        self.wordtree_depth_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.wordtree_depth_label = ctk.CTkLabel(depth_row, text="3", width=30)
        self.wordtree_depth_label.pack(side="left", padx=5)
        
        # Run button
        generate_btn = ctk.CTkButton(
            controls_frame,
            text="🌳 Generar Árbol",
            command=self._run_wordtree_analysis,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_btn.pack(pady=10)
        
        # Image display area
        self.wordtree_label = ctk.CTkLabel(
            frame,
            text="Árbol de palabras aparecerá aquí",
            text_color="gray"
        )
        self.wordtree_label.pack(expand=True)
    
    def _on_wordtree_depth_change(self, value: float) -> None:
        """Handle depth slider change - auto-regenerate if phrase exists."""
        n = int(value)
        self.wordtree_depth_label.configure(text=str(n))
        
        # Auto-regenerate if phrase is already entered
        phrase = self.wordtree_phrase.get().strip()
        if phrase and self.text_content:
            self._run_wordtree_analysis()
    
    def _run_wordtree_analysis(self) -> None:
        """Run WordTree analysis."""
        # Check text size first
        if not self._check_text_size(show_warning=True):
            return
        
        if not self.text_content:
            self.status_label.configure(text="No hay texto cargado", text_color="orange")
            return
        
        phrase = self.wordtree_phrase.get().strip()
        if not phrase:
            self.status_label.configure(text="Ingrese una frase raíz", text_color="orange")
            return
        
        max_depth = int(self.wordtree_depth_slider.get())
        
        try:
            from tools.text_tool.processor import analyze_wordtree
            
            result = analyze_wordtree(self.text_content, phrase, max_depth=max_depth)
            
            if result.get('success') and (result.get('image_data') or result.get('tree')):
                self._show_wordtree(result)  # Pass full result
                self.status_label.configure(
                    text=f"Árbol generado para: '{phrase}'",
                    text_color="green"
                )
            elif result.get('success'):
                self.status_label.configure(
                    text=result.get('error', 'No se encontraron relaciones repetidas'),
                    text_color="orange"
                )
            else:
                self.status_label.configure(
                    text=result.get('error', 'Error'),
                    text_color="red"
                )
        except Exception as e:
            logger.error(f"WordTree error: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    def _show_wordtree(self, result) -> None:
        """Display interactive WordTree visualization."""
        try:
            # Handle both old format (image_data only) and new format (dict with image_data and tree)
            if isinstance(result, dict):
                image_data = result.get('image_data')
                tree_data = result.get('tree')
            else:
                image_data = result
                tree_data = None
            
            # Save tree data for collapse/expand functionality
            self._last_wordtree_result = tree_data
            
            # If we have tree_data, build interactive tree
            if tree_data and tree_data.get('children'):
                self._build_interactive_wordtree(tree_data)
            elif image_data:
                # Fallback to image display
                self._show_wordtree_image(image_data)
            else:
                self.wordtree_label.configure(text="No se encontraron relaciones")
                
        except Exception as e:
            logger.error(f"WordTree display error: {e}")
            self.wordtree_label.configure(text=f"Error: {e}")
    
    def _build_interactive_wordtree(self, tree_data: dict) -> None:
        """Build interactive tree with clickable nodes and collapse/expand."""
        # Clear previous content
        self.wordtree_label.configure(image=None, text="")
        
        # Initialize collapse state if not exists
        if not hasattr(self, 'wordtree_collapsed'):
            self.wordtree_collapsed = {}
        
        # Create a canvas with scroll for the tree
        if not hasattr(self, 'wordtree_canvas'):
            # Create canvas frame - darker background, más altura mínima
            self.wordtree_canvas_frame = ctk.CTkFrame(
                self.tab_wordtree, 
                fg_color="#1a1a1a",
                height=504  # Aumentado 40%
            )
            self.wordtree_canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            self.wordtree_canvas = ctk.CTkCanvas(self.wordtree_canvas_frame, bg="#1a1a1a", highlightthickness=0)
            self.wordtree_scrollbar = ctk.CTkScrollbar(self.wordtree_canvas_frame, command=self.wordtree_canvas.yview)
            self.wordtree_canvas.configure(yscrollcommand=self.wordtree_scrollbar.set)
            
            self.wordtree_scrollbar.pack(side="right", fill="y")
            self.wordtree_canvas.pack(side="left", fill="both", expand=True)
            
            self.wordtree_inner_frame = ctk.CTkFrame(self.wordtree_canvas, fg_color="#1a1a1a")
            self.wordtree_canvas.create_window((0, 0), window=self.wordtree_inner_frame, anchor="nw")
            
            # Configure scrollregion with proper bounds
            def update_scrollregion(event=None):
                bbox = self.wordtree_canvas.bbox("all")
                if bbox:
                    self.wordtree_canvas.configure(scrollregion=bbox)
            
            self.wordtree_inner_frame.bind("<Configure>", update_scrollregion)
        
        # Clear inner frame
        for widget in self.wordtree_inner_frame.winfo_children():
            widget.destroy()
        
        # Build the tree
        root_phrase = tree_data.get('root', '')
        
        # Root label (clickable to change root) - larger and more visible
        root_frame = ctk.CTkFrame(self.wordtree_inner_frame, fg_color="#1a1a1a")
        root_frame.pack(pady=(15, 10), fill="x")
        
        root_btn = ctk.CTkButton(
            root_frame,
            text=f"🌳 {root_phrase}",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#4A90D9",
            hover_color="#6BA8E0",
            text_color="white",
            command=lambda: self._expand_wordtree_node(root_phrase),
            width=350,
            height=45,
            corner_radius=8
        )
        root_btn.pack()
        
        ctk.CTkLabel(
            root_frame,
            text="(click para re-centrar)",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(pady=(5, 15))
        
        # Show children
        children = tree_data.get('children', [])
        if not children:
            ctk.CTkLabel(
                self.wordtree_inner_frame,
                text="No se encontraron palabras relacionadas",
                text_color="#888888"
            ).pack()
            return
        
        # Container for children - wider cards
        children_frame = ctk.CTkFrame(self.wordtree_inner_frame, fg_color="#1a1a1a")
        children_frame.pack(fill="x", padx=15, pady=10)
        
        # Draw each child as a card with solid colors
        for child in children:
            word = child.get('word', '')
            count = child.get('count', 0)
            subchildren = child.get('children', [])
            
            # Check if this node is collapsed
            is_collapsed = self.wordtree_collapsed.get(word, False)
            child_count = len(subchildren)
            
            # Card frame - solid dark background
            card = ctk.CTkFrame(children_frame, fg_color="#2d2d2d", corner_radius=10)
            card.pack(side="left", padx=8, pady=8, fill="both", expand=True)
            
            # Header frame with collapse/expand button
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=8, pady=(8, 0))
            
            # Collapse/expand button if has children
            if child_count > 0:
                collapse_btn = ctk.CTkButton(
                    header_frame,
                    text="−" if not is_collapsed else "+",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color="#4A4A4A",
                    hover_color="#5A5A5A",
                    text_color="white",
                    width=30,
                    height=30,
                    command=lambda w=word: self._toggle_wordtree_collapse(w),
                    corner_radius=4
                )
                collapse_btn.pack(side="left", padx=(0, 5))
            
            # Word button - solid color
            word_btn = ctk.CTkButton(
                card,
                text=word.title(),
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="#3A3A3A",
                hover_color="#505050",
                text_color="white",
                command=lambda w=word: self._expand_wordtree_node(w),
                width=140 if child_count == 0 else 110,
                height=40,
                corner_radius=6
            )
            word_btn.pack(padx=8, pady=(8 if child_count == 0 else 0, 4))
            
            # Count label with collapsed indicator - more visible
            count_text = f"🔢 {count} veces"
            if is_collapsed and child_count > 0:
                count_text += f" ({child_count} hidden)"
            
            ctk.CTkLabel(
                card,
                text=count_text,
                font=ctk.CTkFont(size=12),
                text_color="#AAAAAA"
            ).pack(pady=(0, 8))
            
            # Sub-children - show more clearly (only if not collapsed)
            if subchildren and not is_collapsed:
                sub_frame = ctk.CTkFrame(card, fg_color="transparent")
                sub_frame.pack(padx=8, pady=(0, 8))
                
                ctk.CTkLabel(
                    sub_frame,
                    text="Continúa:",
                    font=ctk.CTkFont(size=10),
                    text_color="#666666"
                ).pack(pady=(4, 4))
                
                for sub in subchildren[:4]:
                    sub_btn = ctk.CTkButton(
                        sub_frame,
                        text=f"→ {sub['word']} ({sub['count']})",
                        font=ctk.CTkFont(size=11),
                        fg_color="#252525",
                        hover_color="#404040",
                        text_color="#BBBBBB",
                        command=lambda w=sub['word']: self._expand_wordtree_node(w),
                        height=26,
                        width=120,
                        corner_radius=4
                    )
                    sub_btn.pack(pady=2)
            elif is_collapsed:
                # Show collapsed indicator
                ctk.CTkLabel(
                    card,
                    text=f"(Click + para expandir)",
                    font=ctk.CTkFont(size=10),
                    text_color="#666666"
                ).pack(pady=5)
        
        # Add export/zoom button at bottom
        export_frame = ctk.CTkFrame(self.wordtree_inner_frame, fg_color="#1a1a1a")
        export_frame.pack(fill="x", pady=(15, 10), padx=10)
        
        ctk.CTkButton(
            export_frame,
            text="🔍 Ver en detalle + Exportar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4A90D9",
            hover_color="#6BA8E0",
            text_color="white",
            command=self._open_wordtree_modal,
            height=35,
            corner_radius=6
        ).pack(pady=5)
    
    def _open_wordtree_modal(self) -> None:
        """Open WordTree in modal with zoom/pan and export options."""
        # Get the current tree image data from processor
        phrase = self.wordtree_phrase.get().strip()
        if not phrase:
            return
        
        try:
            from tools.text_tool.processor import analyze_wordtree
            from PIL import Image
            from io import BytesIO
            
            max_depth = int(self.wordtree_depth_slider.get())
            result = analyze_wordtree(self.text_content, phrase, max_depth=max_depth)
            
            if result.get('success') and result.get('image_data'):
                image_data = result['image_data']
                self._open_chart_modal(image_data, f"Árbol de Palabras: {phrase}")
            else:
                self.status_label.configure(text="No hay imagen para mostrar", text_color="orange")
                
        except Exception as e:
            logger.error(f"Error opening WordTree modal: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    def _expand_wordtree_node(self, word: str) -> None:
        """Expand tree from a specific word as new root."""
        if not self.text_content or not word:
            return
        
        # Update phrase input
        self.wordtree_phrase.delete(0, tk.END)
        self.wordtree_phrase.insert(0, word)
        
        # Re-run analysis
        self._run_wordtree_analysis()
        
        self.status_label.configure(text=f"Árbol re-centrado en: '{word}'", text_color="green")
    
    def _toggle_wordtree_collapse(self, word: str) -> None:
        """Toggle collapse/expand state of a node in the WordTree."""
        if not hasattr(self, 'wordtree_collapsed'):
            self.wordtree_collapsed = {}
        
        # Toggle state
        self.wordtree_collapsed[word] = not self.wordtree_collapsed.get(word, False)
        
        # Re-render the tree to reflect the change
        # Get current tree data from the last result
        if hasattr(self, '_last_wordtree_result'):
            self._build_interactive_wordtree(self._last_wordtree_result)
        
        status = "colapsado" if self.wordtree_collapsed[word] else "expandido"
        self.status_label.configure(text=f"Nodo '{word}' {status}", text_color="green")
    
    def _show_wordtree_image(self, image_data) -> None:
        """Display WordTree as image (fallback)."""
        try:
            from PIL import Image
            from io import BytesIO
            
            if not isinstance(image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(image_data)}")
            
            img = Image.open(BytesIO(image_data))
            img.thumbnail((700, 400))
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            self.wordtree_label.configure(image=ctk_img, text="")
            self.wordtree_label.image = ctk_img
            
            # Add click binding to open modal
            self.wordtree_label.unbind("<Button-1>")
            self.wordtree_label.bind("<Button-1>", lambda e: self._open_chart_modal(image_data, "Árbol de Palabras"))
            
            self.wordtree_label.configure(cursor="hand2")
            
        except Exception as e:
            self.wordtree_label.configure(text=f"Error: {e}")
    
    # ============ CHART MODAL ============
    def _open_chart_modal(self, image_data, title: str) -> None:
        """Opens expanded chart view in modal window."""
        # Validate image_data - could be bytes or could be something else
        if image_data is None:
            self.status_label.configure(text="No hay imagen para mostrar", text_color="orange")
            return
        
        # Check if it's bytes
        if not isinstance(image_data, (bytes, bytearray)):
            logger.warning(f"image_data is not bytes, it's: {type(image_data)}")
            self.status_label.configure(text="Error: datos de imagen inválidos", text_color="orange")
            return
        
        if len(image_data) == 0:
            self.status_label.configure(text="Imagen vacía", text_color="orange")
            return
        
        # Create modal window
        modal = ChartModal(self, image_data, title, self.status_label)
    
    def _export_chart(self, image_data: bytes, format: str, default_filename: str) -> bool:
        """Export chart as PNG (300 DPI) or PDF (vector)."""
        if image_data is None:
            return False
        
        from datetime import datetime
        from PIL import Image
        from io import BytesIO
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{default_filename}_{timestamp}"
        
        if format == "png":
            filename = filedialog.asksaveasfilename(
                title="Guardar imagen PNG",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("All files", "*.*")],
                initialfile=f"{default_name}.png"
            )
            if not filename:
                return False
            
            try:
                # Save as PNG with high quality (300 DPI equivalent)
                img = Image.open(BytesIO(image_data))
                # Set DPI to 300 for high quality print
                img.save(filename, "PNG", dpi=(300, 300))
                return True
            except Exception as e:
                logger.error(f"Error exporting PNG: {e}")
                return False
        
        elif format == "pdf":
            filename = filedialog.asksaveasfilename(
                title="Guardar como PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
                initialfile=f"{default_name}.pdf"
            )
            if not filename:
                return False
            
            try:
                # Use matplotlib to save as PDF (vector quality)
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_pdf import PdfPages
                import numpy as np
                from PIL import Image
                
                # Open image and convert to numpy array
                img = Image.open(BytesIO(image_data))
                
                # Save to PDF using matplotlib
                with PdfPages(filename) as pdf:
                    fig = plt.figure(figsize=(10, 8))
                    plt.imshow(np.array(img), aspect='auto')
                    plt.axis('off')
                    plt.tight_layout(pad=0)
                    pdf.savefig(fig, bbox_inches='tight', dpi=300)
                    plt.close(fig)
                return True
            except Exception as e:
                logger.error(f"Error exporting PDF: {e}")
                return False
        
        return False


class ChartModal(ctk.CTkToplevel):
    """Modal for expanded chart view with export."""
    
    def __init__(self, parent, image_data: bytes, title: str, status_label):
        super().__init__(parent)
        
        self.image_data = image_data
        self.title_text = title
        self.status_label = status_label
        self._current_width = 800
        self._current_height = 600
        
        # Configure modal window
        self.title(f"📊 {title}")
        
        # Set minimum size 600x600, start at 800x600
        self.minsize(600, 600)
        self.geometry("800x600")
        self._current_width = 800
        self._current_height = 600
        
        # Center on screen
        self._center_window()
        
        # Make modal transient (stays on top of parent)
        self.transient(parent)
        
        # Grab focus
        self.grab_set()
        
        # Setup UI
        self._setup_ui()
        
        # Bind Escape key to close
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self.destroy)
    
    def _on_scroll(self, event) -> str:
        """Handle scroll events - zoom only (Linux + Windows)."""
        try:
            from PIL import Image, ImageTk
            
            if not hasattr(self, 'zoom_level'):
                self.zoom_level = 1.0
            
            # Cross-platform: Linux uses event.num (Button-4/Button-5), Windows uses event.delta (MouseWheel)
            if hasattr(event, 'num') and event.num in (4, 5):
                # Linux scroll: Button-4 = scroll up, Button-5 = scroll down
                if event.num == 4:
                    self.zoom_level *= 1.2  # Zoom in
                else:
                    self.zoom_level *= 0.8  # Zoom out
            elif hasattr(event, 'delta') and event.delta != 0:
                # Windows MouseWheel
                if event.delta > 0:
                    self.zoom_level *= 1.2  # Zoom in
                else:
                    self.zoom_level *= 0.8  # Zoom out
            else:
                return "break"
            
            # Limit zoom range (0.5x to 5x)
            self.zoom_level = max(0.5, min(5.0, self.zoom_level))
            
            # Get original image and apply zoom
            if hasattr(self, 'full_image') and self.full_image:
                orig_width, orig_height = self.full_image.size
                new_width = int(orig_width * self.zoom_level)
                new_height = int(orig_height * self.zoom_level)
                
                # Resize keeping aspect ratio
                img_display = self.full_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Update canvas
                self.photo_img = ImageTk.PhotoImage(img_display)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
                self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
                
        except Exception as e:
            logger.error(f"Zoom error: {e}")
        
        return "break"
    
    def _on_drag_start(self, event) -> None:
        """Start drag for panning."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def _on_drag_motion(self, event) -> None:
        """Pan the canvas during drag - smooth movement."""
        if hasattr(self, '_drag_start_x'):
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            
            # Move the canvas content directly (smoother than scroll)
            self.canvas.move("all", dx, dy)
            
            self._drag_start_x = event.x
            self._drag_start_y = event.y
    
    def _on_drag_release(self, event) -> None:
        """End drag."""
        if hasattr(self, '_drag_start_x'):
            del self._drag_start_x
            del self._drag_start_y
    
    def _center_window(self) -> None:
        """Center the modal on screen."""
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Get modal dimensions (use minsize if not yet set)
        modal_width = max(self.winfo_width(), self._current_width)
        modal_height = max(self.winfo_height(), self._current_height)
        
        # Calculate center position
        x = (screen_width - modal_width) // 2
        y = max(50, (screen_height - modal_height) // 2)  # At least 50px from top
        
        # Apply position
        self.geometry(f"{modal_width}x{modal_height}+{x}+{y}")
    
    def _setup_ui(self) -> None:
        """Setup modal UI components."""
        
        # Title bar frame
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title label
        title_label = ctk.CTkLabel(
            title_frame,
            text=f"📊 {self.title_text}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=5)
        
        # Hint for controls
        hint_label = ctk.CTkLabel(
            title_frame,
            text="(Scroll = zoom, arrastrar = mover)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        hint_label.pack(side="left", padx=10)
        
        # Image container frame with scrollbars for small screens
        img_container = ctk.CTkFrame(self)
        img_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas with scrollbars for small viewports
        self.canvas_frame = ctk.CTkFrame(img_container, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Canvas for image
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0, takefocus=True)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbars (will show only if needed)
        v_scrollbar = ctk.CTkScrollbar(self.canvas_frame, command=self.canvas.yview, orientation="vertical")
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = ctk.CTkScrollbar(self, command=self.canvas.xview, orientation="horizontal")
        h_scrollbar.pack(fill="x")
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Bind scroll events - zoom in/out (cross-platform: Windows MouseWheel + Linux Button-4/5)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", self._on_scroll)
        self.canvas.bind("<Button-5>", self._on_scroll)
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Button-4>", self._on_scroll)
        self.bind("<Button-5>", self._on_scroll)
        
        # Bind drag events for panning - left click + drag
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_release)
        self.canvas.configure(cursor="hand2")
        
        # Focus on canvas so scroll works
        self.canvas.focus_set()
        
        # Display image
        try:
            from PIL import Image, ImageTk
            from io import BytesIO
            
            # Validate image_data before processing
            if not isinstance(self.image_data, (bytes, bytearray)):
                raise ValueError(f"image_data debe ser bytes, recibido: {type(self.image_data)}")
            
            if len(self.image_data) == 0:
                raise ValueError("image_data está vacío")
            
            # Open image
            img = Image.open(BytesIO(self.image_data))
            
            # Get original size (but limit for very large images)
            orig_width, orig_height = img.size
            
            # Calculate display size (fit to modal if too large)
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            max_width = min(orig_width, int(screen_width * 0.9))
            max_height = min(orig_height, int(screen_height * 0.8))
            
            # Calculate scaled size maintaining aspect ratio
            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            ratio = min(width_ratio, height_ratio, 1)  # Don't upscale
            
            display_width = int(orig_width * ratio)
            display_height = int(orig_height * ratio)
            
            # Convert to CTk compatible image
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize for display
            img_display = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            
            # Create PhotoImage for tkinter canvas (NOT CTkImage)
            self.photo_img = ImageTk.PhotoImage(img_display)
            
            # Display on canvas
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Store original image for export
            self.full_image = img
            
        except Exception as e:
            logger.error(f"Error displaying image in modal: {e}")
            error_label = ctk.CTkLabel(
                self.canvas_frame,
                text=f"Error al cargar imagen: {e}",
                text_color="red"
            )
            error_label.pack()
        
        # Export buttons frame
        export_frame = ctk.CTkFrame(self)
        export_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Export label and buttons on left
        export_label = ctk.CTkLabel(export_frame, text="Exportar:", font=ctk.CTkFont(size=12, weight="bold"))
        export_label.pack(side="left", padx=10)
        
        # PNG export button
        png_btn = ctk.CTkButton(
            export_frame,
            text="💾 PNG",
            command=self._export_png,
            width=100
        )
        png_btn.pack(side="left", padx=5, pady=5)
        
        # PDF export button
        pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 PDF",
            command=self._export_pdf,
            width=100
        )
        pdf_btn.pack(side="left", padx=5, pady=5)
        
        # Close button - on right
        close_btn = ctk.CTkButton(
            export_frame,
            text="✕ Cerrar",
            command=self.destroy,
            width=100,
            fg_color="#c44",
            hover_color="#a33"
        )
        close_btn.pack(side="right", padx=10, pady=5)
    
    def _on_image_click(self, event) -> None:
        """Handle click on image - expand to full size."""
        try:
            from PIL import Image, ImageTk
            from io import BytesIO
            
            # Open original image at full size
            img = Image.open(BytesIO(self.image_data))
            
            # Calculate new size (fit to screen but show full)
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            max_width = int(screen_width * 0.95)
            max_height = int(screen_height * 0.9)
            
            orig_width, orig_height = img.size
            
            # Calculate scaled size
            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            ratio = min(width_ratio, height_ratio, 1)
            
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)
            
            # Resize
            img_full = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Update canvas with larger image
            if img_full.mode != 'RGBA':
                img_full = img_full.convert('RGBA')
            
            # Use PhotoImage for canvas (NOT CTkImage)
            photo_img = ImageTk.PhotoImage(img_full)
            
            # Clear and redraw
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=photo_img)
            
            # Keep reference to prevent garbage collection
            self.photo_img = photo_img
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Resize window to fit image
            new_geometry = f"{new_width + 40}x{new_height + 120}"
            self.geometry(new_geometry)
            self._center_window()
            
            # Update stored image
            self.full_image = img
            
        except Exception as e:
            logger.error(f"Error expanding image: {e}")
    
    def _export_png(self) -> None:
        """Export chart as PNG."""
        try:
            from datetime import datetime
            from PIL import Image
            from io import BytesIO
            
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{self.title_text.lower().replace(' ', '_')}_{timestamp}"
            
            filename = filedialog.asksaveasfilename(
                title="Guardar imagen PNG",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("All files", "*.*")],
                initialfile=f"{default_name}.png"
            )
            
            if not filename:
                return
            
            # Get the full size image
            if hasattr(self, 'full_image'):
                img = self.full_image
            else:
                img = Image.open(BytesIO(self.image_data))
            
            # Save with high DPI
            img.save(filename, "PNG", dpi=(300, 300))
            
            # Update status
            self.status_label.configure(text=f"✅ PNG guardado: {filename}", text_color="green")
            
        except Exception as e:
            logger.error(f"Error exporting PNG: {e}")
            self.status_label.configure(text=f"❌ Error al guardar PNG: {e}", text_color="red")
    
    def _export_pdf(self) -> None:
        """Export chart as PDF."""
        try:
            from datetime import datetime
            from PIL import Image
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
            import numpy as np
            from io import BytesIO
            
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{self.title_text.lower().replace(' ', '_')}_{timestamp}"
            
            filename = filedialog.asksaveasfilename(
                title="Guardar como PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
                initialfile=f"{default_name}.pdf"
            )
            
            if not filename:
                return
            
            # Get the image
            if hasattr(self, 'full_image'):
                img = self.full_image
            else:
                img = Image.open(BytesIO(self.image_data))
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Save to PDF
            with PdfPages(filename) as pdf:
                fig = plt.figure(figsize=(10, 8))
                plt.imshow(img_array, aspect='auto')
                plt.axis('off')
                plt.tight_layout(pad=0)
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
                plt.close(fig)
            
            # Update status
            self.status_label.configure(text=f"✅ PDF guardado: {filename}", text_color="green")
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            self.status_label.configure(text=f"❌ Error al guardar PDF: {e}", text_color="red")