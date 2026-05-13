# Ingeniería del Proyecto

## 1. Visión General

**Herramientas** es una aplicación de escritorio multiplataforma (Windows/Linux) construida con Python y CustomTkinter. Su propósito es proporcionar un conjunto de herramientas de productividad para el usuario final: procesamiento de audio, video, imágenes, PDFs, texto, compression, hash, etc.

### Stack Tecnológico
- **Frontend**: CustomTkinter (Tkinter con look moderno)
- **Backend**: Python 3.11+
- **Async**: ThreadPoolExecutor (core/async_utils.py)
- **Plugins**: Descubrimiento automático via plugin_manager
- **Externos**: ffmpeg (audio/video), pdftotext, etc.

---

## 2. Arquitectura Global

### Capas del Sistema

```
┌─────────────────────────────────────┐
│           App (ui/app.py)           │  ← Main window, sidebar, tool switching
├─────────────────────────────────────┤
│        BaseToolUI (core/)           │  ← UI base: file selector, tabs, progress
├─────────────────────────────────────┤
│         BaseTool (core/)            │  ← Interface mínima para tools
├─────────────────────────────────────┤
│      Processor (tools/XYZ/)         │  ← Lógica de negocio específica
└─────────────────────────────────────┘
```

### Flujo de Datos

```
Usuario → Botón UI → process_async() → on_process callback
                                         ↓
                              processor.*_async() → callback
                                         ↓
                              _finish_processing() → UI update
```

---

## 3. Componentes Core

### 3.1 BaseTool (core/base_tool.py)

**Propósito**: Interfaz mínima que toda herramienta debe implementar.

```python
class BaseTool(ABC):
    @abstractmethod
    def get_name(self) -> str          # "Audio", "PDF", etc.
    
    @abstractmethod
    def get_icon(self) -> str          # Emoji o nombre lucide
    
    @abstractmethod
    def get_description(self) -> str   # Descripción breve
    
    @abstractmethod
    def build_ui(self, parent_frame)   # Construye la UI
    
    @abstractmethod
    def process(files, options)        # Procesamiento sync
```

**Responsabilidad del padre**: Define el contrato. No tiene lógica de negocio.

---

### 3.2 BaseToolUI (core/base_tool_ui.py)

**Propósito**: UI base compartida por todas las herramientas con selector de archivos.

#### Estado que maneja el padre:
- `self.files` - Lista de archivos seleccionados
- `self.file_listbox` - Widget de lista de archivos
- `self.status_label` - Label de estado (resultados, errores)
- `self.progress_bar` - Barra de progreso
- `self.is_processing` - Flag de procesamiento activo

#### Métodos del padre (no tocar en hijos):
- `_check_files()` - Valida que haya archivos seleccionados
- `_get_selected_files()` - Retorna archivos marcados en listbox
- `process_async(action, files, options)` - Ejecuta en background
- `_finish_processing(result)` - Maneja resultado en thread principal
- `_show_result(result)` - Muestra mensaje en status_label
- `start_progress()` / `stop_progress()` - Controla progress bar

#### Hooks overrideables en hijos:
```python
def _get_file_dialog_filters()  # Filtros para diálogo de archivos
def _get_file_label()            # Texto de la etiqueta "Archivos:"
def _get_custom_buttons()        # Botones adicionales en barra
def _setup_ui()                  # Setup completo de UI (override total)
```

**Responsabilidad del padre**: Manejo de archivos, estado, progress, callbacks.

---

### 3.3 Async Utils (core/async_utils.py)

```python
_executor = ThreadPoolExecutor(max_workers=4)

def run_in_background(func, callback=None) -> Future:
    """Ejecuta función en threadpool sin bloquear UI."""
```

**Responsabilidad del padre**: Threadpool compartido para todas las tools.

---

### 3.4 Tool Builder (core/tool_builder.py)

```python
def create_standard_tool_ui(parent, icon_and_name, description, 
                            tab_configs, help_config, file_types)
```

Crea automáticamente: selector de archivos, listbox, tabs, botones de ayuda.

**Responsabilidad del padre**: UI estándar reusable.

---

## 4. Identificación: Propiedad del Padre vs Hijos

