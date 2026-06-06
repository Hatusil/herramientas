"""Bubblelines tab for Text Analyzer UI."""
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Optional

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class BubblelinesTab(BaseTab):
    """Tab displaying Bubblelines visualization (lines with bubbles)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize BubblelinesTab."""
        self._image_label: ctk.CTkLabel | None = None
        self._current_image_data: Optional[bytes] = None
        self._terms_entry: ctk.CTkEntry | None = None
        self._show_bubbles: ctk.BooleanVar = ctk.BooleanVar(value=True)
        self._scale_slider: ctk.CTkSlider | None = None
        self._scale_label: ctk.CTkLabel | None = None
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

        # Row 1: terms entry
        terms_row = ctk.CTkFrame(controls)
        terms_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(terms_row, text="Términos:", width=80, anchor="w").pack(side="left", padx=5)

        self._terms_entry = ctk.CTkEntry(terms_row, placeholder_text="palabra1, palabra2, palabra3")
        self._terms_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Row 2: show_bubbles checkbox
        options_row = ctk.CTkFrame(controls)
        options_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(options_row, text="Opciones:", width=80, anchor="w").pack(side="left", padx=5)

        ctk.CTkCheckBox(options_row, text="Mostrar burbujas", variable=self._show_bubbles).pack(side="left", padx=5)

        # Row 3: bubble_scale slider
        scale_row = ctk.CTkFrame(controls)
        scale_row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(scale_row, text="Escala:", width=80, anchor="w").pack(side="left", padx=5)

        self._scale_slider = ctk.CTkSlider(
            scale_row,
            from_=0.5,
            to=3.0,
            number_of_steps=25,
            command=self._on_scale_change,
        )
        self._scale_slider.set(1.5)
        self._scale_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._scale_label = ctk.CTkLabel(scale_row, text="1.5", width=40)
        self._scale_label.pack(side="left", padx=5)

        # Generate button
        generate_btn = ctk.CTkButton(
            controls,
            text="Generar Bubblelines",
            command=self._run_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        generate_btn.pack(pady=10)

        # Image display area
        self._image_label = ctk.CTkLabel(
            self._frame,
            text="🫧 Bubblelines aparecerá aquí",
            text_color="gray",
        )
        self._image_label.pack(expand=True)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def on_tab_selected(self) -> None:
        """Re-render image when tab is selected."""
        if self._current_image_data:
            self._display_image(self._current_image_data)

    def _on_scale_change(self, value: float) -> None:
        """Handle bubble_scale slider change."""
        n = round(value, 1)
        self._scale_label.configure(text=str(n))

    def _run_analysis(self) -> None:
        """Run Bubblelines analysis."""
        if not self.state.cleaned_content:
            self.update_status("Cargue y analice el texto primero", "orange")
            return

        # Get terms from entry or auto-detect top 10
        terms_text = self._terms_entry.get().strip()
        if not terms_text:
            words = self.state.filter_pipeline.filtered_words
            if len(words) < 10:
                words = self.state.text_content.split()
            top_words = [
                w for w, _ in Counter(
                    w.lower() for w in words if w.isalpha()
                ).most_common(10)
            ]
            if not top_words:
                self.update_status("No hay suficientes palabras", "orange")
                return
            terms_list = top_words
            self._terms_entry.delete(0, tk.END)
            self._terms_entry.insert(0, ", ".join(top_words))
        else:
            terms_list = [t.strip() for t in terms_text.split(",") if t.strip()]
            if not terms_list:
                self.update_status("Ingrese términos válidos", "orange")
                return

        show_bubbles = self._show_bubbles.get()
        bubble_scale = round(self._scale_slider.get(), 1)

        try:
            from tools.text_tool.processor import analyze_bubblelines

            result = analyze_bubblelines(
                self.state.cleaned_content,
                terms_list=terms_list,
                show_bubbles=show_bubbles,
                bubble_scale=bubble_scale,
                already_cleaned=True,
            )

            if result.get("success") and result.get("image_data"):
                self._display_image(result["image_data"])
                self.update_status(f"Bubblelines generado: {len(terms_list)} términos", "green")
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
            text="🫧 Bubblelines aparecerá aquí",
        )
        self._current_image_data = None

    def _display_image(self, image_data: bytes) -> None:
        """Display Bubblelines image."""
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
                "title": "Bubblelines"
            })