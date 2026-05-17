# Herramientas 🛠️

Dashboard de herramientas de productividad desarrollado en Python con CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Aplicación de escritorio con múltiples herramientas para procesamiento de archivos y análisis de texto.

## Herramientas Incluidas

| Ícono | Herramienta | Descripción |
|-------|-------------|-------------|
| 🔍 | **Buscador** | Busca archivos por nombre, contenido (DOCX/PDF/XLSX/PPTX), fecha y extensión |
| 📋 | **Duplicados** | Encuentra y elimina archivos duplicados por tamaño o hash |
| 📄 | **PDF** | Une, extrae páginas, watermarks, rota, cifra, comprime |
| #️⃣ | **Hash** | Calcula MD5, SHA1, SHA256, SHA512 para verificar archivos |
| ✏️ | **Renombrar** | Renombra en masa con prefijos, sufijos, números, mayúsculas |
| 📦 | **Compresor** | ZIP, TAR.GZ - comprime y extrae |
| 📊 | **Text Analyzer** | WordCloud, frecuencia, estadísticas, n-grams, trends, correlaciones |
| 🎵 | **Audio** | Normaliza, limpia metadatos, convierte, **transcribe** (OLMoASR) |
| 🎬 | **Video** | Extrae audio, convierte, info |
| 🖼️ | **Imagen** | PDI: 7 fases — filtros, geometría, bordes, morfología |
| 🎞️ | **GIF** | Crea GIFs animados de imágenes |
| 🧹 | **Limpiador** | Elimina metadatos EXIF, DOCX, XLSX |

## Requisitos

- Python 3.11+
- FFmpeg (para audio/video) - incluido en el proyecto
- opencv-python (para herramienta Imagen)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/herramientas.git
cd herramientas

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
# Windows
python __main__.py
# o
python -m herramientas
# o
python ui/app.py

# Linux/Mac
python3 ui/app.py
# o
./ejecutar.sh
```

## Crear ejecutable .exe (Windows)

```bash
python build.py
```

El ejecutable se crea en `dist/Herramientas.exe` o `build/dist/`.

## Agregar Nuevas Herramientas

1. Crear directorio `tools/<nombre_tool>/`
2. Crear `__init__.py` con clase que herede de `BaseTool`
3. Implementar: `get_name()`, `get_icon()`, `get_description()`, `build_ui()`
4. ¡Se descubre automáticamente!

## Estructura

```
herramientas/
├── core/              # Sistema base (BaseTool, PluginManager, config, utils)
├── ui/                # Interfaz gráfica (app, sidebar, componentes)
│   ├── app.py         # Main app (<300 líneas - SRP refactorizado)
│   ├── window_utils.py
│   └── content_manager.py
├── tools/             # Herramientas (plugins - 12 directorios)
│   ├── video_tool/
│   │   ├── processor.py    # (<300 líneas)
│   │   └── async_processors.py
│   ├── scrubber/
│   │   ├── processor.py   # (re-export - 20 líneas)
│   │   ├── image_processor.py
│   │   ├── docx_processor.py
│   │   └── xlsx_processor.py
│   ├── search_tool/
│   │   ├── processor.py   # (re-export - 28 líneas)
│   │   ├── filters.py
│   │   ├── content_extractors.py
│   │   ├── exports.py
│   │   └── search_all.py
│   ├── text_tool/ui/
│   │   ├── main_ui.py      # (threading + keyboard extraídos)
│   │   ├── threading_utils.py
│   │   └── keyboard_shortcuts.py
│   └── pdf_tool/
│       ├── processor.py    # (630 líneas - wrapper API)
│       ├── utils.py
│       ├── async_processors.py
│       └── modules/
│           ├── transform.py      # (re-export - 20 líneas)
│           ├── validation.py
│           └── transform_operations.py
├── tests/             # Tests unitarios con pytest
├── informes/          # Documentación interna (roadmap, backlog)
├── assets/            # Recursos (iconos, imágenes)
├── build/             # Build outputs de PyInstaller
├── dist/              # Ejecutables generados
└── .agent/            # Configuración de agentes IA
```

### Arquitectura y Maximas

El proyecto sigue 20 maximas de arquitectura (almacenadas en Engram):

- **R0**: Clases <300 líneas, funciones <50 líneas
- **A1-A12**: SRP, cohesión, acoplamiento, interfaces, reemplazabilidad, reusabilidad, stateless, idempotencia, asincronía, sin bloqueo, observabilidad
- **C2**: Código compartido en `core/`

Archivos refactorizados para cumplir SRP:
- ✅ ui/app.py (308 → 255 líneas)
- ✅ video_tool/processor.py (329 → 299 líneas)
- ✅ scrubber/processor.py (374 → 20 líneas)
- ✅ search_tool/processor.py (453 → 28 líneas)
- ✅ pdf_tool/modules/transform.py (465 → 20 líneas)

## Desarrollo

### Ejecutar tests
```bash
pytest
```

### Verificar estructura de plugins
```bash
python -c "from core.plugin_manager import PluginManager; pm = PluginManager(); print(pm.discover_tools())"
```

## Licencia

MIT License - Puedes usar, modificar y distribuir libremente