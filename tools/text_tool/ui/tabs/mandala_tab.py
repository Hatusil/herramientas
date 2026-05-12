"""Mandala tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class MandalaTab(BaseTab):
    """Tab displaying Mandala visualization (concentric rings)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize MandalaTab."""
        self._image_label: ctk.CTkLabel | None = None
        self._current_image_data: Optional[bytes] = None
        self._terms_slider: ctk.CTkSlider | None = None
        self._terms_label: ctk.CTkLabel | None = None
        self._rings_slider: ctk.CTkSlider | None = None
        self._rings_label: ctk.CTkLabel | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Controls frame
        controls = ctk.CTkFrame(self._frame)
        controls.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            controls, text="Parámetros:", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Row 1: n_terms slider
        terms_row = ctk.CTkFrame(controls)
        terms_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(terms_row, text="Términos:", width=80, anchor="w").pack(side="left", padx=5)

        self._terms_slider = ctk.CTkSlider(
            terms_row,
            from_=5,
            to=15,
            number_of_steps=10,
            command=self._on_terms_change,
        )
        self._terms_slider.set(12)
        self._terms_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._terms_label = ctk.CTkLabel(terms_row, text="12", width=40)
        self._terms_label.pack(side="left", padx=5)

        # Row 2: n_rings slider
        rings_row = ctk.CTkFrame(controls)
        rings_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(rings_row, text="Anillos:", width=80, anchor="w").pack(side="left", padx=5)

        self._rings_slider = ctk.CTkSlider(
            rings_row,
            from_=2,
            to=6,
            number_of_steps=4,
            command=self._on_rings_change,
        )
        self._rings_slider.set(3)
        self._rings_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._rings_label = ctk.CTkLabel(rings_row, text="3", width=40)
        self._rings_label.pack(side="left", padx=5)

        # Generate button
        generate_btn = ctk.CTkButton(
            controls,
            text="Generar Mandala",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        generate_btn.pack(pady=10)

        # Image display area
        self._image_label = ctk.CTkLabel(
            self._frame,
            text="⭕ Mandala aparecerá aquí",
            text_color="gray",
        )
        self._image_label.pack(expand=True)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_terms_change(self, value: float) -> None:
        """Handle n_terms slider change."""
        n = int(value)
        self._terms_label.configure(text=str(n))

    def _on_rings_change(self, value: float) -> None:
        """Handle n_rings slider change."""
        n = int(value)
        self._rings_label.configure(text=str(n))

    def _run_analysis(self) -> None:
        """Run Mandala analysis."""
        if not self.state.cleaned_content:
            self.update_status("Cargue y analice el texto primero", "orange")
            return

        n_terms = int(self._terms_slider.get())
        n_rings = int(self._rings_slider.get())

        try:
            from tools.text_tool.processor import analyze_mandala

            self.update_status("🔄 Generando mandala...", "blue")
            self._parent.update()

            result = analyze_mandala(self.state.cleaned_content, n_terms=n_terms, n_rings=n_rings)

            if result.get("success") and result.get("image_data"):
                self._display_image(result["image_data"])
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def refresh(self) -> None:
        """Update display when text changes."""
        if not self.state.cleaned_content:
            self._reset_display()
            return

        # Auto-run if enough text (100+ words)
        if len(self.state.cleaned_content.split()) >= 100:
            self._run_analysis()

    def _reset_display(self) -> None:
        """Reset display to placeholder."""
        self._image_label.configure(
            image=None,
            text="⭕ Mandala aparecerá aquí",
        )
        self._current_image_data = None

    def _display_image(self, image_data: bytes) -> None:
        """Display Mandala image."""
        try:
            from PIL import Image
            from io import BytesIO

            img = Image.open(BytesIO(image_data))
            img.thumbnail((500, 500))

            if img.mode != "RGBA":
                img = img.convert("RGBA")

            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size,
            )

            self._image_label.configure(image=ctk_img, text="")
            self._image_label.image = ctk_img
            self._current_image_data = image_data
            self._bind_click_handler()

        except Exception as e:
            self._image_label.configure(text=f"Error: {e}")

    def _bind_click_handler(self) -> None:
        """Bind click to open modal."""
        self._image_label.unbind("<Button-1>")
        self._image_label.bind("<Button-1>", self._open_modal)
        self._image_label.configure(cursor="hand2")

    def _open_modal(self, event) -> None:
        """Open chart in modal."""
        if self._current_image_data:
            self._callbacks.request_analysis("open_modal", {
                "image_data": self._current_image_data,
                "title": "Mandala"
            })