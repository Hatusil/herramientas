"""
Exportación de resultados de búsqueda a CSV y TXT.
Separado de processor.py por SRP (máxima R0: clases <300 líneas).
"""
import csv
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def export_to_csv(results: List[Dict], output_path: str) -> bool:
    """Exporta resultados a CSV."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['path', 'name', 'size', 'modified', 'matches'])
            writer.writeheader()
            writer.writerows(results)
        return True
    except Exception as e:
        logger.error(f"Export CSV error: {e}")
        return False


def export_to_txt(results: List[Dict], output_path: str) -> bool:
    """Exporta resultados a TXT."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(f"{r['path']}\n")
        return True
    except Exception as e:
        logger.error(f"Export TXT error: {e}")
        return False