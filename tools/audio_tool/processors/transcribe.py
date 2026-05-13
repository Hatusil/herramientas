"""
Transcribe - OCR de audio usando OLMoASR.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Cache del modelo OLMoASR
_olmoasr_model: Optional[Any] = None
_olmoasr_processor: Optional[Any] = None


def _get_model(model_size: str = "base"):
    """Carga o retorna modelo OLMoASR cacheado."""
    global _olmoasr_model, _olmoasr_processor

    if _olmoasr_model is None:
        try:
            from transformers import OlmoASRForConditionalGeneration, AutoProcessor
            logger.info(f"Cargando OLMoASR-{model_size}.en...")
            _olmoasr_model = OlmoASRForConditionalGeneration.from_pretrained(
                f"allenai/OLMoASR-{model_size}.en"
            )
            _olmoasr_processor = AutoProcessor.from_pretrained(
                f"allenai/OLMoASR-{model_size}.en"
            )
            logger.info("OLMoASR cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando OLMoASR: {e}")
            raise

    return _olmoasr_model, _olmoasr_processor


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    output_format: str = "txt"
) -> Dict[str, Any]:
    """
    Transcribe audio a texto usando OLMoASR.

    Args:
        audio_path: Ruta al archivo de audio
        model_size: tiny, base, small
        output_format: txt, srt, vtt

    Returns:
        dict con success, text, output_file
    """
    try:
        # Importar aquí para evitar carga innecesaria
        import torch
        from transformers import AutoProcessor, OlmoASRForConditionalGeneration

        logger.info(f"Transcribiendo {audio_path} con OLMoASR-{model_size}")

        # Cargar modelo
        model_name = f"allenai/OLMoASR-{model_size}.en"
        processor = AutoProcessor.from_pretrained(model_name)
        model = OlmoASRForConditionalGeneration.from_pretrained(model_name)

        # Cargar audio (soporta múltiples formatos)
        import librosa
        audio_input, sr = librosa.load(audio_path, sr=16000)

        # Procesar
        inputs = processor(audio_input, return_tensors="pt")

        if torch.cuda.is_available():
            model = model.cuda()
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Transcribir
        generated_ids = model.generate(**inputs, max_new_tokens=512)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Guardar archivo
        base = Path(audio_path).stem
        ext = "txt" if output_format == "txt" else output_format
        out_file = f"{base}_transcribed.{ext}"

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)

        logger.info(f"Transcripción completada: {out_file}")

        return {
            "success": True,
            "text": text,
            "output_file": out_file,
            "message": f"Transcrito a {out_file}"
        }

    except ImportError as e:
        logger.error(f"Dependencia faltante: {e}")
        return {
            "success": False,
            "error": f"Instala dependencias: pip install torch transformers librosa",
            "message": "Error: faltan dependencias"
        }
    except Exception as e:
        logger.error(f"Error en transcripción: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error: {str(e)}"
        }


def transcribe_audio_async(
    files: List[str],
    callback: Optional[Callable] = None,
    model: str = "base",
    format: str = "txt"
) -> None:
    """Versión async de transcribe_audio."""
    from core.async_utils import run_in_background

    def worker():
        results = []
        for f in files:
            result = transcribe_audio(f, model_size=model, output_format=format)
            results.append(result)

        all_success = all(r.get("success") for r in results)
        texts = [r.get("text", "") for r in results if r.get("text")]

        return {
            "success": all_success,
            "message": f"Transcritos {len(results)} archivos",
            "output_files": [r.get("output_file", "") for r in results if r.get("output_file")],
            "text": "\n\n".join(texts)
        }

    run_in_background(worker, callback=callback)