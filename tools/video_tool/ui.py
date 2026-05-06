"""UI: Interfaz para herramienta de video."""
import sys
import os
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import List, Callable

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


class VideoToolUI(BaseToolUI):
    """UI para procesamiento básico de video."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific tabs
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_extract = self.tabview.add("Extraer Audio")
        self.tab_convert = self.tabview.add("Convertir")
        self.tab_info = self.tabview.add("Info")
        
        self._setup_extract_tab()
        self._setup_convert_tab()
        self._setup_info_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivo de video:"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filter for video files."""
        return [
            ("Videos", "*.mp4 *.avi *.mkv *.mov *.webm *.wmv *.flv"),
            ("Todos", "*.*")
        ]
    
    def _setup_ui(self) -> None:
        title = ctk.CTkLabel(
            self, 
            text="Herramienta de Video", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Help panel
        help_panel = add_help(
            self,
            description="🎬 Procesa video: extrae audio, convierte formato, muestra info (bitrate, fps)",
            usage=[
                "1. 📥 Agregar videos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                "3. 📑 Elegir operación (Extraer Audio/Convertir/Info)",
                "4. ⚙️ Configurar formato y calidad CRF",
                "5. ▶️ Click en ejecutar (procesa solo los seleccionados)"
            ],
            warnings=[
                "⚠️ CRF: 18=mejor calidad, 23=normal, 28=más baja",
                "⚠️ mp4→mp4 con CRF23 se omite (ya en formato)",
                "⚠️ Cambiar CRF para forzar recodificación",
                "⚠️ Conversión puede tardar minutos",
                "⚠️ FFmpeg debe estar instalado",
                "⚠️ Archivos >1GB necesitan mucho espacio"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI)
    
    def _hide_progress_bar(self, progress_bar) -> None:
        """Oculta la barra de progreso."""
        progress_bar.set(0)
        progress_bar.pack_forget()
    
    def _setup_extract_tab(self) -> None:
        frame = self.tab_extract
        
        ctk.CTkLabel(
            frame, 
            text="Extraer audio de video:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=10)
        
        ctk.CTkLabel(fmt_frame, text="Formato:").pack(side="left", padx=5)
        self.audio_format = ctk.StringVar(value="mp3")
        
        rb_font = ("Segoe UI", 12)
        RadioButton(fmt_frame, text="MP3", variable=self.audio_format, value="mp3", font=rb_font).pack(side="left", padx=10)
        RadioButton(fmt_frame, text="WAV", variable=self.audio_format, value="wav", font=rb_font).pack(side="left", padx=10)
        RadioButton(fmt_frame, text="OGG", variable=self.audio_format, value="ogg", font=rb_font).pack(side="left", padx=10)
        
        # Progress bar (hidden initially)
        self.extract_progress = ctk.CTkProgressBar(frame, width=300)
        self.extract_progress.pack(pady=10)
        self.extract_progress.pack_forget()
        self.extract_progress.set(0)
        
        ctk.CTkButton(
            frame, 
            text="💿 Extraer Audio", 
            command=self._extract_audio, 
            height=40
        ).pack(pady=10)
    
    def _extract_audio(self) -> None:
        if not self._check_files():
            return
        
        # Show progress
        self.extract_progress.pack()
        self.extract_progress.set(0.1)
        self.status_label.configure(text="Extrayendo audio...", text_color="#FFD700")
        self.update()
        
        # Run in thread
        def extract_thread():
            try:
                from tools.video_tool.processor import extract_audio
                
                selected = self._get_selected_files()
                total = len(selected)
                success_count = 0
                errors = []
                
                for i, video_file in enumerate(selected):
                    # Update progress
                    progress = (i + 1) / total
                    self.after(0, lambda p=progress: self.extract_progress.set(p))
                    
                    result = extract_audio(video_file, self.audio_format.get())
                    if result['success']:
                        success_count += 1
                    else:
                        errors.append(Path(video_file).name)
                
                # Final result
                if success_count == total:
                    final_result = {'success': True, 'message': f'✓ Audio extraído de {total} videos'}
                elif success_count > 0:
                    final_result = {'success': True, 'message': f'✓ {success_count}/{total} OK, {len(errors)} errores'}
                else:
                    final_result = {'success': False, 'error': f'Errores: {", ".join(errors[:3])}'}
                
                self.after(0, lambda: self._on_extract_done(final_result))
            except Exception as e:
                self.after(0, lambda: self._on_extract_done({'success': False, 'error': str(e)}))
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    def _on_extract_done(self, result: dict) -> None:
        self.extract_progress.set(1)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
        
        self.after(3000, lambda: self._hide_progress_bar(self.extract_progress))
    
    def _setup_convert_tab(self) -> None:
        frame = self.tab_convert
        
        ctk.CTkLabel(
            frame, 
            text="Convertir video a otro formato:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        fmt_frame = ctk.CTkFrame(frame)
        fmt_frame.pack(pady=5)
        
        ctk.CTkLabel(fmt_frame, text="Formato salida:").pack(side="left", padx=5)
        self.out_format = ctk.StringVar(value="mp4")
        
        rb_font = ("Segoe UI", 12)
        for fmt in ["mp4", "avi", "mkv", "mov"]:
            RadioButton(fmt_frame, text=fmt, variable=self.out_format, value=fmt, font=rb_font).pack(side="left", padx=5)
        
        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(pady=5)
        
        ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
        self.crf_var = ctk.StringVar(value="23")
        
        RadioButton(quality_frame, text="Alta (18)", variable=self.crf_var, value="18", font=rb_font).pack(side="left", padx=5)
        RadioButton(quality_frame, text="Media (23)", variable=self.crf_var, value="23", font=rb_font).pack(side="left", padx=5)
        RadioButton(quality_frame, text="Baja (28)", variable=self.crf_var, value="28", font=rb_font).pack(side="left", padx=5)
        
        # Progress bar (hidden initially)
        self.convert_progress = ctk.CTkProgressBar(frame, width=300)
        self.convert_progress.pack(pady=10)
        self.convert_progress.pack_forget()
        self.convert_progress.set(0)
        
        ctk.CTkButton(
            frame, 
            text="🔄 Convertir", 
            command=self._convert_video, 
            height=40
        ).pack(pady=10)
    
    def _convert_video(self) -> None:
        if not self._check_files():
            return
        
        # Disable button and show progress
        self.convert_progress.pack()
        self.convert_progress.set(0.1)
        selected = self._get_selected_files()
        self.status_label.configure(text=f"Convirtiendo 0/{len(selected)}...", text_color="#FFD700")
        self.update()
        
        # Run conversion in thread
        def convert_thread():
            try:
                from tools.video_tool.processor import convert_video
                
                total = len(selected)
                success_count = 0
                errors = []
                skipped_files = []
                
                for i, video_file in enumerate(selected):
                    # Update progress
                    progress = (i + 1) / total
                    self.after(0, lambda p=progress, c=i+1: self._update_convert_progress(p, c, total))
                    
                    # Pass as list, not single string
                    result = convert_video([video_file], self.out_format.get(), crf=int(self.crf_var.get()))
                    if result.get('skipped'):
                        skipped_files.extend(result['skipped'])
                    elif result['success']:
                        success_count += 1
                    else:
                        errors.append(Path(video_file).name)
                
                # Final result
                if skipped_files and success_count == 0:
                    final_result = {'success': True, 'message': f'✓ {len(skipped_files)} Videos ya estaban en formato'}
                elif skipped_files and success_count > 0:
                    final_result = {'success': True, 'message': f'✓ {success_count} convertidos, {len(skipped_files)} omitidos'}
                elif success_count == total:
                    final_result = {'success': True, 'message': f'✓ {total} videos convertidos'}
                elif success_count > 0:
                    final_result = {'success': True, 'message': f'✓ {success_count}/{total} OK'}
                else:
                    final_result = {'success': False, 'error': f'Errores: {", ".join(errors[:3])}'}
                
                self.after(0, lambda: self._on_convert_done(final_result))
            except Exception as e:
                self.after(0, lambda: self._on_convert_done({'success': False, 'error': str(e)}))
        
        threading.Thread(target=convert_thread, daemon=True).start()
    
    def _update_convert_progress(self, progress: float, current: int, total: int) -> None:
        self.convert_progress.set(progress)
        self.status_label.configure(text=f"Convirtiendo {current}/{total}...", text_color="#FFD700")
    
    def _on_convert_done(self, result: dict) -> None:
        self.convert_progress.set(1)
        
        if result['success']:
            self.status_label.configure(text=result['message'], text_color="green")
        else:
            self.status_label.configure(text=result.get('error', 'Error'), text_color="red")
        
        # Reset and hide progress after delay
        self.after(3000, lambda: self._hide_progress_bar(self.convert_progress))
    
    def _setup_info_tab(self) -> None:
        frame = self.tab_info
        
        ctk.CTkLabel(
            frame, 
            text="Información del video:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        ctk.CTkButton(
            frame, 
            text="👁️ Ver Info", 
            command=self._show_info
        ).pack(pady=10)
        
        self.info_text = ctk.CTkTextbox(frame, width=500, height=300, wrap="word")
        self.info_text.pack(padx=10, pady=10)
        self.info_text.configure(state="disabled")
    
    def _show_info(self) -> None:
        if not self._check_files():
            self.status_label.configure(text="Seleccioná un video primero", text_color="#FFA500")
            return
        
        from tools.video_tool.processor import get_video_info
        
        self.status_label.configure(text="Cargando info...", text_color="#FFD700")
        self.update()
        
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná un video", text_color="#FFA500")
            return
        
        # Enable textbox to write
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        
        all_info = []
        errors = []
        
        for video_path in selected:
            result = get_video_info(video_path)
            
            if result['success']:
                # Format FPS cleaner
                fps = result['video_fps']
                if '/' in str(fps):
                    try:
                        num, den = fps.split('/')
                        fps = f"{float(num)/float(den):.2f}"
                    except (ValueError, ZeroDivisionError):
                        pass
                
                # Show only first format
                fmt = result['format'] or 'N/A'
                if ',' in fmt:
                    fmt = fmt.split(',')[0]
                
                # Shorten resolution
                res = result['video_resolution'] or 'N/A'
                
                info = f"""📹 {result['file_name']}
{'─'*35}
  📦 Formato:     {fmt}
  💾 Tamaño:      {result['file_size'] / 1024 / 1024:.2f} MB
  ⏱️ Duración:    {result['duration']:.1f}s
  🎬 Video:       {result['video_codec'] or 'N/A'} | {res}
  ⚡ Bitrate:     {result.get('video_bitrate', 'N/A')}
  🎞️ FPS:        {fps}
  🔊 Audio:       {result['audio_codec'] or 'N/A'}"""
                all_info.append(info)
            else:
                errors.append(f"{Path(video_path).name}: {result.get('error', 'Error')}")
        
        # Display results
        if all_info:
            self.info_text.insert("1.0", "\n\n".join(all_info))
        
        if errors:
            if all_info:
                self.info_text.insert(tk.END, f"\n\n⚠️ ERRORES:\n" + "\n".join(errors))
            else:
                self.info_text.insert("1.0", "⚠️ ERRORES:\n" + "\n".join(errors))
        
        # Update status bar
        if errors and not all_info:
            self.status_label.configure(text="Error al cargar info", text_color="red")
        else:
            self._update_selection_status()
        
        # Disable textbox again
        self.info_text.configure(state="disabled")