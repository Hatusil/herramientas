"""
Build script para crear ejecutable con PyInstaller.
"""
import PyInstaller.__main__
import os
import shutil
import time

# Configuración
APP_NAME = "Herramientas"
ENTRY_POINT = "ui/app.py"
ICON = None  # Agregar path a icono si existe: "assets/icon.ico"

# Nuevo directorio para evitar conflictos
dist_dir = "dist_new"
build_dir = "build_new"

if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

print(f"Building {APP_NAME}...")

# argumentos PyInstaller
args = [
    ENTRY_POINT,
    "--name", APP_NAME,
    "--onefile",       # Un solo .exe
    "--windowed",     # Sin consola
    #"--clean",
]

# Agregar icono si existe
if ICON:
    args.extend(["--icon", ICON])

# Incluir directorios del proyecto
dirs_to_include = ["core", "tools", "ui", "assets"]
for d in dirs_to_include:
    if os.path.exists(d):
        args.extend(["--add-data", f"{d}:{d}"])

# Agregar archivos sueltos
files_to_include = ["requirements.txt", "README.md", "__main__.py"]
for f in files_to_include:
    if os.path.exists(f):
        args.extend(["--add-data", f"{f}:."])

# Hidden imports para todas las libs
hidden_imports = [
    "customtkinter",
    "PIL",
    "mutagen",
    "pypdf",
    "reportlab",
    "piexif",
    "docx",
    "openpyxl",
    "chardet",
    "wordcloud",
    "nltk",
    "pdfplumber",
    "requests",
    # BeautifulSoup4
    "bs4",
    "beautifulsoup4",
    "pptx",
    "lxml",
]

for imp in hidden_imports:
    args.extend(["--hidden-import", imp])

# Collect all para libs
args.extend(["--collect-all", "nltk"])
args.extend(["--collect-all", "bs4"])
args.extend(["--collect-all", "beautifulsoup4"])

PyInstaller.__main__.run(args)

# Mover al directorio final
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists(dist_dir):
    os.rename(dist_dir, "dist")
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

print(f"\nDone! Executable at: dist/{APP_NAME}.exe")