| Componente | Padre | Hijo | Notas |
|------------|-------|------|-------|
| Selector de archivos | ✅ | - | Común a todos |
| Listbox de archivos | ✅ | - | Común a todos |
| Status label | ✅ | - | Común a todos |
| Progress bar | ✅ | - | Común a todos |
| is_processing flag | ✅ | - | **No setear en hijos** |
| process_async() | ✅ | - | **No reimplementar** |
| Tabs custom | - | ✅ | Cada tool define los suyos |
| Botones de acción | - | ✅ | Cada tool define sus operaciones |
| Processor logic | - | ✅ | Todo el negocio específico |
| file_types filters | - | ✅ | Override _get_file_dialog_filters() |

### Regla de Oro
> Los hijos **NO** deben setear `is_processing = True` manualmente. El padre lo maneja internamente en `process_async()`.

---

## 5. Tema y Modo Oscuro

### Implementación Actual
- **Tema**: `core/config.py` carga configuración de `config.json`
- **Modo**: `dark` / `light` configurable
- **CustomTkinter**: `ctk.set_appearance_mode(mode)`

### Componentes que respetan el tema:
- Todos los widgets CustomTkinter (CTkFrame, CTkButton, etc.)
- tool_builder usa `COLORS` de `core/constants.py`

### Responsabilidad del padre:
- Cargar y aplicar tema al iniciar app
- Proveer `COLORS` constante para uso en hijos
- **Los hijos deben usar widgets CTk** para respetar el tema

---

## 6. Maximas del Proyecto

Las siguientes máximas rigen el diseño y evolución del proyecto:

### Máxima A0 (Brevedad)
- Ninguna función > 30 líneas
- Ninguna clase > 300 líneas
- Una función = una responsabilidad

### Máxima A1 (Responsabilidad Única SRP)
- Un módulo debe tener una única razón para cambiar
- Alta cohesión interna, bajo acoplamiento externo

### Máxima A2 (Interfaces Explícitas)
- Toda comunicación entre módulos via contratos claros
- No acceder a estado interno de otros módulos

### Máxima A3 (Stateless Preferible)
- Si un módulo guarda estado, debe ser en almacén externo compartido
- Facilita testing y replicación

### Máxima A4 (Código Compartido en core/)
- Lo que se repite en múltiples tools → `core/`
- Ejemplo: `process_async`, `run_in_background`, `create_standard_tool_ui`

### Máxima A5 (Async para Operaciones Lentas)
- Tareas bloqueantes → background thread
- UI nunca se bloquea durante procesamiento

### Máxima A6 (Observabilidad)
- Cada tool debe loguear operaciones
-Usar `logging` standard, no `print`

### Máxima A7 (Idempotencia)
- Procesar mismos archivos varias veces → mismo resultado
- Skip logic para evitar trabajo redundante

### Máxima A8 (Compatibilidad Multiplataforma)
- `platform.system()` para detectar SO
- Rutas, ejecutables, fuentes adaptadas al entorno

### Máxima A12 (Métricas)
- Instrumentar tools con Counter, Timer
- Para observar operaciones lentas y trackear uso

---

## 7. Plugin System (Descubrimiento de Tools)

### Cómo funciona
1. `core/plugin_manager.py` escanea directorio `tools/`
2. Busca subclases de `BaseTool` en `__init__.py` de cada subdirectorio
3. Instancia y registra en el diccionario de tools

### Estructura esperada de una tool
```
tools/
  audio_tool/
    __init__.py    ← define AudioTool(BaseTool)
    processor.py   ← lógica de negocio
    ui.py          ← UI (旧, retrocompatibilidad)
    ui/
      main_ui.py   ← AudioToolUI(BaseToolUI)
      *_tab.py     ← tabs específicos
    processors/    ← módulos de procesamiento
      __init__.py
      normalize.py
      convert.py
      ...
```

### Checklist para nueva tool
- [ ] Crear `tools/nueva_tool/__init__.py` con clase `NuevaTool(BaseTool)`
- [ ] Implementar `get_name()`, `get_icon()`, `get_description()`, `build_ui()`, `process()`
- [ ] UI hereda `BaseToolUI` o usa `create_standard_tool_ui()`
- [ ] Usar `process_async()` del padre, no reimplementar
- [ ] No setear `is_processing` manualmente
- [ ] Agregar métricas si corresponde (A12)

---

## 8. Patrones Comunes

