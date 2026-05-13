"""Results view panel for Search Tool UI."""
from __future__ import annotations

import logging
import csv
from pathlib import Path
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from tkinter import filedialog

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.search_tool.ui.state import SearchState
    from tools.search_tool.ui.callbacks import SearchCallbacks

logger = logging.getLogger(__name__)


class ResultsView:
    """Panel for displaying search results."""

    def __init__(
        self,
        ui: "SearchToolUIBase",
        parent_frame: ctk.CTkFrame,
    ) -> None:
        """Initialize results view panel.

        Args:
            ui: Parent UI instance.
            parent_frame: Parent frame to contain this panel.
        """
        self._ui = ui
        self._parent = parent_frame
        self._frame: Optional[ctk.CTkFrame] = None
        self._textbox: Optional[ctk.CTkTextbox] = None
        self._results: List[Dict[str, Any]] = []
        self._selected_indices: List[int] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the results view UI."""
        self._frame = ctk.CTkFrame(self._parent)
        self._frame.pack(fill="both", expand=True, padx=10, pady=5)

        title = ctk.CTkLabel(
            self._frame,
            text="📋 Resultados",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        self._textbox = ctk.CTkTextbox(
            self._frame,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self._textbox.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        export_csv_btn = ctk.CTkButton(
            btn_frame,
            text="Exportar CSV",
            command=self._export_csv,
            width=120,
        )
        export_csv_btn.pack(side="left", padx=(0, 10))

        export_txt_btn = ctk.CTkButton(
            btn_frame,
            text="Exportar TXT",
            command=self._export_txt,
            width=120,
        )
        export_txt_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Limpiar",
            command=self.clear,
            width=80,
        )
        clear_btn.pack(side="right")

    def display_results(self, results: List[Dict[str, Any]]) -> None:
        """Display search results.

        Args:
            results: List of result dictionaries.
        """
        self._results = results
        self._textbox.delete("1.0", "end")

        if not results:
            self._textbox.insert("1.0", "No se encontraron resultados.")
            return

        for idx, result in enumerate(results, 1):
            path = result.get("path", "Unknown")
            line = result.get("line", "")
            text = result.get("text", "")

            line_content = f"{idx}. {path}"
            if line:
                line_content += f":{line}"
            if text:
                line_content += f"\n   {text[:200]}"
            line_content += "\n\n"

            self._textbox.insert("end", line_content)

        logger.info(f"Displayed {len(results)} results")

    def get_selected(self) -> List[Dict[str, Any]]:
        """Get selected results.

        Returns:
            List of selected result dictionaries.
        """
        if self._selected_indices:
            return [self._results[i] for i in self._selected_indices if i < len(self._results)]
        return list(self._results)

    def clear(self) -> None:
        """Clear results."""
        self._results = []
        self._selected_indices = []
        self._textbox.delete("1.0", "end")

    def _export_csv(self) -> None:
        """Export results to CSV file."""
        if not self._results:
            logger.warning("No results to export")
            return

        file_path = filedialog.asksaveasfilename(
            title="Guardar CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["path", "line", "text"])
                writer.writeheader()
                writer.writerows(self._results)
            logger.info(f"Exported {len(self._results)} results to CSV: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")

    def _export_txt(self) -> None:
        """Export results to TXT file."""
        if not self._results:
            logger.warning("No results to export")
            return

        file_path = filedialog.asksaveasfilename(
            title="Guardar TXT",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for result in self._results:
                    path = result.get("path", "Unknown")
                    line = result.get("line", "")
                    text = result.get("text", "")

                    f.write(f"Path: {path}")
                    if line:
                        f.write(f":{line}")
                    if text:
                        f.write(f"\n  {text}")
                    f.write("\n\n")
            logger.info(f"Exported {len(self._results)} results to TXT: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting TXT: {e}")

    def get_frame(self) -> ctk.CTkFrame:
        """Get the main frame.

        Returns:
            The panel frame.
        """
        return self._frame