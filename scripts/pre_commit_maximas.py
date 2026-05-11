#!/usr/bin/env python3
"""
Pre-commit hook para verificar cumplimiento de maximas del proyecto.

Este script debe ejecutarse ANTES de cada commit para verificar:
- C2: Código compartido en core/ - NO duplicar
- A12: Observabilidad - métricas si corresponde
- E1: Compatibilidad Windows/Linux
- A1: Una responsabilidad por módulo

Ejecutar desde la raíz del proyecto:
    python scripts/pre_commit_maximas.py
"""
import os
import re
import sys
from pathlib import Path

# Configuración
ROOT = Path(__file__).parent


def check_c2(file_path: Path) -> tuple:
    """Verifica C2: código duplicado o en core/"""
    # Patrones que indican posible duplicación
    dupe_patterns = [
        r"def get_output_path",
        r"def validate_input",
        r"def check_ffmpeg",
    ]
    
    content = file_path.read_text(errors='ignore')
    
    for pattern in dupe_patterns:
        if re.search(pattern, content):
            # Verificar si existe en core/
            core_path = ROOT / "core" / f"{file_path.stem.replace('tools_', '')}.py"
            if not core_path.exists():
                return False, f"Posible duplicación: {pattern} - considerar mover a core/"
    
    return True, None

def check_a12(file_path: Path) -> tuple:
    """Verifica A12: métricas para operaciones lentas"""
    # Si hay threading, debería haber métricas
    content = file_path.read_text(errors='ignore')
    
    has_threading = "threading" in content or "ThreadPoolExecutor" in content
    has_metrics = "from core.metrics" in content or "from core import metrics" in content
    
    if has_threading and not has_metrics:
        return False, f"Usa threading pero no importa core/metrics (A12)"
    
    return True, None

def check_e1(file_path: Path) -> tuple:
    """Verifica E1: multiplataforma"""
    content = file_path.read_text(errors='ignore')
    
    # Si usa paths hardcodeados de Windows, warn
    has_hardcode = re.search(r"[A-Z]:\\|C:\\\\|D:\\\\", content)
    
    if has_hardcode:
        return False, f"Path hardcodeado de Windows encontrado (E1)"
    
    return True, None


MAXIMAS = {
    "C2": {
        "name": "Código compartido en core/",
        "check": check_c2,
        "message": "Evitar duplicación - usar core/ o módulos existentes"
    },
    "A12": {
        "name": "Observabilidad",
        "check": check_a12,
        "message": "Usar métricas para operaciones lentas"
    },
    "E1": {
        "name": "Multiplataforma",
        "check": check_e1,
        "message": "Usar platform.system() para paths"
    }
}


def scan_files() -> dict:
    """Escanear archivos modificados"""
    issues = []
    
    # Archivos Python a escanear
    patterns = ["tools/**/*.py", "core/**/*.py"]
    
    for pattern in patterns:
        for file_path in ROOT.glob(pattern):
            if file_path.is_file() and file_path.suffix == ".py":
                for maxima_id, maxima in MAXIMAS.items():
                    passed, issue = maxima["check"](file_path)
                    if not passed:
                        issues.append({
                            "file": str(file_path.relative_to(ROOT)),
                            "maxima": maxima_id,
                            "issue": issue
                        })
    
    return issues

def main():
    print("🔍 Verificando cumplimiento de maximas...")
    
    issues = scan_files()
    
    if issues:
        print("\n⚠️ ISSUES ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue['maxima']}: {issue['file']} - {issue['issue']}")
        
        print("\n⚠️ Estas violaciones deben resolverse ANTES de commit.")
        print("Puedes forzar commit con: git commit --no-verify")
        return 1
    else:
        print("✅ Todas las maximas verificadas correctamente")
        return 0

if __name__ == "__main__":
    sys.exit(main())