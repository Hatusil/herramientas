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
        if not self.text_content:
            self.status_label.configure(text="No hay texto cargado", text_color="orange")
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
        
        # Slider frame
        slider_frame = ctk.CTkFrame(frame)
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
        
        # Text view - taller with expand=True
        self.freq_text = ctk.CTkTextbox(frame, font=("Courier New", 14), height=300)
        self.freq_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def _on_freq_slider_change(self, value: float) -> None:
        """Handle frequency slider change - update display after release."""
        n = int(value)
        self.freq_label.configure(text=f"{n} palabras")
    
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
        opts.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(opts, text="N-gram size:").pack(side="left", padx=10)
        
        self.ngram_size = ctk.IntVar(value=2)
        
        for n in [2, 3]:
            ctk.CTkRadioButton(
                opts, 
                text=f"{n}-grams", 
                variable=self.ngram_size, 
                value=n
            ).pack(side="left", padx=10)
        
        # Slider frame for top_k
        slider_frame = ctk.CTkFrame(frame)
        slider_frame.pack(fill="x", padx=10, pady=(5, 10))
        
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
        
        # Text view - taller with expand=True
        self.ngram_text = ctk.CTkTextbox(frame, font=("Courier New", 14), height=300)
        self.ngram_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def _on_ngram_slider_change(self, value: float) -> None:
        """Handle n-gram slider change - update label."""
        top_k = int(value)
        self.ngram_label.configure(text=f"{top_k} resultados")
    
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
        """Handle scroll events - zoom in/out, prevent propagation to parent."""
        try:
            from PIL import Image, ImageTk
            
            # Determine zoom factor based on delta
            if event.delta > 0:
                zoom_factor = 1.2  # Zoom in
            else:
                zoom_factor = 0.8  # Zoom out
            
            # Get current image
            if hasattr(self, 'full_image') and self.full_image:
                orig_width, orig_height = self.full_image.size
                
                # Calculate new size
                new_width = int(orig_width * zoom_factor)
                new_height = int(orig_height * zoom_factor)
                
                # Limit zoom range (200-4000px)
                if new_width < 200:
                    return "break"
                if new_width > 4000:
                    return "break"
                
                # Resize
                img_display = self.full_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Update canvas
                self.photo_img = ImageTk.PhotoImage(img_display)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                # Update window size
                self.geometry(f"{new_width + 40}x{new_height + 120}")
                self._current_width = new_width + 40
                self._current_height = new_height + 120
                
        except Exception as e:
            logger.error(f"Zoom error: {e}")
        
        return "break"
    
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
        
        # Click instruction label
        hint_label = ctk.CTkLabel(
            title_frame,
            text="(Click en la imagen para expandir)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        hint_label.pack(side="left", padx=10)
        
        # Close button (X)
        close_btn = ctk.CTkButton(
            title_frame,
            text="✕",
            width=30,
            height=30,
            command=self.destroy,
            fg_color="#c44",
            hover_color="#a33"
        )
        close_btn.pack(side="right", padx=5)
        
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
        
        # Bind scroll events - zoom in/out
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.bind("<MouseWheel>", self._on_scroll)
        
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
        
        # Export buttons on bottom-right
        export_label = ctk.CTkLabel(export_frame, text="Exportar:", font=ctk.CTkFont(size=12, weight="bold"))
        export_label.pack(side="left", padx=10)
        
        # PNG export button
        png_btn = ctk.CTkButton(
            export_frame,
            text="💾 Exportar como PNG",
            command=self._export_png,
            width=160
        )
        png_btn.pack(side="right", padx=5, pady=5)
        
        # PDF export button
        pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 Exportar como PDF",
            command=self._export_pdf,
            width=160
        )
        pdf_btn.pack(side="right", padx=5, pady=5)
    
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