### Patrón: Botón de Acción
```python
# En un tab (hijos)
def mi_accion(ui: 'ToolUI') -> None:
    if not ui._check_files():
        return
    ui.status_label.configure(text="🔄 Procesando...", text_color="#FFD700")
    ui.process_async("mi_accion", ui.files, opciones)
```

### Patrón: Skip Logic
```python
# En processor (hijos)
def convert_audio(files, output_format, quality):
    for f in files:
        if get_format(f) == output_format:
            logger.info(f"Omite (mismo formato): {f}")
            continue  # Skip
        # ... procesar
```

### Patrón: Async con Callback
```python
# En processor (hijos)
def mi_funcion_async(files, callback=None, **options):
    def worker():
        result = mi_funcion_sync(files, **options)
        if callback:
            callback(result)
    run_in_background(worker, callback=callback)
```

---

## 9. Herramientas

### 9.1 Audio Tool

**Propósito**: Normalizar, convertir, limpiar y reparar archivos de audio.

**Icono**: 🎵 (music)

#### Arquitectura

```
tools/audio_tool/
├── __init__.py          → AudioTool(BaseTool)
├── processor.py         → Funciones sync + coordinación async
├── ui.py                → Re-export backward compatibility
├── ui/
│   ├── __init__.py
│   ├── main_ui.py       → AudioToolUI(BaseToolUI)
│   ├── normalize_tab.py
│   ├── clean_tab.py
│   ├── edit_meta_tab.py
│   ├── convert_tab.py
│   ├── repair_tab.py
│   ├── info_tab.py
│   └── verify_tab.py
└── processors/
    ├── __init__.py
    ├── normalize.py     → Normalización LUFS
    ├── convert.py       → Conversión de formato
    ├── metadata.py      → Limpieza/edición metadatos
    ├── repair.py        → Reparación de archivos
    └── audio_info.py    → Extracción de info
```

#### Herencia de BaseToolUI
- **Heredados**: files, file_listbox, status_label, progress_bar, is_processing
- **Override hooks**: No usa muchos, tabs definen su propia UI
- **Custom propio**: `tab_normalize`, `tab_clean`, `tab_edit_meta`, `tab_convert`, `tab_repair`, `tab_info`, `tab_verify`

#### Casos de Uso (Workflows)

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Normalizar | `normalize` | `processor.normalize_audio_async` | `_normalized.mp3` |
| Convertir | `convert` | `processor.convert_audio_async` | archivo en nuevo formato |
| Limpiar metadatos | `clean` | `processor.clean_audio_metadata_async` | `_cleaned.mp3 |
| Editar metadatos | `edit_metadata` | `processor.edit_audio_metadata_async` | `_edited.mp3` |
| Reparar | `repair` | `processor.repair_audio_async` | `_repaired.mp3` |
| Ver info | `show_info` | `get_audio_info` | display en UI |
| Verificar | `verify` | `verify_multiple_audio` | display en UI |

#### Puntos de Conexión Clave

```python
# AudioTool.__init__ → build_ui
self.ui = AudioToolUI(parent_frame, self._on_process)

# AudioTool._on_process → procesador sync
def _on_process(self, action, files, options):
    if action == 'normalize':
        return processor.normalize_audio(files, **options)
    elif action == 'convert':
        return processor.convert_audio(files, **options)
    ...

# AudioTool.process_async → processor async
def process_async(self, files, options, callback):
    action = options.get('action')
    if action == 'normalize':
        normalize_audio_async(files, callback=callback, **options)
```

#### Funciones Async Disponibles
```python
normalize_audio_async(files, callback=None, target_lufs=-16, limit_clipping=True, quality=192)
convert_audio_async(files, output_format='mp3', quality=192, callback=None)
clean_audio_metadata_async(files, callback=None)
edit_audio_metadata_async(files, callback=None, **metadata)
repair_audio_async(files, callback=None)
```

#### Skip Logic Implementada
- **convert**: Si formato origen == formato destino, omite
- **clean**: Si no hay metadatos para limpiar, omite
- **normalize**: Siempre procesa (no hay forma de saber LUFS actual)

#### Métricas (A12)
- ❌ No implementadas aún
- TODO: agregar Counter para cada operación, Timer para duración

#### Notas Técnicas
- Dependencias externas: `ffmpeg` (convert, normalize, repair), `mutagen` (metadata)
- Los processors usan `pydub` para audio processing
- Skip logic en convert: `if get_audio_format(f) == output_format: skip`

---

### 9.2 Video Tool

**Propósito**: Extraer audio y convertir videos entre formatos.

**Icono**: 🎬

#### Arquitectura

```
tools/video_tool/
├── __init__.py          → VideoTool(BaseTool)
├── processor.py         → extract_audio_async, convert_video_async
├── ui.py                → VideoToolUI
└── tests/
    └── test_processor.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Extraer audio | `extract_audio` | `processor.extract_audio_async` | `.mp3/.ogg/.wav` |
