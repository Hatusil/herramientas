"""Chart Modal component for expanded chart view with export."""
import logging
from typing import Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from core.constants import COLORS

logger = logging.getLogger(__name__)


class ChartModal(ctk.CTkToplevel):
    """Modal for expanded chart view with export capabilities.

    Displays an image with zoom (scroll), pan (drag), and export (PNG/PDF).
    Uses callbacks instead of direct attribute access for better decoupling.

    Args:
        parent: Parent widget (CTkTabview or CTkFrame)
        image_data: PNG image bytes
        title: Title for the modal window
        on_status: Callback function(message, color) for status updates
    """

    def __init__(
        self,
        parent,
        image_data: bytes,
        title: str,
        on_status: Callable[[str, str], None]
    ):
        super().__init__(parent)

        self.image_data = image_data
        self.title_text = title
        self.on_status = on_status or (lambda *_: None)
        self._current_width = 800
        self._current_height = 600
        self.zoom_level = 1.0

        # Configure modal window
        self.title(f"📊 {title}")

        # Set minimum size 600x600, start at 800x600
        self.minsize(600, 600)
        self.geometry("800x600")
        self._current_width = 800
        self._current_height = 600

        # Center on screen
        self._center_window()

        # Make modal transient (stays on top of parent)
        self.transient(parent)

        # Grab focus
        self.grab_set()

        # Setup UI
        self._setup_ui()

        # Bind Escape key to close
        self.bind("<Escape>", lambda e: self.destroy())

        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # -------------------------------------------------------------------------
    # Scroll / Zoom
    # -------------------------------------------------------------------------

    def _on_scroll(self, event) -> str:
        """Handle scroll events - zoom only (Linux + Windows)."""
        try:
            from PIL import Image, ImageTk

            # Cross-platform: Linux uses event.num (Button-4/Button-5),
            # Windows uses event.delta (MouseWheel)
            if hasattr(event, 'num') and event.num in (4, 5):
                if event.num == 4:
                    self.zoom_level *= 1.2  # Zoom in
                else:
                    self.zoom_level *= 0.8  # Zoom out
            elif hasattr(event, 'delta') and event.delta != 0:
                if event.delta > 0:
                    self.zoom_level *= 1.2
                else:
                    self.zoom_level *= 0.8
            else:
                return "break"

            # Limit zoom range (0.5x to 5x)
            self.zoom_level = max(0.5, min(5.0, self.zoom_level))

            # Get original image and apply zoom
            if hasattr(self, 'full_image') and self.full_image:
                orig_width, orig_height = self.full_image.size
                new_width = int(orig_width * self.zoom_level)
                new_height = int(orig_height * self.zoom_level)
                img_display = self.full_image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )
                self.photo_img = ImageTk.PhotoImage(img_display)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
                self.canvas.configure(scrollregion=(0, 0, new_width, new_height))

        except Exception as e:
            logger.error(f"Zoom error: {e}")

        return "break"

    # -------------------------------------------------------------------------
    # Drag / Pan
    # -------------------------------------------------------------------------

    def _on_drag_start(self, event) -> None:
        """Start drag for panning."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event) -> None:
        """Pan the canvas during drag - smooth movement."""
        if hasattr(self, '_drag_start_x'):
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            self.canvas.move("all", dx, dy)
            self._drag_start_x = event.x
            self._drag_start_y = event.y

    def _on_drag_release(self, event) -> None:
        """End drag."""
        if hasattr(self, '_drag_start_x'):
            del self._drag_start_x
            del self._drag_start_y

    # -------------------------------------------------------------------------
    # Window Management
    # -------------------------------------------------------------------------

    def _center_window(self) -> None:
        """Center the modal on screen."""
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        modal_width = max(self.winfo_width(), self._current_width)
        modal_height = max(self.winfo_height(), self._current_height)

        x = (screen_width - modal_width) // 2
        y = max(50, (screen_height - modal_height) // 2)

        self.geometry(f"{modal_width}x{modal_height}+{x}+{y}")

    # -------------------------------------------------------------------------
    # UI Setup
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Setup modal UI components."""

        # Title bar frame
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        title_label = ctk.CTkLabel(
            title_frame,
            text=f"📊 {self.title_text}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=5)

        hint_label = ctk.CTkLabel(
            title_frame,
            text="(Scroll = zoom, arrastrar = mover)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        hint_label.pack(side="left", padx=10)

        # Image container
        img_container = ctk.CTkFrame(self)
        img_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas_frame = ctk.CTkFrame(img_container, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame, bg=COLORS["bg_light"], highlightthickness=0, takefocus=True
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbars
        v_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, command=self.canvas.yview, orientation="vertical"
        )
        v_scrollbar.pack(side="right", fill="y")

        h_scrollbar = ctk.CTkScrollbar(
            self, command=self.canvas.xview, orientation="horizontal"
        )
        h_scrollbar.pack(fill="x")

        self.canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Bind scroll events - zoom
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", self._on_scroll)
        self.canvas.bind("<Button-5>", self._on_scroll)
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Button-4>", self._on_scroll)
        self.bind("<Button-5>", self._on_scroll)

        # Bind drag events for panning
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_release)
        self.canvas.configure(cursor="hand2")

        self.canvas.focus_set()

        # Display image
        self._display_image()

        # Export buttons
        self._setup_export_buttons()

    def _display_image(self) -> None:
        """Display the image on canvas."""
        try:
            from PIL import Image, ImageTk
            from io import BytesIO

            if not isinstance(self.image_data, (bytes, bytearray)):
                raise ValueError(
                    f"image_data debe ser bytes, recibido: {type(self.image_data)}"
                )

            if len(self.image_data) == 0:
                raise ValueError("image_data está vacío")

            img = Image.open(BytesIO(self.image_data))
            orig_width, orig_height = img.size

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            max_width = min(orig_width, int(screen_width * 0.9))
            max_height = min(orig_height, int(screen_height * 0.8))

            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            ratio = min(width_ratio, height_ratio, 1)

            display_width = int(orig_width * ratio)
            display_height = int(orig_height * ratio)

            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            img_display = img.resize(
                (display_width, display_height), Image.Resampling.LANCZOS
            )

            self.photo_img = ImageTk.PhotoImage(img_display)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.full_image = img

        except Exception as e:
            logger.error(f"Error displaying image in modal: {e}")
            error_label = ctk.CTkLabel(
                self.canvas_frame,
                text=f"Error al cargar imagen: {e}",
                text_color="red"
            )
            error_label.pack()

    def _setup_export_buttons(self) -> None:
        """Setup export buttons at bottom of modal."""
        export_frame = ctk.CTkFrame(self)
        export_frame.pack(fill="x", padx=10, pady=(5, 10))

        export_label = ctk.CTkLabel(
            export_frame,
            text="Exportar:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        export_label.pack(side="left", padx=10)

        png_btn = ctk.CTkButton(
            export_frame,
            text="💾 PNG",
            command=self._export_png,
            width=100
        )
        png_btn.pack(side="left", padx=5, pady=5)

        pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 PDF",
            command=self._export_pdf,
            width=100
        )
        pdf_btn.pack(side="left", padx=5, pady=5)

        close_btn = ctk.CTkButton(
            export_frame,
            text="✕ Cerrar",
            command=self.destroy,
            width=100,
            fg_color=COLORS["error"],
            hover_color=COLORS["error"],
        )
        close_btn.pack(side="right", padx=10, pady=5)

    # -------------------------------------------------------------------------
    # Export Methods
    # -------------------------------------------------------------------------

    def _export_png(self) -> None:
        """Export chart as PNG (300 DPI)."""
        try:
            from datetime import datetime
            from PIL import Image
            from io import BytesIO

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{self.title_text.lower().replace(' ', '_')}_{timestamp}"

            filename = filedialog.asksaveasfilename(
                title="Guardar imagen PNG",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("All files", "*.*")],
                initialfile=f"{default_name}.png"
            )

            if not filename:
                return

            if hasattr(self, 'full_image'):
                img = self.full_image
            else:
                img = Image.open(BytesIO(self.image_data))

            img.save(filename, "PNG", dpi=(300, 300))
            self.on_status(f"✅ PNG guardado: {filename}", "green")

        except Exception as e:
            logger.error(f"Error exporting PNG: {e}")
            self.on_status(f"❌ Error al guardar PNG: {e}", "red")

    def _export_pdf(self) -> None:
        """Export chart as PDF (vector)."""
        try:
            from datetime import datetime
            from PIL import Image
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
            import numpy as np
            from io import BytesIO

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{self.title_text.lower().replace(' ', '_')}_{timestamp}"

            filename = filedialog.asksaveasfilename(
                title="Guardar como PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
                initialfile=f"{default_name}.pdf"
            )

            if not filename:
                return

            if hasattr(self, 'full_image'):
                img = self.full_image
            else:
                img = Image.open(BytesIO(self.image_data))

            img_array = np.array(img)

            with PdfPages(filename) as pdf:
                fig = plt.figure(figsize=(10, 8))
                plt.imshow(img_array, aspect='auto')
                plt.axis('off')
                plt.tight_layout(pad=0)
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
                plt.close(fig)

            self.on_status(f"✅ PDF guardado: {filename}", "green")

        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            self.on_status(f"❌ Error al guardar PDF: {e}", "red")