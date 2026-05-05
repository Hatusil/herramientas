"""
Build script para crear ejecutable con PyInstaller.
Usa Herramientas.spec para la configuración.
"""
import PyInstaller.__main__
import os

print("Building Herramientas using Herramientas.spec...")

# Usar el spec file directamente
PyInstaller.__main__.run(["Herramientas.spec"])

# Verificar que se creó el exe
exe_path = "dist/Herramientas.exe"
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"\nDone! Executable at: {exe_path} ({size_mb:.1f} MB)")
else:
    print(f"\nError: No se encontró {exe_path}")