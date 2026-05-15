#!/usr/bin/env python3
"""
Architecture Verifier - Pre-commit hook para verificar reglas de arquitectura.
Uso: python scripts/verify_architecture.py
También se puede usar como git hook en .git/hooks/pre-commit
"""
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Ejecuta los tests de arquitectura."""
    project_root = Path(__file__).parent.parent
    test_file = project_root / "tests" / "test_arch_structure.py"
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    return result.returncode, result.stdout, result.stderr


def main():
    print("🔍 Verificando arquitectura...")
    print("=" * 60)
    
    code, stdout, stderr = run_tests()
    
    # Mostrar output relevante
    print(stdout)
    if stderr:
        print("STDERR:", stderr[:500])
    
    print("=" * 60)
    
    if code == 0:
        print("✅ Arquitectura verificada - OK")
        sys.exit(0)
    else:
        print("❌ VIOLACIÓN DE ARQUITECTURA")
        print("\nEl commit fue BLOQUEADO por violar reglas de arquitectura.")
        print("Fix los errores antes de hacer commit.")
        sys.exit(1)


if __name__ == "__main__":
    main()