"""
Utilidades para cargar prompts desde archivos.
"""
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "codificacion_nueva"


def load_prompt(nombre: str) -> str:
    """
    Carga un prompt desde un archivo .md.
    
    Args:
        nombre: Nombre del prompt (sin extensión .md)
        
    Returns:
        Contenido del prompt como string
    """
    ruta = PROMPTS_DIR / f"{nombre}.md"
    return ruta.read_text(encoding="utf-8")

