"""Handlers module for PDF tool UI."""
from __future__ import annotations

from tools.pdf_tool.ui.handlers.info_handler import get_pdf_info, get_page_count
from tools.pdf_tool.ui.handlers.watermark_handler import (
    apply_text_watermark,
    apply_image_watermark,
    remove_watermark,
)
from tools.pdf_tool.ui.handlers.transform_handler import rotate_pages, reorder_pages
from tools.pdf_tool.ui.handlers.security_handler import encrypt_pdf, decrypt_pdf
from tools.pdf_tool.ui.handlers.combine_handler import merge_pdfs, extract_pages, extract_range
from tools.pdf_tool.ui.handlers.optimize_handler import compress_pdf, clean_metadata
from tools.pdf_tool.ui.handlers.numbers_handler import add_page_numbers
from tools.pdf_tool.ui.handlers.edit_handler import add_annotation, redact_area
from tools.pdf_tool.ui.handlers.pipeline_handler import execute_pipeline

__all__ = [
    "get_pdf_info",
    "get_page_count",
    "apply_text_watermark",
    "apply_image_watermark",
    "remove_watermark",
    "rotate_pages",
    "reorder_pages",
    "encrypt_pdf",
    "decrypt_pdf",
    "merge_pdfs",
    "extract_pages",
    "extract_range",
    "compress_pdf",
    "clean_metadata",
    "add_page_numbers",
    "add_annotation",
    "redact_area",
    "execute_pipeline",
]