| Convertir video | `convert` | `processor.convert_video_async` | `.mp4/.avi/.mkv` |
| Ver info | `info` | `get_video_info` | display en UI |

#### Skip Logic
- **convert**: Si formato origen == formato destino y CRF=23, omite
- **extract**: Siempre procesa

#### Métricas (A12)
- ✅ Implementadas: `video_tool.audio_extracted`, `video_tool.video_converted`, `video_tool.errors`

#### Notas Técnicas
- Dependencias: `ffmpeg`, `ffprobe`
- Validación: extensión (.mp4/.avi/.mkv/.mov), tamaño máx 2GB
- Timeout: 300s extracción, 600s conversión

---

### 9.3 Image Tool

**Propósito**: Procesamiento Digital de Imágenes — 7 fases (adquisición, análisis, bordes, morfología, filtros, mejora, geometría).

**Icono**: 🖼️

#### Arquitectura

```
tools/image_tool/
├── __init__.py          → ImageTool(BaseTool)
├── processor.py         → Coordinación de processors
├── ui.py                → Re-export backward compatibility
├── ui/
│   ├── main_ui.py      → ImageToolUI(BaseToolUI)
│   ├── adquisicion_tab.py
│   ├── analisis_tab.py
│   ├── bordes_tab.py
│   ├── morfologia_tab.py
│   ├── filtros_tab.py
│   ├── mejora_tab.py
│   └── geometria_tab.py
└── processors/
    ├── __init__.py
    ├── adquisicion.py
    ├── analisis.py
    ├── bordes.py
    ├── morfologia.py
    ├── filtros.py
    ├── mejora.py
    ├── geometria.py
    └── _ok.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Adquisición | `adquisicion` | `processors.adquisicion` | imagen procesada |
| Análisis | `analisis` | `processors.analisis` | display en UI |
| Detección bordes | `bordes` | `processors.bordes` | imagen procesada |
| Morfología | `morfologia` | `processors.morfologia` | imagen procesada |
| Filtros | `filtros` | `processors.filtros` | imagen procesada |
| Mejora | `mejora` | `processors.mejora` | imagen procesada |
| Geometría | `geometria` | `processors.geometria` | imagen procesada |

#### Skip Logic
- No implementada actualmente

#### Métricas (A12)
- ❌ No implementadas aún

#### Notas Técnicas
- Dependencias: `Pillow` (PIL), `numpy`, `opencv` (opcional)
- 7 fases de PDI organizadas en tabs

---

### 9.4 PDF Tool

**Propósito**: Watermark, editar, combinar, encriptar, optimizar PDFs.

**Icono**: 📄

#### Arquitectura

```
tools/pdf_tool/
├── __init__.py          → PDFTool(BaseTool), maneja _on_process
├── processor.py         → Funciones de procesamiento
├── ui.py                → Re-export
├── ui/
│   ├── main_ui.py      → PDFToolUI(BaseToolUI)
│   ├── watermark_tab.py
│   ├── edit_tab.py
│   ├── combine_tab.py
│   ├── transform_tab.py
│   ├── security_tab.py
│   ├── optimize_tab.py
│   ├── pipeline_tab.py
│   ├── info_tab.py
│   └── numbers_tab.py
├── modules/
│   ├── __init__.py
│   ├── watermarks.py   → Watermark (add/remove)
│   ├── transform.py    → Rotate, reorder, extract
│   ├── security.py     → Encrypt, decrypt
│   ├── conversion.py   → Formatos
│   ├── pipeline.py    → Workflows
│   ├── info.py         → Metadata
│   └── watermark_removal.py → WM detection/removal
└── tests/
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Watermark texto | `text_watermark` | `processor.add_text_watermark` | PDF modificado |
| Watermark imagen | `image_watermark` | `processor.add_image_watermark` | PDF modificado |
| Quitar watermark | `remove_watermark` | `processor.remove_watermarks` | PDF limpio |
| Añadir anotación | `add_annotation` | `processor.add_text_annotation` | PDF modificado |
| Redactar área | `redact` | `processor.redact_area` | PDF modificado |
| Rotar páginas | `rotate` | `processor.rotate_pages` | PDF modificado |
| Reordenar | `reorder` | `processor.reorder_pages` | PDF modificado |
| Combinar | `merge` | `processor.merge_pdfs` | PDF nuevo |
| Extraer páginas | `extract` | `processor.extract_pages` | PDF nuevo |
| Encriptar | `encrypt` | `processor.encrypt_pdf` | PDF protegido |
| Desencriptar | `decrypt` | `processor.decrypt_pdf` | PDF desprotegido |
| Comprimir | `compress` | `processor.compress_pdf` | PDF optimizado |
| Limpiar metadata | `clean_metadata` | `processor.clean_metadata` | PDF limpio |
| Numerar páginas | `page_numbers` | `processor.add_page_numbers` | PDF numerado |

