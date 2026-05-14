"""
PDFTool: Plugin para procesamiento de archivos PDF.
"""
import customtkinter as ctk
from typing import List, Dict, Any
import logging

from core.base_tool import BaseTool
from tools.pdf_tool import processor
from tools.pdf_tool.ui import PDFToolUI


logger = logging.getLogger(__name__)


class PDFTool(BaseTool):
    """Herramienta para procesar archivos PDF."""
    
    def __init__(self):
        self.ui = None
        self.files = []
    
    def get_name(self) -> str:
        return "PDF"
    
    def get_icon(self) -> str:
        return "📄"
    
    def get_description(self) -> str:
        return "Watermark, editar, combinar, encriptar, optimizar PDFs"
    
    def build_ui(self, parent_frame) -> None:
        """Construye la UI de la herramienta."""
        self.ui = PDFToolUI(parent_frame, self._on_process)
        self.ui.pack(fill="both", expand=True)
    
    def _on_process(self, action: str, files: list, options: dict) -> dict:
        """
        Maneja el procesamiento de archivos.
        
        Args:
            action: Acción a realizar
            files: Lista de archivos a procesar
            options: Opciones adicionales
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            if action == 'text_watermark':
                return processor.add_text_watermark(
                    files,
                    text=options.get('text', 'WATERMARK'),
                    font_size=options.get('font_size', 48),
                    color=options.get('color', '#888888'),
                    opacity=options.get('opacity', 0.3),
                    rotation=options.get('rotation', 45),
                )
            
            elif action == 'image_watermark':
                return processor.add_image_watermark(
                    files,
                    image_path=options.get('image_path', ''),
                    scale=options.get('scale', 0.5),
                    opacity=options.get('opacity', 0.3),
                )
            
            elif action == 'remove_watermark':
                return processor.remove_watermarks(
                    files,
                    mode=options.get('mode', 'auto'),
                    detection_mode=options.get('detection_mode', 'auto'),
                    manual_region=options.get('manual_region')
                )
            
            elif action == 'add_annotation':
                return processor.add_text_annotation(
                    files,
                    text=options.get('text', ''),
                    page=options.get('page', 0),
                    x=options.get('x', 100),
                    y=options.get('y', 100),
                )
            
            elif action == 'redact':
                return processor.redact_area(
                    files,
                    page=options.get('page', 0),
                    x=options.get('x', 100),
                    y=options.get('y', 100),
                    width=options.get('width', 100),
                    height=options.get('height', 30),
                )
            
            elif action == 'rotate':
                return processor.rotate_pages(
                    files,
                    degrees=options.get('degrees', 90),
                    pages=options.get('pages'),
                )
            
            elif action == 'reorder':
                return processor.reorder_pages(
                    files,
                    new_order=options.get('new_order', []),
                )
            
            elif action == 'merge':
                return processor.merge_pdfs(files)
            
            elif action == 'extract':
                return processor.extract_pages(
                    files,
                    pages=options.get('pages', []),
                )
            
            elif action == 'extract_range':
                return processor.extract_range(
                    files,
                    start=options.get('start', 1),
                    end=options.get('end', 1),
                )
            
            elif action == 'extract_page':
                return processor.extract_page(
                    files,
                    page_number=options.get('page_number', 1),
                )
            
            elif action == 'reorder_advanced':
                return processor.reorder_pages_advanced(
                    files,
                    new_order=options.get('new_order', []),
                )
            
            elif action == 'page_numbers':
                return processor.add_page_numbers(
                    files,
                    position=options.get('position', 'footer'),
                    start=options.get('start', 1),
                    format=options.get('format', 'Página {n} de {total}'),
                )
            
            elif action == 'encrypt':
                return processor.encrypt_pdf(
                    files,
                    password=options.get('password', ''),
                )
            
            elif action == 'decrypt':
                return processor.decrypt_pdf(
                    files,
                    password=options.get('password', ''),
                )
            
            elif action == 'compress':
                return processor.compress_pdf(
                    files,
                    level=options.get('level', 'medium'),
                )
            
            elif action == 'clean_metadata':
                return processor.clean_metadata(files)
            
            else:
                return {
                    'success': False,
                    'message': f'Acción desconocida: {action}',
                    'output_files': [],
                    'error': 'Unknown action'
                }
        
        except Exception as e:
            logger.error(f"Error procesando PDF: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'output_files': [],
                'error': str(e)
            }
    
    def process(self, files: list, options: dict) -> dict:
        """
        Procesa los archivos.
        
        Args:
            files: Lista de rutas de archivos
            options: Opciones de procesamiento
            
        Returns:
            dict: Resultado con success, message, output_files, error
        """
        action = options.get('action', 'text_watermark')
        return self._on_process(action, files, options)