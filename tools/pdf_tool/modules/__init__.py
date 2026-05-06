"""
PDF Tool Modules - Módulos especializados para procesamiento de PDFs.

Este paquete contiene módulos separados para diferentes funcionalidades de PDF:
- info: Información y metadatos de PDFs
- watermarks: Agregar y eliminar marcas de agua
- security: Encriptación y desencriptación
- transform: Rotar, reordenar, combinar y extraer páginas
- conversion: Conversión entre PDFs e imágenes, redacción
- pipeline: Pipeline para encadenar operaciones PDF
"""

# Importar módulos usando import relativo
from . import info
from . import watermarks
from . import security
from . import transform
from . import conversion
from . import watermark_removal
from . import pipeline

# Exportar funciones principales para acceso directo
# Info
get_pdf_info = info.get_pdf_info
check_pdf_encrypted = info.check_pdf_encrypted

# Watermarks
add_text_watermark = watermarks.add_text_watermark
add_image_watermark = watermarks.add_image_watermark
remove_annotations = watermarks.remove_annotations
remove_watermarks = watermarks.remove_watermarks  # Alias

# Security
encrypt_pdf = security.encrypt_pdf
decrypt_pdf = security.decrypt_pdf

# Transform
rotate_pages = transform.rotate_pages
reorder_pages = transform.reorder_pages
merge_pdfs = transform.merge_pdfs
extract_pages = transform.extract_pages
extract_page = transform.extract_page
extract_range = transform.extract_range
reorder_pages_advanced = transform.reorder_pages_advanced
validate_page_number = transform.validate_page_number
validate_page_range = transform.validate_page_range
validate_new_order = transform.validate_new_order

# Conversion
images_to_pdf = conversion.images_to_pdf
pdf_to_images = conversion.pdf_to_images
redact_area = conversion.redact_area

# Watermark Removal (Fitz)
remove_watermark = watermark_removal.remove_watermark
check_fitz = watermark_removal.check_fitz

# Pipeline
PDFPipeline = pipeline.PDFPipeline
create_pipeline = pipeline.create_pipeline
execute_pipeline_operations = pipeline.execute_pipeline_operations

__all__ = [
    # Info
    'get_pdf_info',
    'check_pdf_encrypted',
    # Watermarks
    'add_text_watermark',
    'add_image_watermark',
    'remove_annotations',
    'remove_watermarks',
    # Security
    'encrypt_pdf',
    'decrypt_pdf',
    # Transform
    'rotate_pages',
    'reorder_pages',
    'merge_pdfs',
    'extract_pages',
    'extract_page',
    'extract_range',
    'reorder_pages_advanced',
    'validate_page_number',
    'validate_page_range',
    'validate_new_order',
    # Conversion
    'images_to_pdf',
    'pdf_to_images',
    'redact_area',
    # Watermark Removal
    'remove_watermark',
    'check_fitz',
    # Pipeline
    'PDFPipeline',
    'create_pipeline',
    'execute_pipeline_operations',
]