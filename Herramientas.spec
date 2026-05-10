# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Forzar inclusión de customtkinter y sus submódulos
hiddenimports = []

# Collect todos los submódulos de las librerías principales
for lib in ['customtkinter', 'PIL', 'PIL._imaging', 'matplotlib', 'matplotlib.backends', 'numpy', 'tkinter', 'cv2']:
    try:
        hiddenimports.extend(collect_submodules(lib))
    except:
        pass

# Librerías adicionales (sin nltk/scipy que tienen problemas en PyInstaller)
libs = [
    'mutagen', 'pypdf', 'pypdf2', 'reportlab', 'piexif',
    'docx', 'openpyxl', 'chardet', 'wordcloud',
    'pdfplumber', 'requests', 'bs4', 'beautifulsoup4',
    'pptx', 'lxml', 'cv2', 'numpy'
]

for lib in libs:
    hiddenimports.append(lib)

# Agregar datos de las libs (sin nltk)
datas = []
for lib in ['customtkinter', 'PIL', 'matplotlib', 'numpy', 'cv2']:
    try:
        datas += collect_data_files(lib)
    except:
        pass

# Datos del proyecto
project_datas = [
    ('core', 'core'),
    ('tools', 'tools'), 
    ('ui', 'ui'),
    ('assets', 'assets'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('__main__.py', '.')
]
datas.extend(project_datas)

a = Analysis(
    ['ui\\app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'nltk', 'scipy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Herramientas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)