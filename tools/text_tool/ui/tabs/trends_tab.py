"""Trends tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

from tools.text_tool.ui.tabs.base_tab import BaseTab
from core.constants import COLORS

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class TrendsTab(BaseTab):
    """Tab displaying trends visualization (frequency by sections)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize TrendsTab."""
        self._image_label: ctk.CTkLabel | None = None
        self._current_image_data: Optional[bytes] = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Generate button (fallback if auto fails)
        ctk.CTkButton(
            self._frame,
            text="\U0001f4ca Generar Tendencias",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))

        # Image display area
        self._image_label = ctk.CTkLabel(
            self._frame,
            text="📊 Tendencias aparecerá aquí\nEjecute análisis primero",
            text_color="gray",
        )
        self._image_label.pack(expand=True, padx=10, pady=10)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def on_tab_selected(self) -> None:
        """Re-render image when tab is selected (fix for hidden tab rendering)."""
        if self._current_image_data:
            self._display_image(self._current_image_data)

    def _run_analysis(self) -> None:
        """Run trends analysis and display result."""
        text = self.state.cleaned_content or self.state.text_content
        if not text:
            self.update_status("Primero cargá texto", "orange")
            return

        try:
            from tools.text_tool.processor import analyze_trends

            self.update_status("🔄 Generando tendencias...", "blue")
            result = analyze_trends(
                text,
                already_cleaned=bool(self.state.cleaned_content),
            )
            if result.get("success") and result.get("image_data"):
                self._display_image(result["image_data"])
                self.update_status("✅ Tendencias generadas", "green")
            else:
                self.update_status(result.get("error", "Error en tendencias"), "orange")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def refresh(self) -> None:
        """Update trends when text changes."""
        if not self.state.cleaned_content:
            self._reset_display()
            return
        self._run_analysis()

    def _reset_display(self) -> None:
        """Reset display to placeholder."""
        self._image_label.configure(
            image=None,
            text="📊 Tendencias aparecerá aquí\nEjecute análisis primero",
        )
        self._current_image_data = None

    def _display_image(self, image_data: bytes) -> None:
        """Display trends image."""
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
                "title": "Tendencias"
            })