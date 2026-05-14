"""
Build script para crear ejecutable con PyInstaller.
Usa Herramientas.spec para la configuración.
"""
import platform
import PyInstaller.__main__
import os

print("Building Herramientas using Herramientas.spec...")

# Usar el spec file directamente
PyInstaller.__main__.run(["Herramientas.spec"])

# Verificar que se creó el ejecutable (extensión según plataforma)
ext = ".exe" if platform.system() == "Windows" else ""
exe_path = f"dist/Herramientas{ext}"

if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"\nDone! Executable at: {exe_path} ({size_mb:.1f} MB)")
elif os.listdir("dist/"):
    # Si existe algún archivo en dist/, el build funcionó
    print(f"\nDone! Build completed, check dist/")
else:
    print(f"\nError: No se encontró {exe_path}")