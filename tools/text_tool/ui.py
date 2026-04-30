import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)
class TextAnalyzerUI(ctk.CTkFrame):
    """UI para análisis de texto."""
    
    def __init__(self, master, on_process: Callable):
        super().__init__(master)
        self.on_process = on_process
        self.text_content: str = ""
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
        self._setup_wc_tab()
        self._setup_freq_tab()
        self._setup_stats_tab()
        self._setup_ngram_tab()
        self._setup_trends_tab()
        self._setup_corr_tab()
        self._setup_scatter_tab()
    
    # ============ TAB: ENTRADA ============
    def _setup_input_tab(self) -> None:
        frame = self.tab_input
        
        # Input tipo selector
        tipo_frame = ctk.CTkFrame(frame)
        tipo_frame.pack(fill="x", padx=10, pady=10)
        
        self.input_type = ctk.StringVar(value="text")
        
        ctk.CTkRadioButton(
            tipo_frame, text="📝 Texto", 
            variable=self.input_type, value="text",
            command=self._on_input_type_change
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            tipo_frame, text="📄 Archivo", 
            variable=self.input_type, value="file",
            command=self._on_input_type_change
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            tipo_frame, text="🌐 URL", 
            variable=self.input_type, value="url",
            command=self._on_input_type_change
        ).pack(side="left", padx=10)
        
        # Área de texto (para input directo)
        self.text_input_area = ctk.CTkTextbox(frame, wrap="word")
        self.text_input_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para archivo (oculto por defecto)
        self.file_frame = ctk.CTkFrame(frame)
        self.file_frame.pack(fill="x", padx=10, pady=10)
        self.file_frame.pack_forget()
        
        ctk.CTkLabel(self.file_frame, text="Archivo:").pack(anchor="w")
        
        file_btn_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        file_btn_frame.pack(fill="x", pady=5)
        
        self.file_label = ctk.CTkLabel(
            file_btn_frame, 
            text="Ningún archivo seleccionado",
            text_color="gray"
        )
        self.file_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            file_btn_frame, 
            text="Seleccionar...", 
            command=self._select_file
        ).pack(side="left", padx=5)
        
        self.selected_file: Optional[str] = None
        
        # Frame para URL (oculto por defecto)
        self.url_frame = ctk.CTkFrame(frame)
        self.url_frame.pack(fill="x", padx=10, pady=10)
        self.url_frame.pack_forget()
        
        ctk.CTkLabel(self.url_frame, text="URL:").pack(anchor="w")
        
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="https://...")
        self.url_entry.pack(fill="x", pady=5)
        
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
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="Cargá texto o archivo para analizar",
            text_color="gray"
        )
        self.status_label.pack(pady=5)
    
    def _on_input_type_change(self) -> None:
        """Cambia visibilidad según tipo de input."""
        tipo = self.input_type.get()
        
        self.text_input_area.pack_forget()
        self.file_frame.pack_forget()
        self.url_frame.pack_forget()
        
        if tipo == "text":
            self.text_input_area.pack(fill="both", expand=True, padx=10, pady=10)
            self.load_btn.configure(text="📥 Analizar Texto")
        elif tipo == "file":
            self.file_frame.pack(fill="x", padx=10, pady=10)
            self.load_btn.configure(text="📄 Cargar y Analizar")
        elif tipo == "url":
            self.url_frame.pack(fill="x", padx=10, pady=10)
            self.load_btn.configure(text="🌐 Scrapear y Analizar")
    
    def _select_file(self) -> None:
        """Seleccionar archivo."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Texto", "*.txt *.md *.py *.js *.html"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx *.doc"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=Path(file_path).name)
    
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
                self.text_content = text
                self.status_label.configure(text=f"Texto cargado: {len(text)} caracteres", text_color="green")
            
            elif tipo == "file":
                if not self.selected_file:
                    self.status_label.configure(text="Seleccioná archivo", text_color="orange")
                    return
                
                result = extract_text_from_file(self.selected_file)
                if not result['success']:
                    self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
                    return
                
                self.text_content = result['text']
                self.status_label.configure(text=f"Archivo cargado: {len(self.text_content)} caracteres", text_color="green")
            
            elif tipo == "url":
                url = self.url_entry.get().strip()
                if not url:
                    self.status_label.configure(text="Ingresá URL", text_color="orange")
                    return
                
                self.status_label.configure(text="Scapeando...", text_color="yellow")
                self.update()
                
                result = extract_text_from_url(url)
                if not result['success']:
                    self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
                    return
                
                self.text_content = result['text']
                self.status_label.configure(text=f"URL scrapeada: {len(self.text_content)} caracteres", text_color="green")
            
            # Ejecutar análisis si hay texto
            if self.text_content:
                self._run_all_analysis()
        
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
                analyze_scatter
            )
            
            # WordCloud
            wc_result = analyze_wordcloud(self.text_content)
            if wc_result.get('success') and wc_result.get('image_data'):
                self._show_wordcloud(wc_result['image_data'])
            
            # Frecuencia
            freq_result = analyze_frequency(self.text_content)
            if freq_result.get('success'):
                self._show_frequency(freq_result['frequencies'])
            
            # Stats
            stats_result = analyze_stats(self.text_content)
            if stats_result.get('success'):
                self._show_stats(stats_result)
            
            # N-grams
            ngram_result = analyze_ngrams(self.text_content, n=2)
            if ngram_result.get('success'):
                self._show_ngrams(ngram_result['ngrams'])
            
            # Trends
            trends_result = analyze_trends(self.text_content)
            if trends_result.get('success') and trends_result.get('image_data'):
                self._show_trends(trends_result['image_data'])
            
            # Correlations
            corr_result = analyze_correlations(self.text_content)
            if corr_result.get('success') and corr_result.get('image_data'):
                self._show_correlations(corr_result['image_data'])
            
            # Scatter
            scatter_result = analyze_scatter(self.text_content)
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