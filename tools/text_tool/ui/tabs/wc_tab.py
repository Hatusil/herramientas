"""WordCloud tab for Text Analyzer UI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk

from tools.text_tool.ui.tabs.base_tab import BaseTab

if TYPE_CHECKING:
    from tools.text_tool.ui.state import TextAnalyzerState
    from tools.text_tool.ui.callbacks import AppCallbacks


class WCTab(BaseTab):
    """Tab displaying word cloud visualization with customization options."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        state: TextAnalyzerState,
        callbacks: AppCallbacks,
    ) -> None:
        """Initialize WCTab."""
        self._count_slider: ctk.CTkSlider | None = None
        self._count_label: ctk.CTkLabel | None = None
        self._colormap: ctk.CTkComboBox | None = None
        self._margin_slider: ctk.CTkSlider | None = None
        self._margin_label: ctk.CTkLabel | None = None
        self._shape: ctk.CTkComboBox | None = None
        self._exclude_entry: ctk.CTkEntry | None = None
        self._wc_label: ctk.CTkLabel | None = None
        super().__init__(parent, state, callbacks)

    def _setup_frame(self) -> None:
        """Create the main frame for this tab."""
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")

        # Customization controls
        customize_frame = ctk.CTkFrame(self._frame)
        customize_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            customize_frame,
            text="Personalización:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Word count slider
        self._add_count_slider(customize_frame)
        # Colormap dropdown
        self._add_colormap_dropdown(customize_frame)
        # Margin slider
        self._add_margin_slider(customize_frame)
        # Shape selector
        self._add_shape_selector(customize_frame)
        # Exclude words entry
        self._add_exclude_entry(customize_frame)
        # Generate button
        self._add_generate_button(customize_frame)

        # WordCloud display area
        self._wc_label = ctk.CTkLabel(
            self._frame, text="WordCloud aparecerá aquí", text_color="gray"
        )
        self._wc_label.pack(expand=True)

    def _add_count_slider(self, parent: ctk.CTkFrame) -> None:
        """Add word count slider row."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(row, text="Palabras:", width=80, anchor="w").pack(side="left", padx=5)

        self._count_slider = ctk.CTkSlider(
            row, from_=50, to=200, number_of_steps=150, command=self._on_count_change
        )
        self._count_slider.set(100)
        self._count_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._count_label = ctk.CTkLabel(row, text="100", width=40)
        self._count_label.pack(side="left", padx=5)

    def _add_colormap_dropdown(self, parent: ctk.CTkFrame) -> None:
        """Add colormap dropdown row."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(row, text="Colormap:", width=80, anchor="w").pack(side="left", padx=5)

        self._colormap = ctk.CTkComboBox(
            row,
            values=[
                "viridis", "plasma", "inferno", "magma", "cividis",
                "blues", "greens", "reds", "oranges", "purples",
                "coolwarm", "RdYlGn", "seismic", "terrain", "ocean",
            ],
            state="readonly",
        )
        self._colormap.set("viridis")
        self._colormap.pack(side="left", fill="x", expand=True, padx=5)

    def _add_margin_slider(self, parent: ctk.CTkFrame) -> None:
        """Add margin slider row."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(row, text="Márgenes:", width=80, anchor="w").pack(side="left", padx=5)

        self._margin_slider = ctk.CTkSlider(
            row, from_=0, to=50, number_of_steps=50, command=self._on_margin_change
        )
        self._margin_slider.set(10)
        self._margin_slider.pack(side="left", fill="x", expand=True, padx=5)

        self._margin_label = ctk.CTkLabel(row, text="10px", width=40)
        self._margin_label.pack(side="left", padx=5)

    def _add_shape_selector(self, parent: ctk.CTkFrame) -> None:
        """Add shape selector dropdown."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(row, text="Forma:", width=80, anchor="w").pack(side="left", padx=5)

        self._shape = ctk.CTkComboBox(
            row, values=["rectangle", "circle", "heart", "star"], state="readonly"
        )
        self._shape.set("rectangle")
        self._shape.pack(side="left", fill="x", expand=True, padx=5)

    def _add_exclude_entry(self, parent: ctk.CTkFrame) -> None:
        """Add exclude words entry."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(row, text="Excluir:", width=80, anchor="w").pack(side="left", padx=5)

        self._exclude_entry = ctk.CTkEntry(row, placeholder_text="palabra1, palabra2, ...")
        self._exclude_entry.pack(side="left", fill="x", expand=True, padx=5)

    def _add_generate_button(self, parent: ctk.CTkFrame) -> None:
        """Add generate button."""
        btn = ctk.CTkButton(
            parent,
            text="Generar WordCloud",
            command=self._regenerate,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        btn.pack(pady=10)

    def get_frame(self) -> ctk.CTkFrame:
        """Return the main frame for this tab."""
        return self._frame

    def _on_count_change(self, value: float) -> None:
        """Handle word count slider change."""
        n = int(value)
        self._count_label.configure(text=str(n))

    def _on_margin_change(self, value: float) -> None:
        """Handle margin slider change."""
        m = int(value)
        self._margin_label.configure(text=f"{m}px")

    def refresh(self) -> None:
        """Generate initial wordcloud on tab selection."""
        if not self.state.cleaned_content:
            return
        self._regenerate()

    def _regenerate(self) -> None:
        """Regenerate wordcloud with current settings."""
        if not self.state.cleaned_content:
            self.update_status("Cargue y analice el texto primero", "orange")
            return

        n_words = int(self._count_slider.get()) if self._count_slider else 100
        colormap = self._colormap.get() if self._colormap else "viridis"
        margin = int(self._margin_slider.get()) if self._margin_slider else 10
        shape = self._shape.get() if self._shape else "rectangle"

        exclude_text = self._exclude_entry.get().strip() if self._exclude_entry else ""
        exclude_words = [w.strip().lower() for w in exclude_text.split(",")] if exclude_text else []

        try:
            from tools.text_tool.processor import analyze_wordcloud, clean_text

            cleaned = clean_text(
                self.state.text_content,
                remove_stopwords=True,
                exclude_words=exclude_words,
            )

            if not cleaned or not cleaned.strip():
                self.update_status("Texto vacío tras excluir palabras", "orange")
                return

            actual_words = len(cleaned.split())
            if n_words > actual_words:
                self.update_status(
                    f"Solo {actual_words} palabras disponibles", "orange"
                )

            result = analyze_wordcloud(
                cleaned, n_words=n_words, colormap=colormap, margin=margin, shape=shape
            )

            if result.get("success") and result.get("image_data"):
                self._show_wordcloud(result["image_data"])
                self.update_status(
                    f"WordCloud: {actual_words} palabras, {colormap}", "green"
                )
            else:
                self.update_status(result.get("error", "Error"), "red")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def _show_wordcloud(self, image_data: bytes) -> None:
        """Display wordcloud image."""
        try:
            from io import BytesIO

            from PIL import Image

            img = Image.open(BytesIO(image_data))
            img.thumbnail((570, 285))

            if img.mode != "RGBA":
                img = img.convert("RGBA")

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

            self._wc_label.configure(image=ctk_img, text="")
            self._wc_label.image = ctk_img
            self._wc_label.unbind("<Button-1>")
            self._wc_label.bind(
                "<Button-1>", lambda e: self._callbacks.open_chart_modal(image_data, "WordCloud")
            )
            self._wc_label.configure(cursor="hand2")
        except Exception as e:
            self._wc_label.configure(text=f"Error: {e}")
