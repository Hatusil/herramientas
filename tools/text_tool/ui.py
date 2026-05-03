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

logger = logging.getLogger(__name__)
class TextAnalyzerUI(ctk.CTkFrame):
    """UI para análisis de texto."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.text_content: str = ""
        self.sources: Dict[str, Any] = {"text": [], "files": [], "urls": []}
        self._setup_ui()
    
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
                "   ☁️ WordCloud - nube de palabras",
                "   📈 Frecuencia - palabras más usadas",
                "   📉 Stats - estadísticas del texto",
                "   🔗 N-grams - frases repetidas",
                "   📊 Trends - frecuencia por secciones",
                "   🔥 Correlaciones - palabras que van juntas",
                "   ⬡ Scatter - distribución de términos"
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
    
    # ============ TAB: LIMPIEZA ============
    def _setup_clean_tab(self) -> None:
        frame = self.tab_clean
        
        # Fuentes summary
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
        
        # Frequency preview (antes de generar charts)
        freq_preview_label = ctk.CTkLabel(frame, text="🔍 Preview Frecuencia (top 20):", font=ctk.CTkFont(weight="bold"))
        freq_preview_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.freq_preview_text = ctk.CTkTextbox(frame, wrap="word", height=100, font=("Courier New", 12))
        self.freq_preview_text.pack(fill="x", padx=10, pady=5)
        
        # Texto crudo (sin limpiar)
        raw_label = ctk.CTkLabel(frame, text="📄 Texto crudo:", font=ctk.CTkFont(weight="bold"))
        raw_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.raw_text = ctk.CTkTextbox(frame, wrap="word", height=80)
        self.raw_text.pack(fill="x", padx=10, pady=5)
        
        # Opciones de limpieza
        opts_label = ctk.CTkLabel(frame, text="⚙️ Opciones:", font=ctk.CTkFont(weight="bold"))
        opts_label.pack(anchor="w", padx=10, pady=10)
        
        opts_frame = ctk.CTkFrame(frame)
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        self.remove_stopwords = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts_frame, text="Quitar conectores (stopwords)", variable=self.remove_stopwords).pack(anchor="w", padx=5)
        
        ctk.CTkLabel(opts_frame, text="Excluir palabras:").pack(anchor="w", padx=5, pady=(5, 0))
        self.exclude_entry = ctk.CTkEntry(opts_frame, placeholder_text="que, como, pero, ...")
        self.exclude_entry.pack(fill="x", padx=5, pady=5)
        
        # Botón aplicar
        ctk.CTkButton(frame, text="🔄 Aplicar Limpieza", command=self._apply_clean).pack(pady=10)
        
        # Preview limpio
        preview_label = ctk.CTkLabel(frame, text="✅ Texto limpio (preview):", font=ctk.CTkFont(weight="bold"))
        preview_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.clean_text = ctk.CTkTextbox(frame, wrap="word", height=80)
        self.clean_text.pack(fill="x", padx=10, pady=5)
        
        # Botón generar visualizaciones
        ctk.CTkButton(frame, text="📊 Generar Visualizaciones", command=self._run_all_analysis).pack(pady=10)
    
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
        
        # Mostrar texto crudo y limpio
        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert("1.0", self.text_content[:2000])
        
        self.clean_text.delete("1.0", tk.END)
        self.clean_text.insert("1.0", cleaned[:2000])  # Preview primeros 2000 chars
        
        from collections import Counter
        words = cleaned.lower().split()
        word_freq = Counter(words)
        top_20 = word_freq.most_common(20)
        
        preview = "Top 20 palabras:\n" + "=" * 25 + "\n"
        for i, (word, count) in enumerate(top_20, 1):
            preview += f"{i:2}. {word:<15} {count:>4}\n"
        
        self.freq_preview_text.delete("1.0", tk.END)
        self.freq_preview_text.insert("1.0", preview)
        
        self.cleaned_content = cleaned
        self.status_label.configure(text=f"Limpieza aplicada: {len(cleaned.split())} palabras", text_color="green")
    
    def _remove_source(self, source_type: str) -> None:
        """Quita un tipo de fuente y resetea todo el contenido."""
        if not self.text_content and not self.sources[source_type]:
            return
        
        self.text_content = ""
        self.cleaned_content = None
        self.raw_text.delete("1.0", tk.END)
        self.clean_text.delete("1.0", tk.END)
        self.freq_preview_text.delete("1.0", tk.END)
        self.sources = {"text": [], "files": [], "urls": []}
        
        self._update_sources_summary()
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
        
        ctk.CTkLabel(self.file_frame, text="📄 Agregar Archivos", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
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
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="Cargá texto o archivo para analizar",
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
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
                self.status_label.configure(
                    text=f"{len(urls)} URLs: {len(self.text_content)} caracteres - andá a Limpieza",
                    text_color="green"
                )
                if hasattr(self, 'raw_text'):
                    self.raw_text.delete("1.0", tk.END)
                    self.raw_text.insert("1.0", self.text_content[:5000])
                
                logger.info(f"URL SCRAPER: Done - final text_content is {len(self.text_content)} chars")
            
            # No ejecutar análisis automáticamente - usuario debe ir a Limpieza
        
        except ImportError:
            self.status_label.configure(
                text="Installa dependencias: pip install wordcloud nltk pdfplumber requests beautifulsoup4",
                text_color="red"
            )
    
    def _run_all_analysis(self) -> None:
        """Ejecuta todos los análisis."""
        if not self.text_content:
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
                clean_text
            )
            
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
            
            # WordCloud
            wc_result = analyze_wordcloud(cleaned)
            if wc_result.get('success') and wc_result.get('image_data'):
                self._show_wordcloud(wc_result['image_data'])
            
            # Frecuencia
            freq_result = analyze_frequency(cleaned)
            if freq_result.get('success'):
                self._show_frequency(freq_result['frequencies'])
            
            # Stats
            stats_result = analyze_stats(cleaned)
            if stats_result.get('success'):
                self._show_stats(stats_result)
            
            # N-grams
            ngram_result = analyze_ngrams(cleaned, n=2)
            if ngram_result.get('success'):
                self._show_ngrams(ngram_result['ngrams'])
            
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
            
            self.status_label.configure(text="Análisis completo!", text_color="green")
            
        except Exception as e:
            import traceback
            logger.error(f"Error analysis: {e}")
            traceback.print_exc()
            self.status_label.configure(text=f"Error: {e}", text_color="red")
    
    # ============ TAB: WORDCLOUD ============
    def _setup_wc_tab(self) -> None:
        frame = self.tab_wc
        
        # Campo para excluir palabras (después de ver la nube)
        exclude_frame = ctk.CTkFrame(frame)
        exclude_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(exclude_frame, text="Excluir palabras:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5)
        
        self.wc_exclude_entry = ctk.CTkEntry(exclude_frame, placeholder_text="palabra1, palabra2, ...")
        self.wc_exclude_entry.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(exclude_frame, text="🔄 Regenerar sin estas palabras", command=self._regenerate_wc).pack(pady=5)
        
        self.wc_label = ctk.CTkLabel(
            frame,
            text="WordCloud aparecerá aquí",
            text_color="gray"
        )
        self.wc_label.pack(expand=True)
    
    def _show_wordcloud(self, image_data: bytes) -> None:
        """Muestra WordCloud."""
        try:
            from PIL import Image
            from io import BytesIO
            
            # Abrir imagen desde bytes
            img = Image.open(BytesIO(image_data))
            
            # Resize para display (más pequeño)
            img.thumbnail((600, 300))
            
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
            
        except Exception as e:
            import traceback
            logger.error(f"WordCloud error: {e}")
            logger.debug(traceback.format_exc())
            self.wc_label.configure(text=f"Error: {e}")
    
    def _regenerate_wc(self) -> None:
        """Regenera WordCloud sin palabras excluidas."""
        if not self.text_content:
            self.status_label.configure(text="No hay texto cargado", text_color="orange")
            return
        
        # Obtener palabras a excluir
        exclude_text = self.wc_exclude_entry.get().strip()
        exclude_words = [w.strip().lower() for w in exclude_text.split(',')] if exclude_text else []
        
        from tools.text_tool.processor import analyze_wordcloud, clean_text
        
        # Limpiar con palabras excluidas
        cleaned = clean_text(self.text_content, remove_stopwords=True, exclude_words=exclude_words)
        
        # Generar nuevo WordCloud
        result = analyze_wordcloud(cleaned)
        
        if result.get('success') and result.get('image_data'):
            self._show_wordcloud(result['image_data'])
            self.status_label.configure(text=f"WordCloud regenerado ({len(cleaned.split())} palabras)", text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
    
    # ============ TAB: FRECUENCIA ============
    def _setup_freq_tab(self) -> None:
        frame = self.tab_freq
        
        self.freq_text = ctk.CTkTextbox(frame, font=("Courier New", 14))
        self.freq_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _show_frequency(self, frequencies: Dict[str, int]) -> None:
        """Muestra frecuencia de palabras."""
        self.freq_text.delete("1.0", tk.END)
        
        texto = "📈 Palabras más frecuentes\n"
        texto += "=" * 30 + "\n\n"
        
        for i, (word, count) in enumerate(frequencies.items(), 1):
            texto += f"{i:2}. {word:<20} {count:>5}\n"
        
        self.freq_text.insert("1.0", texto)
    
    # ============ TAB: ESTADÍSTICAS ============
    def _setup_stats_tab(self) -> None:
        frame = self.tab_stats
        
        stats_frame = ctk.CTkFrame(frame)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.stats_text = ctk.CTkTextbox(stats_frame, font=("Courier New", 15))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _show_stats(self, stats: Dict[str, Any]) -> None:
        """Muestra estadísticas."""
        self.stats_text.delete("1.0", tk.END)
        
        texto = "📉 Estadísticas del Texto\n"
        texto += "=" * 30 + "\n\n"
        
        texto += f"Caracteres totales:     {stats.get('total_chars', 0):,}\n"
        texto += f"Palabras totales:      {stats.get('total_words', 0):,}\n"
        texto += f"Palabras únicas:        {stats.get('unique_words', 0):,}\n"
        texto += f"Oraciones:             {stats.get('total_sentences', 0):,}\n"
        texto += "\n"
        texto += f"Longitud promedio palabra: {stats.get('avg_word_length', 0):.2f}\n"
        texto += f"Longitud promedio oración: {stats.get('avg_sentence_length', 0):.2f}\n"
        texto += f"Type-Token Ratio:       {stats.get('type_token_ratio', 0):.4f}\n"
        
        self.stats_text.insert("1.0", texto)
    
    # ============ TAB: N-GRAMS ============
    def _setup_ngram_tab(self) -> None:
        frame = self.tab_ngram
        
        opts = ctk.CTkFrame(frame)
        opts.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(opts, text="N-gram size:").pack(side="left", padx=10)
        
        self.ngram_size = ctk.IntVar(value=2)
        
        for n in [2, 3]:
            ctk.CTkRadioButton(
                opts, 
                text=f"{n}-grams", 
                variable=self.ngram_size, 
                value=n
            ).pack(side="left", padx=10)
        
        self.ngram_text = ctk.CTkTextbox(frame, font=("Courier New", 14))
        self.ngram_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _show_ngrams(self, ngrams: Dict[str, int]) -> None:
        """Muestra n-grams."""
        self.ngram_text.delete("1.0", tk.END)
        
        texto = f"🔗 N-grams ({self.ngram_size.get()})\n"
        texto += "=" * 30 + "\n\n"
        
        for i, (ng, count) in enumerate(ngrams.items(), 1):
            texto += f"{i:2}. {ng:<30} {count:>4}\n"
        
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
    
    def _show_trends(self, image_data: bytes) -> None:
        """Muestra gráfico de tendencias."""
        try:
            from PIL import Image
            from io import BytesIO
            
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
    
    def _show_correlations(self, image_data: bytes) -> None:
        """Muestra heatmap de correlaciones."""
        try:
            from PIL import Image
            from io import BytesIO
            
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
    
    def _show_scatter(self, image_data: bytes) -> None:
        """Muestra scatter plot."""
        try:
            from PIL import Image
            from io import BytesIO
            
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
            
        except Exception as e:
            self.scatter_label.configure(text=f"Error: {e}")