"""Folder selector panel for Search Tool UI."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional
from tkinter import filedialog

import customtkinter as ctk

if TYPE_CHECKING:
    from tools.search_tool.ui.state import SearchState
    from tools.search_tool.ui.callbacks import SearchCallbacks

logger = logging.getLogger(__name__)


class FolderSelector:
    """Panel for folder selection."""

    def __init__(
        self,
        ui: "SearchToolUIBase",
        parent_frame: ctk.CTkFrame,
    ) -> None:
        """Initialize folder selector panel.

        Args:
            ui: Parent UI instance.
            parent_frame: Parent frame to contain this panel.
        """
        self._ui = ui
        self._parent = parent_frame
        self._frame: Optional[ctk.CTkFrame] = None
        self._path_label: Optional[ctk.CTkLabel] = None
        self._selected_folder: str = ""
        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the folder selector UI."""
        self._frame = ctk.CTkFrame(self._parent)
        self._frame.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(
            self._frame,
            text="📁 Carpeta de búsqueda",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        btn_frame = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        select_btn = ctk.CTkButton(
            btn_frame,
            text="Seleccionar carpeta",
            command=self._on_select_folder,
            width=200,
        )
        select_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Limpiar",
            command=self._on_clear_folder,
            width=80,
        )
        clear_btn.pack(side="left")

        self._path_label = ctk.CTkLabel(
            self._frame,
            text="No hay carpeta seleccionada",
            text_color="gray",
            anchor="w",
            justify="left",
        )
        self._path_label.pack(fill="x", padx=10, pady=(5, 10))

    def _on_select_folder(self) -> None:
        """Handle folder selection."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de búsqueda")
        if folder:
            self.set_folder(folder)
            logger.info(f"Folder selected: {folder}")

    def _on_clear_folder(self) -> None:
        """Clear selected folder."""
        self.set_folder("")
        logger.info("Folder cleared")

    def get_selected_folder(self) -> str:
        """Get the selected folder path.

        Returns:
            Selected folder path or empty string.
        """
        return self._selected_folder

    def set_folder(self, path: str) -> None:
        """Set the selected folder.

        Args:
            path: Folder path to set.
        """
        self._selected_folder = path
        if path:
            self._path_label.configure(text=path, text_color="white")
        else:
            self._path_label.configure(text="No hay carpeta seleccionada", text_color="gray")

    def get_frame(self) -> ctk.CTkFrame:
        """Get the main frame.

        Returns:
            The panel frame.
        """
        return self._frame