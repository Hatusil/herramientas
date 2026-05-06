"""UI: Interfaz de usuario para la herramienta de audio."""
import os
import logging
from core.help_panel import add_help
from ui.radiobutton import RadioButton
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Callable, Dict, Any

# Import BaseToolUI from core
from core.base_tool_ui import BaseToolUI


logger = logging.getLogger(__name__)


class AudioToolUI(BaseToolUI):
    """UI para procesamiento de archivos de audio."""
    
    def __init__(self, master, on_process: Callable, **kwargs):
        # Call BaseToolUI __init__ which calls _setup_ui()
        super().__init__(master, on_process, **kwargs)
        
        # Build tool-specific tabs after base selector
        self._build_tabs()
    
    def _build_tabs(self) -> None:
        """Build tool-specific tabs."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_normalize = self.tabview.add("Normalizar")
        self.tab_clean = self.tabview.add("Limpiar")
        self.tab_edit_meta = self.tabview.add("Editar Metadatos")
        self.tab_convert = self.tabview.add("Convertir")
        self.tab_repair = self.tabview.add("Reparar")
        self.tab_info = self.tabview.add("Info")
        self.tab_verify = self.tabview.add("Verificar")
        
        self._setup_normalize_tab()
        self._setup_clean_tab()
        self._setup_edit_meta_tab()
        self._setup_convert_tab()
        self._setup_repair_tab()
        self._setup_info_tab()
        self._setup_verify_tab()
    
    def _get_file_label(self) -> str:
        """Override: Label for file section."""
        return "Archivos de audio:"
    
    def _get_file_dialog_filters(self) -> List[tuple]:
        """Override: Filters for file dialog."""
        return [
            ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
            ("MP3", "*.mp3"),
            ("Todos", "*.*")
        ]
    
    def _setup_ui(self) -> None:
        """Configura los widgets de la UI."""
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="Procesamiento de Audio",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Panel de ayuda
        help_panel = add_help(
            self,
            description="🎵 Procesa audio MP3/WAV/FLAC/OGG/M4A: normaliza volumen, limpia metadatos ID3, convierte formato, repara archivos, muestra info",
            usage=[
                "1. 📥 Agregar archivos (+)",
                "2. ☑️ Seleccionar con Ctrl+click o botones 'Todos'/'Ninguno'",
                "3. 📑 Elegir operación (Normalizar/Limpiar/Convertir/Reparar/Info)",
                "4. ⚙️ Configurar opciones LUFS o calidad (192k default)",
                "5. ▶️ Click en ejecutar (procesa solo los seleccionados)"
            ],
            warnings=[
                "⚠️ mp3→mp3 con calidad 192k se omite (ya en formato)",
                "⚠️ Cambiar calidad para forzar conversión",
                "⚠️ Normalización alta puede afectar calidad",
                "⚠️ Conversión siempre crea nuevo archivo",
                "⚠️ Reparar archivos severos puede dejar artefactos"
            ]
        )
        help_panel.pack(fill="x", padx=10, pady=5)
        
        # File selector (from BaseToolUI)
        self._setup_file_selector()
        
        # Status label (from BaseToolUI sets self.status_label)
    
    # =========================================================================
    # TAB: NORMALIZAR
    # =========================================================================
    def _setup_normalize_tab(self) -> None:
        frame = self.tab_normalize
        
        info = ctk.CTkLabel(
            frame,
            text="Normalizar volumen del audio",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        # Target LUFS
        lufs_frame = ctk.CTkFrame(frame)
        lufs_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lufs_frame, text="Target LUFS:").pack(side="left", padx=5)
        self.lufs_var = ctk.StringVar(value="-16")
        
        rb_font = ctk.CTkFont(size=14)
        for val, label in [("-20", "Muy bajo (-20)"), ("-16", "Estándar (-16)"), 
                          ("-14", "Alto (-14)"), ("-12", "Muy alto (-12)")]:
            RadioButton(
                lufs_frame,
                text=label,
                variable=self.lufs_var,
                value=val,
                font=rb_font
            ).pack(side="left", padx=5)
        
        # Opciones adicionales
        opts_frame = ctk.CTkFrame(frame)
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        self.limit_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame,
            text="Aplicar limitador (evita clipping)",
            variable=self.limit_var
        ).pack(anchor="w", padx=20)
        
        # Calidad
        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(quality_frame, text="Calidad MP3:").pack(side="left", padx=5)
        self.quality_var = ctk.StringVar(value="192")
        
        for val in ["128", "192", "256", "320"]:
            RadioButton(
                quality_frame,
                text=f"{val} kbps",
                variable=self.quality_var,
                value=val
            ).pack(side="left", padx=5)
        
        # Remuestreo
        sample_frame = ctk.CTkFrame(frame)
        sample_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sample_frame, text="Remuestreo:").pack(side="left", padx=5)
        self.sample_var = ctk.StringVar(value="0")
        
        RadioButton(
            sample_frame,
            text="Mantener original",
            variable=self.sample_var,
            value="0"
        ).pack(side="left", padx=5)
        
        for val in ["44100", "48000"]:
            RadioButton(
                sample_frame,
                text=f"{val} Hz",
                variable=self.sample_var,
                value=val
            ).pack(side="left", padx=5)
        
        # Botón
        ctk.CTkButton(
            frame,
            text="🎚️ Normalizar Volumen",
            command=self._normalize,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def _normalize(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        options = {
            'target_lufs': int(self.lufs_var.get()),
            'limit_clipping': self.limit_var.get(),
            'quality': int(self.quality_var.get()),
        }
        
        sample = self.sample_var.get()
        if sample != "0":
            options['sample_rate'] = int(sample)
        
        result = self.on_process('normalize', self.files, options)
        self._show_result(result)
    
    # =========================================================================
    # TAB: LIMPIAR
    # =========================================================================
    def _setup_clean_tab(self) -> None:
        frame = self.tab_clean
        
        info = ctk.CTkLabel(
            frame,
            text="Limpiar metadatos (ID3, título, artista, etc.)",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        info2 = ctk.CTkLabel(
            frame,
            text="Esto eliminará: título, artista, álbum, género, año, etc.",
            text_color="gray"
        )
        info2.pack(pady=5)
        
        ctk.CTkButton(
            frame,
            text="🧹 Limpiar Metadatos",
            command=self._clean_metadata,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def _clean_metadata(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('clean', self.files, {})
        self._show_result(result)
    
    # =========================================================================
    # TAB: EDITAR METADATOS
    # =========================================================================
    def _setup_edit_meta_tab(self) -> None:
        frame = self.tab_edit_meta
        
        info = ctk.CTkLabel(
            frame,
            text="Editar metadatos (título, artista, álbum, género...)",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        container = ctk.CTkFrame(frame)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("title", "Título:"),
            ("artist", "Artista:"),
            ("album", "Álbum:"),
            ("genre", "Género:"),
            ("year", "Año:"),
            ("track", "Pista:"),
            ("comment", "Comentario:"),
            ("composer", "Compositor:")
        ]
        
        self.meta_vars = {}
        
        for i, (key, label) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            ctk.CTkLabel(container, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            
            var = ctk.StringVar()
            self.meta_vars[key] = var
            
            ctk.CTkEntry(container, textvariable=var, width=180).grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
        
        ctk.CTkButton(
            container,
            text="✏️ Editar Metadatos",
            command=self._edit_metadata,
            height=40,
            font=ctk.CTkFont(size=14)
        ).grid(row=4, column=0, columnspan=4, pady=20)
    
    def _edit_metadata(self) -> None:
        if not self._check_files():
            return
        
        options = {k: v.get() for k, v in self.meta_vars.items() if v.get().strip()}
        
        if not options:
            self.status_label.configure(text="Ingresa al menos un campo", text_color="#FFA500")
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('edit_metadata', self.files, options)
        self._show_result(result)
    
    # =========================================================================
    # TAB: CONVERTIR
    # =========================================================================
    def _setup_convert_tab(self) -> None:
        frame = self.tab_convert
        
        info = ctk.CTkLabel(
            frame,
            text="Convertir a otro formato de audio",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        # Formato de salida
        format_frame = ctk.CTkFrame(frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(format_frame, text="Formato de salida:").pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="mp3")
        
        for fmt in ["mp3", "wav", "flac", "ogg"]:
            RadioButton(
                format_frame,
                text=fmt.upper(),
                variable=self.format_var,
                value=fmt
            ).pack(side="left", padx=10)
        
        # Calidad
        quality_frame = ctk.CTkFrame(frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(quality_frame, text="Calidad:").pack(side="left", padx=5)
        self.conv_quality_var = ctk.StringVar(value="192")
        
        for val in ["128", "192", "256", "320"]:
            RadioButton(
                quality_frame,
                text=f"{val} kbps",
                variable=self.conv_quality_var,
                value=val
            ).pack(side="left", padx=5)
        
        info2 = ctk.CTkLabel(
            frame,
            text="Nota: WAV y FLAC usan calidad sin pérdida",
            text_color="gray",
            font=ctk.CTkFont(size=14)
        )
        info2.pack(pady=5)
        
        ctk.CTkButton(
            frame,
            text="🔄 Convertir Formato",
            command=self._convert,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def _convert(self) -> None:
        if not self._check_files():
            return
        
        self.status_label.configure(text="Procesando...", text_color="blue")
        
        result = self.on_process('convert', self.files, {
            'format': self.format_var.get(),
            'quality': int(self.conv_quality_var.get())
        })
        
        self._show_result(result)
    
    # =========================================================================
    # TAB: REPARAR
    # =========================================================================
    def _setup_repair_tab(self) -> None:
        frame = self.tab_repair
        
        info = ctk.CTkLabel(
            frame,
            text="Reparar archivos de audio corruptos",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        info2 = ctk.CTkLabel(
            frame,
            text="Primero verificá qué archivos están corruptos, luego decidí qué reparar",
            text_color="gray"
        )
        info2.pack(pady=5)
        
        # Textbox para resultados de verificación
        self.repair_verify_text = ctk.CTkTextbox(frame, width=500, height=180, wrap="word")
        self.repair_verify_text.pack(padx=10, pady=10)
        self.repair_verify_text.configure(state="disabled")
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔍 Verificar",
            command=self._verify_before_repair,
            height=35,
            width=120
        ).pack(side="left", padx=3)
        
        self.btn_repair_corrupt = ctk.CTkButton(
            btn_frame,
            text="🔧 Solo Corruptos",
            command=lambda: self._do_repair(mode='corrupt'),
            height=35,
            width=130,
            state="disabled"
        )
        self.btn_repair_corrupt.pack(side="left", padx=3)
        
        self.btn_repair_all = ctk.CTkButton(
            btn_frame,
            text="🔧 Reparar Todos",
            command=lambda: self._do_repair(mode='all'),
            height=35,
            width=130,
            state="disabled"
        )
        self.btn_repair_all.pack(side="left", padx=3)
        
        # Estado de verificación
        self.verify_state = {'ok': [], 'corrupt': []}
    
    def _verify_before_repair(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="#FFA500")
            return
        
        self.status_label.configure(text="Verificando...", text_color="#FFD700")
        self.repair_verify_text.configure(state="normal")
        self.repair_verify_text.delete("1.0", tk.END)
        self.update()
        
        try:
            from tools.audio_tool.processor import verify_multiple_audio
            result = verify_multiple_audio(selected)
            
            # Clasificar
            ok_files = [r for r in result['results'] if not r['corrupt']]
            corrupt_files = [r for r in result['results'] if r['corrupt']]
            
            # Guardar estado
            self.verify_state = {'ok': [r['file'] for r in ok_files], 'corrupt': [r['file'] for r in corrupt_files]}
            
            # Mostrar resultados
            self.repair_verify_text.insert("1.0", f"📊 VERIFICACIÓN:\n{'─'*35}\n")
            
            if ok_files:
                self.repair_verify_text.insert(tk.END, f"✅ OK ({len(ok_files)}):\n")
                for r in ok_files:
                    self.repair_verify_text.insert(tk.END, f"  ✓ {r['name']}\n")
                self.repair_verify_text.insert(tk.END, "\n")
            
            if corrupt_files:
                self.repair_verify_text.insert(tk.END, f"❌ CORRUPTOS ({len(corrupt_files)}):\n")
                for r in corrupt_files:
                    self.repair_verify_text.insert(tk.END, f"  ✗ {r['name']}\n")
            
            self.repair_verify_text.insert(tk.END, f"\n{'─'*35}\nTotal: {result['total']} | OK: {result['ok']} | corruptos: {result['corrupt']}")
            self.repair_verify_text.configure(state="disabled")
            
            # Habilitar botones
            if len(corrupt_files) > 0:
                self.btn_repair_corrupt.configure(state="normal")
                self.status_label.configure(text=f"{len(corrupt_files)} corruptos", text_color="#FFA500")
            else:
                self.btn_repair_corrupt.configure(state="disabled")
                self.status_label.configure(text="Todos OK", text_color="green")
            
            self.btn_repair_all.configure(state="normal" if len(ok_files) > 0 else "disabled")
                
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
    
    def _do_repair(self, mode: str) -> None:
        if mode == 'corrupt':
            files = self.verify_state['corrupt']
            if not files:
                return
            self.status_label.configure(text=f"Reparando {len(files)} corruptos...", text_color="#FFD700")
        else:
            files = self._get_selected_files()
            self.status_label.configure(text=f"Reparando {len(files)} archivos...", text_color="#FFD700")
        
        result = self.on_process('repair', files, {})
        self._show_result(result)
    
    # =========================================================================
    # TAB: VERIFICAR
    # =========================================================================
    def _setup_verify_tab(self) -> None:
        frame = self.tab_verify
        
        info = ctk.CTkLabel(
            frame,
            text="Verificar integridad de archivos de audio",
            font=ctk.CTkFont(weight="bold")
        )
        info.pack(pady=10)
        
        info2 = ctk.CTkLabel(
            frame,
            text="Verifica qué archivos están corruptos antes de repararlos",
            text_color="gray"
        )
        info2.pack(pady=5)
        
        # Textbox para resultados
        self.verify_text = ctk.CTkTextbox(frame, width=500, height=280, wrap="word")
        self.verify_text.pack(padx=10, pady=10)
        self.verify_text.configure(state="disabled")
        
        ctk.CTkButton(
            frame,
            text="🔍 Verificar Archivos",
            command=self._verify_audio,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
    
    def _verify_audio(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="#FFA500")
            return
        
        self.status_label.configure(text="Verificando archivos...", text_color="#FFD700")
        self.update()
        
        try:
            from tools.audio_tool.processor import verify_multiple_audio
            result = verify_multiple_audio(selected)
            
            # Enable textbox to write
            self.verify_text.configure(state="normal")
            self.verify_text.delete("1.0", tk.END)
            
            # Mostrar resultados
            ok_files = [r for r in result['results'] if not r['corrupt']]
            corrupt_files = [r for r in result['results'] if r['corrupt']]
            
            if ok_files:
                self.verify_text.insert("1.0", f"✅ ARCHIVOS OK ({len(ok_files)}):\n")
                for r in ok_files:
                    self.verify_text.insert(tk.END, f"  ✓ {r['name']}\n")
            
            if corrupt_files:
                if ok_files:
                    self.verify_text.insert(tk.END, f"\n")
                self.verify_text.insert(tk.END, f"❌ ARCHIVOS CORRUPTOS ({len(corrupt_files)}):\n")
                for r in corrupt_files:
                    self.verify_text.insert(tk.END, f"  ✗ {r['name']} - {r['message']}\n")
            
            # Resumen
            self.verify_text.insert(tk.END, f"\n{'─'*35}\n")
            self.verify_text.insert(tk.END, f"Total: {result['total']} | OK: {result['ok']} | Corruptos: {result['corrupt']}")
            
            self.verify_text.configure(state="disabled")
            
            # Status
            if result['corrupt'] == 0:
                self.status_label.configure(text=f"Todos OK ({result['ok']} archivos)", text_color="green")
            else:
                self.status_label.configure(text=f"{result['ok']} OK, {result['corrupt']} corruptos", text_color="#FFA500")
                
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
    
    # =========================================================================
    # TAB: INFO
    # =========================================================================
    def _setup_info_tab(self) -> None:
        frame = self.tab_info
        
        ctk.CTkLabel(
            frame,
            text="Información del archivo de audio:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        self.info_text = ctk.CTkTextbox(frame, width=500, height=300, wrap="word")
        self.info_text.pack(padx=10, pady=10)
        self.info_text.configure(state="disabled")
        
        ctk.CTkButton(
            frame,
            text="👁️ Ver Información",
            command=self._show_info
        ).pack(pady=5)
    
    def _show_info(self) -> None:
        selected = self._get_selected_files()
        if not selected:
            self.status_label.configure(text="Seleccioná al menos un archivo", text_color="#FFA500")
            return
        
        # Enable textbox to write
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        
        all_info = []
        errors = []
        
        for file_path in selected:
            try:
                from tools.audio_tool.processor import get_audio_info
                info = get_audio_info(file_path)
                
                if info.get('success'):
                    audio_info = f"""📄 {info.get('file_name', 'N/A')}
{'─'*35}
  💾 Tamaño:      {info.get('file_size', 0) / 1024 / 1024:.2f} MB
  ⏱️ Duración:    {info.get('duration', 0):.1f} seg
  📦 Formato:    {info.get('format', 'N/A')}
  🔊 Codec:      {info.get('codec', 'N/A')}
  🎵 Muestreo:   {info.get('sample_rate', 0)} Hz
  🔀 Canales:    {info.get('channels', 0)}
  📊 Bitrate:    {info.get('bit_rate', 0) / 1000:.0f} kbps
  📝 Título:     {info.get('title', 'N/A')}
  👤 Artista:    {info.get('artist', 'N/A')}
  📀 Álbum:      {info.get('album', 'N/A')}
  #️⃣ Pista:      {info.get('track', 'N/A')}
  📅 Año:        {info.get('year', 'N/A')}
  🎼 Género:     {info.get('genre', 'N/A')}"""
                    all_info.append(audio_info)
                else:
                    errors.append(f"{Path(file_path).name}: {info.get('error', 'Error')}")
            except Exception as e:
                errors.append(f"{Path(file_path).name}: {str(e)}")
        
        # Display results
        if all_info:
            self.info_text.insert("1.0", "\n\n".join(all_info))
        
        if errors:
            if all_info:
                self.info_text.insert(tk.END, f"\n\n⚠️ ERRORES:\n" + "\n".join(errors))
            else:
                self.info_text.insert("1.0", "⚠️ ERRORES:\n" + "\n".join(errors))
        
        # Disable textbox again
        self.info_text.configure(state="disabled")
        
        # Update status
        status = f"Mostrando {len(all_info)}/{len(selected)} archivos"
        self.status_label.configure(text=status, text_color="green" if not errors else "#FFA500")
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    def _show_result(self, result: Dict[str, Any]) -> None:
        """Muestra el resultado del procesamiento."""
        if result.get('success'):
            self.status_label.configure(
                text=result.get('message', 'Completado'),
                text_color="green"
            )
        else:
            self.status_label.configure(
                text=result.get('message', 'Error'),
                text_color="red"
            )