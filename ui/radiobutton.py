"""
Wrapper legacy para tk.Radiobutton.

NOTA: CTk SI tiene CTkRadioButton nativo (desde versiones tempranas).
Este wrapper se mantiene por compatibilidad con tools existentes que
usan tk.Radiobutton directamente. Para tools nuevas, usar CTkRadioButton
o core.tool_builder.create_radiobutton().
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