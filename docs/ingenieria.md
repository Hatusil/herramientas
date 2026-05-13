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

*(Pendiente)*

---

### 9.3 Image Tool

*(Pendiente)*

---

*Documento vivo - actualizar según evoluciona el proyecto.*