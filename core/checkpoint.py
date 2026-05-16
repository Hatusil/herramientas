"""
Checkpoint system for D18 - Guardar respaldo antes de operaciones costosas.
"""
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any
from functools import wraps

# Directorio de checkpoints
CHECKPOINT_DIR = Path("output/checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# Threshold para operación "costosa" (líneas de código afectadas)
COSTLY_THRESHOLD = 100


def get_project_state() -> dict:
    """Captura el estado actual del proyecto."""
    state = {
        "timestamp": datetime.now().isoformat(),
        "git_branch": _get_git_branch(),
        "uncommitted_files": _get_uncommitted_changes(),
    }
    return state


def _get_git_branch() -> str:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _get_uncommitted_changes() -> list:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except Exception:
        return []


def save_checkpoint(operation: str, context: Optional[dict] = None) -> str:
    """
    Guarda un checkpoint antes de operación costosa.
    
    Args:
        operation: Nombre de la operación
        context: Contexto adicional a guardar
        
    Returns:
        ID del checkpoint para referencia
    """
    state = get_project_state()
    if context:
        state["context"] = context
    
    # Generar ID único
    checkpoint_id = hashlib.md5(
        f"{operation}{state['timestamp']}".encode()
    ).hexdigest()[:8]
    
    checkpoint = {
        "id": checkpoint_id,
        "operation": operation,
        "state": state,
    }
    
    filepath = CHECKPOINT_DIR / f"{checkpoint_id}.json"
    filepath.write_text(json.dumps(checkpoint, indent=2))
    
    return checkpoint_id


def load_checkpoint(checkpoint_id: str) -> Optional[dict]:
    """Carga un checkpoint guardado."""
    filepath = CHECKPOINT_DIR / f"{checkpoint_id}.json"
    if filepath.exists():
        return json.loads(filepath.read_text())
    return None


def list_checkpoints() -> list:
    """Lista todos los checkpoints disponibles."""
    checkpoints = []
    for f in CHECKPOINT_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            checkpoints.append({
                "id": data["id"],
                "operation": data["operation"],
                "timestamp": data["state"]["timestamp"],
            })
        except Exception:
            continue
    return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)


def costly_operation(threshold: int = COSTLY_THRESHOLD) -> Callable:
    """
    Decorador para marcar operaciones costosas.
   自动 guarda checkpoint antes de ejecutar.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Auto-checkpoint antes de operación
            checkpoint_id = save_checkpoint(
                operation=f"{func.__module__}.{func.__name__}",
                context={"args": str(args)[:100], "threshold": threshold}
            )
            print(f"[CHECKPOINT] Guardado {checkpoint_id} antes de {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                print(f"[CHECKPOINT] Operación completada exitosamente")
                return result
            except Exception as e:
                print(f"[CHECKPOINT] Error en operación: {e}")
                print(f"[CHECKPOINT] Recovery ID: {checkpoint_id}")
                raise
        return wrapper
    return decorator


# Alias para uso rápido
checkpoint = save_checkpoint