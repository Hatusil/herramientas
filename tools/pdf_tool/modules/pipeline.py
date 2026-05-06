"""
PDF Pipeline: Sistema de pipeline para encadenar múltiples operaciones PDF.

Permite agregar múltiples operaciones (reorder, watermark, rotate, extract)
y aplicarlas en un solo paso, generando un único archivo de salida.

Operaciones soportadas:
- reorder: Reordenar páginas
- watermark: Agregar marca de agua
- rotate: Rotar páginas
- extract: Extraer páginas/rango
"""
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Tipos de operaciones soportadas en el pipeline."""
    REORDER = "reorder"
    WATERMARK = "watermark"
    ROTATE = "rotate"
    EXTRACT = "extract"
    EXTRACT_RANGE = "extract_range"


@dataclass
class PipelineOperation:
    """Representa una operación en el pipeline."""
    op_type: OperationType
    params: Dict[str, Any]
    description: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Genera descripción legible de la operación."""
        if self.op_type == OperationType.REORDER:
            order = self.params.get('new_order', [])
            return f"Reorder: {order}"
        elif self.op_type == OperationType.WATERMARK:
            text = self.params.get('text', '')
            return f"Watermark: {text}"
        elif self.op_type == OperationType.ROTATE:
            degrees = self.params.get('degrees', 0)
            pages = self.params.get('pages', [])
            if pages:
                return f"Rotate: {degrees}° páginas {pages}"
            return f"Rotate: {degrees}°"
        elif self.op_type == OperationType.EXTRACT:
            pages = self.params.get('pages', [])
            return f"Extract: páginas {pages}"
        elif self.op_type == OperationType.EXTRACT_RANGE:
            start = self.params.get('start', 0)
            end = self.params.get('end', 0)
            return f"Extract: {start}-{end}"
        return f"{self.op_type.value}"