#### Skip Logic
- Varias operaciones verifican precondiciones antes de procesar

#### Métricas (A12)
- ❌ No implementadas aún

#### Notas Técnicas
- Dependencias: `pypdf`, `pikepdf`, `pdfplumber`, `reportlab` (watermarks)
- Módulos especializados para watermark removal avanzado

---

### 9.5 Text Analyzer Tool

**Propósito**: Análisis de texto: WordCloud, frecuencia, estadísticas, N-grams.

**Icono**: 📊

#### Arquitectura

```
tools/text_tool/
├── __init__.py         → TextAnalyzerTool(BaseTool)
├── processor.py        → Coordinación
├── ui.py               → Re-export
├── ui/
│   ├── main_ui.py     → TextAnalyzerUI(BaseToolUI)
│   ├── state.py       → Estado de análisis
│   ├── callbacks.py   → Callbacks de UI
│   ├── common.py      → Componentes comunes
│   ├── constants.py   → Constantes
│   ├── modal.py       → Modales
│   └── tabs/
│       ├── __init__.py
│       ├── base_tab.py
│       ├── input_tab.py
│       ├── clean_tab.py
│       ├── freq_tab.py
│       ├── stats_tab.py
│       ├── wc_tab.py      → WordCloud
│       ├── ngrams_tab.py → N-grams
│       ├── topics_tab.py → LDA topics
│       ├── kwic_tab.py   → KWIC
│       ├── mandala_tab.py
│       ├── wordtree_tab.py
│       ├── trends_tab.py
│       ├── scatter_tab.py
│       ├── corr_tab.py
│       ├── streamgraph_tab.py
│       └── bubblelines_tab.py
└── processors/
    ├── __init__.py
    ├── utils.py
    ├── extractors.py
    ├── frequency.py
    ├── wordcloud.py
    ├── topics.py
    ├── kwic.py
    ├── mandala.py
    ├── wordtree.py
    ├── trends.py
    ├── correlations.py
    ├── scatter.py
    ├── streamgraph.py
    ├── bubblelines.py
    └── category.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Input/Cargar | `load` | `extractors` | texto en memoria |
| Limpiar | `clean` | `utils.clean_text` | texto limpiado |
| Frecuencia | `frequency` | `processors.frequency` | display en UI |
| Estadísticas | `stats` | `extractors.get_stats` | display en UI |
| WordCloud | `wordcloud` | `processors.wordcloud` | imagen |
| N-grams | `ngrams` | `processors.frequency` | display en UI |
| Topics | `topics` | `processors.topics` | display en UI |
| KWIC | `kwic` | `processors.kwic` | display en UI |
| Mandala | `mandala` | `processors.mandala` | imagen |
| WordTree | `wordtree` | `processors.wordtree` | visualización |
| Trends | `trends` | `processors.trends` | visualización |
| Scatter | `scatter` | `processors.scatter` | visualización |

#### Skip Logic
- No implementada actualmente

#### Métricas (A12)
- ❌ No implementadas aún

#### Notas Técnicas
- Dependencias: `wordcloud`, `nltk`, `matplotlib`, `scipy` (opcional)
- Múltiples visualizaciones: wordcloud, mandala, wordtree, trends, scatter, streamgraph, bubblelines

---

### 9.6 Compress Tool

**Propósito**: Comprimir y extraer archivos ZIP, TAR.

**Icono**: 📦

#### Arquitectura

```
tools/compress_tool/
├── __init__.py         → CompressTool(BaseTool)
├── processor.py        → compress_to_zip, compress_to_tar, decompress
├── ui.py               → CompressToolUI
└── tests/
    └── test_processor.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Comprimir ZIP | `compress_zip` | `processor.compress_to_zip` | `.zip` |
