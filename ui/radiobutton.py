"""
Wrapper para widgets de Tk no disponibles en customtkinter (CTk).

CTk no tiene RadioButton nativo, usamos tk.Radiobutton con soporte para
los kwargs más comunes para mantener consistencia visual con el tema CTk.
"""
import tkinter as tk


def RadioButton(parent, **kwargs):
    """
    Wrapper para tk.Radiobutton ya que CTk no tiene RadioButton nativo.
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos para tk.Radiobutton:
            - text: Texto del radio button
            - variable: StringVar/IntVar para grupo de radios
            - value: Valor asociado a este radio
            - font: Fuente (tk.Font o tuple)
            - fg: Color del texto
            - bg: Color de fondo
            - activeforeground: Color cuando está activo
            - activebackground: Color de fondo cuando está activo
            - selectcolor: Color del indicador
            - indicatoron: Si True muestra indicador (default True)
            - command: Callback al seleccionar
            - state: 'normal', 'disabled', o 'active'
            - width: Ancho del widget
            - height: Alto del widget
            - anchor: Posición del texto ('n', 's', 'e', 'w', etc.)
            - justify: Alineación del texto ('left', 'center', 'right')
            - padx, pady: Padding interno
            - relief: Estilo del borde ('flat', 'raised', 'sunken', etc.)
            - bd: Ancho del borde
    
    Returns:
        tk.Radiobutton widget
    """
    return tk.Radiobutton(parent, **kwargs)