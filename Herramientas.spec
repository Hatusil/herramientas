# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all para las librerías principales
hiddenimports = []

# Agregar todos los submódulos de estas librerías
for lib in ['customtkinter', 'PIL', 'matplotlib', 'numpy']:
    try:
        hiddenimports.extend(collect_submodules(lib))
    except:
        hiddenimports.append(lib)

# Librerías adicionales
for lib in ['mutagen', 'pypdf', 'reportlab', 'piexif', 'docx', 'openpyxl', 
            'chardet', 'wordcloud', 'nltk', 'pdfplumber', 'requests', 
            'bs4', 'beautifulsoup4', 'pptx', 'lxml', 'sklearn']:
    hiddenimports.append(lib)

# Datos del proyecto
datas = [
    ('core', 'core'),
    ('tools', 'tools'), 
    ('ui', 'ui'),
    ('assets', 'assets'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('__main__.py', '.')
]

a = Analysis(
    ['ui\\app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
)