# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('core', 'core'), ('tools', 'tools'), ('ui', 'ui'), ('assets', 'assets'), ('requirements.txt', '.'), ('README.md', '.'), ('__main__.py', '.')]
binaries = []
hiddenimports = ['customtkinter', 'PIL', 'mutagen', 'pypdf', 'reportlab', 'piexif', 'docx', 'openpyxl', 'chardet', 'wordcloud', 'nltk', 'pdfplumber', 'requests', 'bs4', 'beautifulsoup4', 'pptx', 'lxml']
tmp_ret = collect_all('nltk')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('bs4')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('beautifulsoup4')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['ui\\app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
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