| Comprimir TAR | `compress_tar` | `processor.compress_to_tar` | `.tar/.tar.gz` |
| Extraer ZIP | `decompress_zip` | `processor.decompress_zip` | carpeta |
| Extraer TAR | `decompress_tar` | `processor.decompress_tar` | carpeta |
| Ver contenido | `list` | `processor.list_zip_contents` | display en UI |

#### Skip Logic
- **compress_zip**: Si extensión == .zip, omite
- **compress_tar**: Si extensión es .tar/.tar.gz/.tgz/etc, omite

#### Métricas (A12)
- ✅ Implementadas: `compress_operations_total`, `compress_errors`

#### Notas Técnicas
- Dependencias: standard library (`zipfile`, `tarfile`)
- Nivel ZIP: 0-9 (default 6)
- Compression TAR: None, gz, bz2, xz

---

### 9.7 Hash Tool

**Propósito**: Calcular y verificar MD5, SHA1, SHA256.

**Icono**: #️⃣

#### Arquitectura

```
tools/hash_tool/
├── __init__.py         → HashTool(BaseTool)
├── processor.py        → calculate_hash, verify_hash
└── ui.py               → HashToolUI
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Calcular hash | `calculate` | `processor.calculate_hash` | hash string |
| Calcular todos | `calculate_all` | `processor.calculate_all_hashes` | dict todos |
| Verificar hash | `verify` | `processor.verify_hash` | match boolean |
| Lista archivos | `list` | `processor.calculate_file_hash_list` | lista hashes |

#### Skip Logic
- No implementada (operación idempotente)

#### Métricas (A12)
- ✅ Implementadas: `hash_operations_total`, `hash_errors`

#### Notas Técnicas
- Dependencias: standard library (`hashlib`)
- Timeout configurable (default 300s para archivos grandes)
- Algoritmos: md5, sha1, sha256, sha512
- Lectura en chunks (8192 bytes) para archivos grandes

---

### 9.8 Duplicate Tool

**Propósito**: Encontrar archivos duplicados por contenido.

**Icono**: 📋

#### Arquitectura

```
tools/duplicate_tool/
├── __init__.py         → DuplicateTool(BaseTool)
├── processor.py        → find_duplicates_by_hash, find_duplicates_async
├── ui.py               → DuplicateToolUI
└── tests/
    └── test_processor.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Por tamaño | `by_size` | `processor.find_duplicates_by_size` | dict duplicates |
| Por hash | `by_hash` | `processor.find_duplicates_by_hash` | dict duplicates |
| Async paralelo | `async` | `processor.find_duplicates_async` | dict duplicates |

#### Skip Logic
- Archivos de tamaño 0 se ignoran
- Solo extensiones específicas (configurable)

#### Métricas (A12)
- ❌ No implementadas aún

#### Notas Técnicas
- Dependencias: standard library (`hashlib`)
- Uso de ThreadPoolExecutor para paralelismo
- Callback de progreso para UI
- Extensiones por defecto: .jpg, .jpeg, .png, .mp3, .mp4, .pdf, .doc, .docx, .xls, .xlsx

---

### 9.9 Rename Tool

**Propósito**: Renombrar archivos en masa.

**Icono**: ✏️

#### Arquitectura

