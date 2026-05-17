"""Modal export utilities for ChartModal."""
import logging
from datetime import datetime
from io import BytesIO
from tkinter import filedialog

from PIL import Image

logger = logging.getLogger(__name__)


def export_png(image_data: bytes, full_image, title: str, on_status) -> None:
    """Export chart as PNG (300 DPI)."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{title.lower().replace(' ', '_')}_{timestamp}"

        filename = filedialog.asksaveasfilename(
            title="Guardar imagen PNG",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("All files", "*.*")],
            initialfile=f"{default_name}.png"
        )

        if not filename:
            return

        img = full_image if full_image else Image.open(BytesIO(image_data))
        img.save(filename, "PNG", dpi=(300, 300))
        on_status(f"✅ PNG guardado: {filename}", "green")

    except Exception as e:
        logger.error(f"Error exporting PNG: {e}")
        on_status(f"❌ Error al guardar PNG: {e}", "red")


def export_pdf(image_data: bytes, full_image, title: str, on_status) -> None:
    """Export chart as PDF (vector)."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        import numpy as np

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{title.lower().replace(' ', '_')}_{timestamp}"

        filename = filedialog.asksaveasfilename(
            title="Guardar como PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{default_name}.pdf"
        )

        if not filename:
            return

        img = full_image if full_image else Image.open(BytesIO(image_data))
        img_array = np.array(img)

        with PdfPages(filename) as pdf:
            fig = plt.figure(figsize=(10, 8))
            plt.imshow(img_array, aspect='auto')
            plt.axis('off')
            plt.tight_layout(pad=0)
            pdf.savefig(fig, bbox_inches='tight', dpi=300)
            plt.close(fig)

        on_status(f"✅ PDF guardado: {filename}", "green")

    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        on_status(f"❌ Error al guardar PDF: {e}", "red")