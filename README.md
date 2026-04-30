# Herramientas 🛠️

Dashboard de herramientas de productividad desarrollado en Python con CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Aplicación de escritorio con múltiples herramientas para procesamiento de archivos y análisis de texto.

## Herramientas Incluidas

| Ícono | Herramienta | Descripción |
|-------|-------------|--------------|
| 🔍 | **Buscador** | Busca archivos por nombre, contenido (DOCX/PDF/XLSX/PPTX), fecha y extensión |
| 📋 | **Duplicados** | Encuentra y elimina archivos duplicados por tamaño o hash |
| 📄 | **PDF** | Une, extrae páginas, watermarks, rota, cifra, comprime |
| #️⃣ | **Hash** | Calcula MD5, SHA1, SHA256, SHA512 para verificar archivos |
| ✏️ | **Renombrar** | Renombra en masa con prefijos, sufijos, números, mayúsculas |
| 📦 | **Comprimir** | ZIP, TAR.GZ - comprime y extrae |
| 📊 | **Text Analyzer** | WordCloud, frecuencia, estadísticas, n-grams, trends, correlaciones |
| 🎵 | **Audio** | Normaliza LUFS, limpia metadatos, convierte |
| 🎬 | **Video** | Extrae audio, convierte, info |
| 🎞️ | **GIF** | Crea GIFs animados de imágenes |
| 🧹 | **Limpiador** | Elimina metadatos EXIF, DOCX, XLSX |

## Requisitos

- Python 3.11+
- FFmpeg (para audio/video)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/herramientas.git
cd herramientas

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
./ejecutar.sh  # Linux/Mac
python __main__.py  # Windows
```

## Crear ejecutable .exe (Windows)

```bash
python build.py
```

El ejecutable se crea en `dist/Herramientas.exe`

## Agregar Nuevas Herramientas

1. Crear directorio `tools/<nombre_tool>/`
2. Crear `__init__.py` con clase que herede de `BaseTool`
3. Implementar: `get_name()`, `get_icon()`, `get_description()`, `build_ui()`
4. ¡Se descubre automáticamente!

## Estructura

```
herramientas/
├── core/              # Sistema base
├── ui/                # Interfaz gráficas
├── tools/             # Herramientas (plugins)
└── assets/            # Recursos
```

## Licencia

MIT License - Pode usar, modificar y distribuir libre