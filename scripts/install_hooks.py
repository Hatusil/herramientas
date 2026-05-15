#!/usr/bin/env python3
"""
Instala el pre-commit hook de arquitectura.
Ejecutar: python scripts/install_hooks.py
"""
import os
import sys
from pathlib import Path


def install_hook():
    """Instala el hook en .git/hooks/pre-commit"""
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"
    hooks_dir = git_dir / "hooks"
    
    if not git_dir.exists():
        print("❌ Este directorio no es un repositorio git")
        sys.exit(1)
    
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / "pre-commit"
    
    # Crear el hook script
    hook_content = """#!/bin/bash
# Pre-commit hook - Architecture verifier
# Bloquea commits que violen reglas de arquitectura

echo "🔍 Verificando arquitectura..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

python3 scripts/verify_architecture.py
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo "❌ Commit bloqueado por violation de arquitectura"
    exit 1
fi

echo "✅ Arquitectura verificada"
exit 0
"""
    
    # Escribir el hook
    hook_path.write_text(hook_content)
    
    # Hacer ejecutable
    hook_path.chmod(0o755)
    
    print(f"✅ Hook instalado en: {hook_path}")
    print("\nEl hook se ejecutará automáticamente en cada commit.")
    print("Para desinstalar: rm .git/hooks/pre-commit")


def uninstall_hook():
    """Desinstala el hook"""
    project_root = Path(__file__).parent.parent
    hook_path = project_root / ".git" / "hooks" / "pre-commit"
    
    if hook_path.exists():
        hook_path.unlink()
        print("✅ Hook desinstalado")
    else:
        print("No hay hook instalado")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_hook()
    else:
        install_hook()