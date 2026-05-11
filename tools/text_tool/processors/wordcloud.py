"""
WordCloud Analyzer - Generación de nubes de palabras.

Funciones:
- analyze_wordcloud: genera WordCloud con opciones de personalización
- _generate_shape_mask: helper para generar máscaras de formas
"""

import logging
from typing import Dict, Any, Optional
from io import BytesIO

from core.utils import clean_text

logger = logging.getLogger(__name__)

# Check availability
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False


def _generate_shape_mask(shape: str, width: int, height: int) -> Optional[Any]:
    """
    Generate mask for WordCloud shapes.

    Args:
        shape: Shape name - 'rectangle', 'circle', 'heart', 'star'
        width: Width in pixels
        height: Height in pixels

    Returns:
        PIL Image mask or None for rectangle
    """
    try:
        import numpy as np
        from PIL import Image, ImageDraw

        shape = shape.lower() if shape else 'rectangle'

        if shape == 'rectangle' or shape == 'rectángulo':
            return None

        elif shape == 'circle' or shape == 'círculo':
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2 - 5

            y, x = np.ogrid[:height, :width]
            mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2
            return (1 - mask.astype(np.uint8)) * 255

        elif shape == 'heart' or shape == 'corazón':
            y, x = np.ogrid[:height, :width]
            center_x = width // 2
            scale_x = width / 100
            scale_y = height / 100

            x_norm = (x - center_x) / scale_x
            y_norm = (y - height * 0.4) / scale_y

            left_circle = ((x_norm + 30) ** 2 + y_norm ** 2) <= 900
            right_circle = ((x_norm - 30) ** 2 + y_norm ** 2) <= 900
            triangle = (y_norm >= -50) & (y_norm <= 30) & (np.abs(x_norm) <= (30 - y_norm / 2))

            mask = (left_circle | right_circle | triangle).astype(np.uint8)
            return (1 - mask) * 255

        elif shape == 'star' or shape == 'estrella':
            center_x, center_y = width // 2, height // 2
            outer_radius = min(width, height) // 2 - 5
            inner_radius = outer_radius * 0.4

            angles = np.linspace(-np.pi/2, -np.pi/2 + 2 * np.pi, 10, endpoint=False)

            points = []
            for i, angle in enumerate(angles):
                r = outer_radius if i % 2 == 0 else inner_radius
                px = center_x + r * np.cos(angle)
                py = center_y + r * np.sin(angle)
                points.append([px, py])

            mask_img = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask_img)
            draw.polygon([(p[0], p[1]) for p in points], fill=255)

            mask_array = np.array(mask_img)
            return (255 - mask_array)

        return None

    except Exception as e:
        logger.warning(f"Could not generate shape mask '{shape}': {e}")
        return None


def analyze_wordcloud(
    text: str,
    n_words: int = 100,
    width: int = 800,
    height: int = 400,
    colormap: str = 'viridis',
    margin: int = 10,
    shape: str = 'rectangle'
) -> Dict[str, Any]:
    """
    Genera una WordCloud con opciones de personalización.

    Args:
        text: Texto de entrada
        n_words: Número máximo de palabras (default: 100)
        width: Ancho en píxeles (default: 800)
        height: Alto en píxeles (default: 400)
        colormap: Nombre del colormap de matplotlib
        margin: Margen entre palabras
        shape: Forma de la máscara

    Returns:
        Dict con 'success', 'image_data' (bytes), 'message'
    """
    if not WORDCLOUD_AVAILABLE:
        return {'success': False, 'error': 'wordcloud no instalado'}

    try:
        # Validate colormap
        colormap_map = {
            'viridis': 'viridis', 'plasma': 'plasma', 'inferno': 'inferno',
            'magma': 'magma', 'cividis': 'cividis', 'blues': 'Blues',
            'greens': 'Greens', 'reds': 'Reds', 'oranges': 'Oranges',
            'purples': 'Purples', 'coolwarm': 'coolwarm', 'rdygn': 'RdYlGn',
            'seismic': 'seismic', 'terrain': 'terrain', 'ocean': 'ocean'
        }
        if colormap.lower() in colormap_map:
            colormap = colormap_map[colormap.lower()]
        else:
            logger.warning(f"Invalid colormap '{colormap}', falling back to 'viridis'")
            colormap = 'viridis'

        cleaned = clean_text(text, remove_stopwords=True)
        mask = _generate_shape_mask(shape, width, height)

        wc_kwargs = {
            'width': width,
            'height': height,
            'background_color': 'white',
            'max_words': n_words,
            'colormap': colormap,
            'prefer_horizontal': 0.7,
            'margin': margin
        }

        if mask is not None:
            wc_kwargs['mask'] = mask

        wc = WordCloud(**wc_kwargs)
        wc.generate(cleaned)

        img_buffer = BytesIO()
        wc.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return {
            'success': True,
            'image_data': img_buffer.getvalue(),
            'message': f'WordCloud con {n_words} palabras'
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}