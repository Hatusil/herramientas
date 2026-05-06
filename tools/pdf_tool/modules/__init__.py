"""
PDF Tool Modules - Módulos especializados para procesamiento de PDFs.

Este paquete contiene módulos separados para diferentes funcionalidades de PDF:
- info: Información y metadatos de PDFs
- watermarks: Agregar y eliminar marcas de agua
- security: Encriptación y desencriptación
- transform: Rotar, reordenar, combinar y extraer páginas
- conversion: Conversión entre PDFs e imágenes, redacción
"""

# Importar módulos directamente (evitar imports que carguen el paquete padre)
import info
import watermarks
import security
import transform
import conversion
import watermark_removal

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

# Conversion
images_to_pdf = conversion.images_to_pdf
pdf_to_images = conversion.pdf_to_images
redact_area = conversion.redact_area

# Watermark Removal (Fitz)
remove_watermark = watermark_removal.remove_watermark
check_fitz = watermark_removal.check_fitz

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
    # Conversion
    'images_to_pdf',
    'pdf_to_images',
    'redact_area',
    # Watermark Removal
    'remove_watermark',
    'check_fitz',
]