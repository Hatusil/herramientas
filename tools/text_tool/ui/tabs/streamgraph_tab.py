"""StreamGraph tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class StreamGraphTab(BaseTab):
    """Tab displaying StreamGraph visualization (stacked area chart)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize StreamGraphTab."""
        self._image_label: ctk.CTkLabel | None = None
        self._current_image_data: Optional[bytes] = None
        self._terms_slider: ctk.CTkSlider | None = None
        self._terms_label: ctk.CTkLabel | None = None
        self._sections_slider: ctk.CTkSlider | None = None
        self._sections_label: ctk.CTkLabel | None = None
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
            to=12,
            number_of_steps=7,
            command=self._on_terms_change,
        )
        self._terms_slider.set(8)
        self._terms_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._terms_label = ctk.CTkLabel(terms_row, text="8", width=40)
        self._terms_label.pack(side="left", padx=5)

        # Row 2: n_sections slider
        sections_row = ctk.CTkFrame(controls)
        sections_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(sections_row, text="Secciones:", width=80, anchor="w").pack(side="left", padx=5)

        self._sections_slider = ctk.CTkSlider(
            sections_row,
            from_=5,
            to=20,
            number_of_steps=15,
            command=self._on_sections_change,
        )
        self._sections_slider.set(15)
        self._sections_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._sections_label = ctk.CTkLabel(sections_row, text="15", width=40)
        self._sections_label.pack(side="left", padx=5)

        # Generate button
        generate_btn = ctk.CTkButton(
            controls,
            text="Generar StreamGraph",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        generate_btn.pack(pady=10)

        # Image display area
        self._image_label = ctk.CTkLabel(
            self._frame,
            text="🌊 StreamGraph aparecerá aquí",
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

    def _on_sections_change(self, value: float) -> None:
        """Handle n_sections slider change."""
        n = int(value)
        self._sections_label.configure(text=str(n))

    def _run_analysis(self) -> None:
        """Run StreamGraph analysis."""
        if not self.state.cleaned_content:
            self.update_status("Cargue y analice el texto primero", "orange")
            return

        n_terms = int(self._terms_slider.get())
        n_sections = int(self._sections_slider.get())

        try:
            from tools.text_tool.processor import analyze_streamgraph

            result = analyze_streamgraph(self.state.cleaned_content, n_terms=n_terms, n_sections=n_sections)

            if result.get("success") and result.get("image_data"):
                self._display_image(result["image_data"])
                self.update_status(f"StreamGraph generado con {n_terms} términos", "green")
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def refresh(self) -> None:
        """Update display when text changes."""
        if not self.state.cleaned_content:
            self._reset_display()
            return

        # Auto-run if enough text (50+ words)
        if len(self.state.cleaned_content.split()) >= 50:
            self._run_analysis()

    def _reset_display(self) -> None:
        """Reset display to placeholder."""
        self._image_label.configure(
            image=None,
            text="🌊 StreamGraph aparecerá aquí",
        )
        self._current_image_data = None

    def _display_image(self, image_data: bytes) -> None:
        """Display StreamGraph image."""
        try:
            from PIL import Image
            from io import BytesIO

            img = Image.open(BytesIO(image_data))
            img.thumbnail((700, 350))

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
                "title": "StreamGraph"
            })