```
tools/rename_tool/
├── __init__.py         → RenameTool(BaseTool)
├── processor.py        → rename_with_prefix, rename_with_suffix, etc.
└── ui.py               → RenameToolUI
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Agregar prefijo | `prefix` | `processor.rename_with_prefix` | archivos renombrados |
| Agregar sufijo | `suffix` | `processor.rename_with_suffix` | archivos renombrados |
| Reemplazar texto | `replace` | `processor.rename_replace` | archivos renombrados |
| Secuencial | `sequence` | `processor.rename_sequential` | archivos renombrados |
| Mayúsculas | `uppercase` | `processor.rename_to_uppercase` | archivos renombrados |
| Minúsculas | `lowercase` | `processor.rename_to_lowercase` | archivos renombrados |

#### Skip Logic
- Si el nombre resultado ya existe, omite o reporta error

#### Métricas (A12)
- ✅ Implementadas: `rename_operations_total`, `rename_errors`

#### Notas Técnicas
- Usa `shutil.copy2` para idempotencia (copia en lugar de renombrar)
- Múltiples patrones de renaming: prefijo, sufijo, reemplazo, secuencial, caso

---

### 9.10 Search Tool

**Propósito**: Búsqueda avanzada por nombre, fecha y contenido.

**Icono**: 🔍

#### Arquitectura

```
tools/search_tool/
├── __init__.py         → SearchTool(BaseTool)
├── processor.py        → search_by_name, search_by_date, search_by_content
├── ui/
│   ├── __init__.py
│   ├── main_ui.py     → SearchToolUI
│   ├── folder_selector.py
│   ├── search_options.py
│   ├── results_view.py
│   ├── callbacks.py
│   └── state.py
└── test_processor.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Buscar por nombre | `by_name` | `processor.search_by_name` | lista archivos |
| Buscar por fecha | `by_date` | `processor.search_by_date` | lista archivos |
| Buscar contenido | `by_content` | `processor.search_by_content` | lista archivos |
| Búsqueda combinada | `all` | `processor.search_all` | lista archivos |
| Exportar CSV | `export` | `processor.export_to_csv` | archivo CSV |

#### Skip Logic
- Manejo de regex inválido graceful

#### Métricas (A12)
- ❌ No implementadas aún

#### Notas Técnicas
- Dependencias opcionales: `python-docx`, `pdfplumber`, `openpyxl`, `python-pptx`
- Soporte para búsqueda en contenido de: .docx, .pdf, .xlsx, .pptx
- Modos: exact, contains, regex

---

### 9.11 Scrubber

**Propósito**: Limpiar metadatos de imágenes y documentos.

**Icono**: 🧹

#### Arquitectura

```
tools/scrubber/
├── __init__.py         → ScrubberTool(BaseTool)
├── processor.py        → clean_image_metadata, clean_docx, clean_xlsx
└── ui.py               → ScrubberToolUI
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Limpiar imagen | `clean_image` | `processor.clean_image_metadata` | imagen limpia |
| Limpiar DOCX | `clean_docx` | `processor.clean_docx` | DOCX limpio |
| Limpiar XLSX | `clean_xlsx` | `processor.clean_xlsx` | XLSX limpio |
| Limpiar PDF | `clean_pdf` | `core.utils.clean_metadata` | PDF limpio |
| Ver metadata | `view` | `processor.get_image_metadata` | display en UI |

#### Skip Logic
- Formatos no soportados retornan error

#### Métricas (A12)
- ✅ Implementadas: `scrubber_operations_total`, `scrubber_errors`

#### Notas Técnicas
- Dependencias: `Pillow` (imágenes), `python-docx` (DOCX), `openpyxl` (XLSX)
- Soporta: JPG, JPEG, PNG, TIFF, WEBP (imágenes)
- Verificación de existencia de metadatos antes de limpiar

---

### 9.12 GIF Tool

**Propósito**: Crear GIFs animados desde imágenes.

**Icono**: 🎞️

#### Arquitectura

```
tools/gif_tool/
├── __init__.py         → GifTool(BaseTool)
├── processor.py        → create_gif, optimize_gif
├── ui.py               → GifToolUI
└── tests/
    └── test_processor.py
```

#### Casos de Uso

| Operación | Acción | Processor | Output |
|-----------|--------|-----------|--------|
| Crear GIF | `create` | `processor.create_gif` | `.gif` animado |
| Optimizar | `optimize` | `processor.optimize_gif` | `.gif` optimizado |

#### Skip Logic
- **create**: Si todas las entradas ya son .gif, omite

#### Métricas (A12)
- ✅ Implementadas: `gif_operations_total`, `gif_errors`

#### Notas Técnicas
- Dependencias: `Pillow` (PIL)
- Parámetros: duration (ms), loop (0=infinito), resize automático al primer frame
- Conversión automática a modo RGBA si es necesario

---

*Documento vivo - actualizar según evoluciona el proyecto.*