class PDFPipeline:
    """
    Pipeline para encadenar operaciones PDF.
    
    Permite acumular múltiples operaciones y ejecutarlas en cadena,
    generando un único archivo de salida.
    
    Ejemplo de uso:
        pipeline = PDFPipeline(input_file="input.pdf")
        pipeline.add_operation("reorder", {"new_order": [3, 1, 2]})
        pipeline.add_operation("watermark", {"text": "DRAFT"})
        pipeline.add_operation("rotate", {"degrees": 90})
        result = pipeline.execute()
    """
    
    def __init__(self, input_file: str, output_path: Optional[str] = None):
        """
        Inicializa el pipeline.
        
        Args:
            input_file: Ruta al archivo PDF de entrada
            output_path: Ruta de salida opcional (si None, genera automáticamente)
        """
        self.input_file = input_file
        self.output_path = output_path
        self.operations: List[PipelineOperation] = []
        
        # Validar archivo de entrada
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Archivo no encontrado: {input_file}")
        
        # Generar output_path si no se proporciona
        if self.output_path is None:
            from core.utils import get_output_path
            self.output_path = get_output_path(input_file, '_pipeline')
    
    def add_operation(self, op_type: str, params: Dict[str, Any]) -> None:
        """
        Agrega una operación a la cola del pipeline.
        
        Args:
            op_type: Tipo de operación ("reorder", "watermark", "rotate", "extract")
            params: Parámetros de la operación
        """
        # Normalizar tipo de operación
        op_type_lower = op_type.lower()
        
        if op_type_lower == "reorder":
            op = PipelineOperation(OperationType.REORDER, params)
        elif op_type_lower == "watermark":
            op = PipelineOperation(OperationType.WATERMARK, params)
        elif op_type_lower == "rotate":
            op = PipelineOperation(OperationType.ROTATE, params)
        elif op_type_lower == "extract":
            # Determinar si es extract o extract_range
            if 'start' in params and 'end' in params:
                op = PipelineOperation(OperationType.EXTRACT_RANGE, params)
            else:
                op = PipelineOperation(OperationType.EXTRACT, params)
        else:
            raise ValueError(f"Tipo de operación desconocida: {op_type}")
        
        self.operations.append(op)
        logger.info(f"Operación agregada: {op.description}")
    
    def get_operations_summary(self) -> List[str]:
        """Retorna lista de descripciones de operaciones."""
        return [op.description for op in self.operations]
    
    def clear_operations(self) -> None:
        """Limpia todas las operaciones acumuladas."""
        self.operations.clear()
        logger.info("Operaciones limpiadas")
    
    def execute(self) -> Dict[str, Any]:
        """
        Ejecuta todas las operaciones en cadena.
        
        Returns:
            dict: Resultado con 'success', 'output_file', 'message', 'error'
        """
        if not self.operations:
            return {
                'success': False,
                'error': 'No hay operaciones para ejecutar',
                'output_file': None
            }
        
        # Importar processor functions
        from tools.pdf_tool import processor
        
        current_file = self.input_file
        temp_files = []  # Archivos temporales para limpiar
        
        try:
            for i, op in enumerate(self.operations):
                logger.info(f"Ejecutando operación {i+1}/{len(self.operations)}: {op.description}")
                
                result = self._execute_single_operation(processor, current_file, op)
                
                if not result.get('success'):
                    return {
                        'success': False,
                        'error': f"Error en operación {op.description}: {result.get('error')}",
                        'output_file': None
                    }
                
                # Obtener el output de esta operación
                output_files = result.get('output_files', [])
                if not output_files:
                    return {
                        'success': False,
                        'error': f"No se generó output para {op.description}",
                        'output_file': None
                    }
                
                # Guardar archivo anterior para limpiarlo después
                if current_file != self.input_file:
                    temp_files.append(current_file)
                
                # Usar el output como input para la siguiente operación
                current_file = output_files[0]
            
            # El último archivo es el output final
            # Renombrar si es diferente al output_path deseado
            if current_file != self.output_path:
                # Copiar al output_path final
                import shutil
                shutil.copy2(current_file, self.output_path)
                # Limpiar el temporal
                if current_file != self.input_file:
                    temp_files.append(current_file)
            
            logger.info(f"Pipeline ejecutado: {len(self.operations)} operaciones completadas")
            
            return {
                'success': True,
                'output_file': self.output_path,
                'message': f"Pipeline completado: {len(self.operations)} operaciones",
                'operations_executed': len(self.operations)
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'output_file': None
            }
        
        finally:
            # Limpiar archivos temporales intermedios (siempre se ejecuta)
            for tf in temp_files:
                if tf and os.path.exists(tf):
                    try:
                        os.remove(tf)
                    except Exception:
                        pass
    
    def _execute_single_operation(
        self, 
        processor, 
        input_file: str, 
        op: PipelineOperation
    ) -> Dict[str, Any]:
        """Ejecuta una sola operación."""
        files = [input_file]
        
        if op.op_type == OperationType.REORDER:
            return processor.reorder_pages(files, **op.params)
        
        elif op.op_type == OperationType.WATERMARK:
            # Determinar tipo de watermark
            if 'text' in op.params:
                return processor.add_text_watermark(files, **op.params)
            elif 'image_path' in op.params:
                return processor.add_image_watermark(files, **op.params)
            else:
                return {'success': False, 'error': 'Parámetros de watermark inválidos'}
        
        elif op.op_type == OperationType.ROTATE:
            # Usar rotate_pages con pages=None (todas las páginas)
            degrees = op.params.get('degrees', 90)
            pages = op.params.get('pages', None)
            return processor.rotate_pages(files, degrees=degrees, pages=pages)
        
        elif op.op_type == OperationType.EXTRACT:
            return processor.extract_pages(files, **op.params)
        
        elif op.op_type == OperationType.EXTRACT_RANGE:
            return processor.extract_range(files, **op.params)
        
        else:
            return {'success': False, 'error': f'Operación no soportada: {op.op_type}'}


# =============================================================================
# FUNCIONES DE FACTORÍA
# =============================================================================

def create_pipeline(input_file: str, output_path: Optional[str] = None) -> PDFPipeline:
    """
    Crea una instancia de PDFPipeline.
    
    Args:
        input_file: Ruta al PDF de entrada
        output_path: Ruta de salida opcional
        
    Returns:
        PDFPipeline: Instancia del pipeline
    """
    return PDFPipeline(input_file, output_path)


def execute_pipeline_operations(
    input_file: str,
    operations: List[Dict[str, Any]],
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Ejecuta una lista de operaciones en pipeline.
    
    Args:
        input_file: Archivo PDF de entrada
        operations: Lista de diccionarios con 'type' y 'params'
        output_path: Ruta de salida opcional
        
    Returns:
        dict: Resultado de la ejecución
    """
    pipeline = create_pipeline(input_file, output_path)
    
    for op in operations:
        op_type = op.get('type', '')
        params = op.get('params', {})
        pipeline.add_operation(op_type, params)
    
    return pipeline.execute()