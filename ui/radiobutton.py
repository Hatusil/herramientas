"""
Utilidades para la UI - wrapper para widgets no disponibles en customtkinter.
"""
import tkinter as tk

def RadioButton(parent, **kwargs):
    """Wrapper para RadioButton ya que CTk no lo tiene."""
    return tk.Radiobutton(parent, **kwargs)