"""
Modulo para manejo de contexto del proyecto en codificacion v0.5
"""
from dataclasses import dataclass, asdict
from typing import Optional
import json


@dataclass
class ContextoProyecto:
    """
    Almacena informacion contextual del proyecto de codificacion
    
    Esta informacion se usa para:
    1. Mejorar la precision de GPT al codificar
    2. Documentar el proyecto en los resultados
    3. Proporcionar trazabilidad
    """
    
    # Campos principales (basados en prompt agente codificacion)
    antecedentes: str = ""
    objetivo: str = ""
    grupo_objetivo: str = ""
    
    # Campos adicionales
    nombre_proyecto: str = ""
    cliente: str = ""
    fecha: str = ""
    notas_adicionales: str = ""
    
    def __post_init__(self):
        """Validacion y limpieza de campos"""
        # Limpiar espacios en blanco
        self.antecedentes = self.antecedentes.strip()
        self.objetivo = self.objetivo.strip()
        self.grupo_objetivo = self.grupo_objetivo.strip()
        self.nombre_proyecto = self.nombre_proyecto.strip()
        self.cliente = self.cliente.strip()
        self.fecha = self.fecha.strip()
        self.notas_adicionales = self.notas_adicionales.strip()
    
    def tiene_contexto(self) -> bool:
        """
        Verifica si se proporciono algun contexto
        
        Returns:
            True si al menos un campo principal esta lleno
        """
        return bool(
            self.antecedentes or 
            self.objetivo or 
            self.grupo_objetivo
        )
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convierte a JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def to_prompt_text(self) -> str:
        """
        Genera texto formateado para incluir en prompt de GPT
        
        Returns:
            Texto formateado con el contexto, o cadena vacia si no hay contexto
        """
        if not self.tiene_contexto():
            return ""
        
        partes = []
        
        partes.append("=== CONTEXTO DEL PROYECTO ===\n")
        
        if self.nombre_proyecto:
            partes.append(f"**Proyecto:** {self.nombre_proyecto}")
        
        if self.cliente:
            partes.append(f"**Cliente:** {self.cliente}")
        
        if self.antecedentes:
            partes.append(f"**Antecedentes:**\n{self.antecedentes}")
        
        if self.objetivo:
            partes.append(f"**Objetivo del Proyecto:**\n{self.objetivo}")
        
        if self.grupo_objetivo:
            partes.append(f"**Grupo Objetivo:**\n{self.grupo_objetivo}")
        
        if self.notas_adicionales:
            partes.append(f"**Notas Adicionales:**\n{self.notas_adicionales}")
        
        partes.append("\n=== FIN CONTEXTO ===\n")
        
        return "\n\n".join(partes)
    
    def resumen_corto(self) -> str:
        """
        Genera un resumen corto del contexto (para logs/UI)
        
        Returns:
            Resumen de 1-2 lineas
        """
        if not self.tiene_contexto():
            return "Sin contexto proporcionado"
        
        partes = []
        
        if self.nombre_proyecto:
            partes.append(f"Proyecto: {self.nombre_proyecto}")
        
        if self.objetivo:
            objetivo_corto = self.objetivo[:80] + "..." if len(self.objetivo) > 80 else self.objetivo
            partes.append(f"Objetivo: {objetivo_corto}")
        
        if self.grupo_objetivo:
            partes.append(f"Grupo: {self.grupo_objetivo}")
        
        return " | ".join(partes) if partes else "Contexto proporcionado"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContextoProyecto':
        """Crea instancia desde diccionario"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    @classmethod
    def vacio(cls) -> 'ContextoProyecto':
        """Crea instancia vacia (sin contexto)"""
        return cls()


# Funcion de utilidad para validacion
def validar_contexto(contexto: ContextoProyecto) -> tuple[bool, str]:
    """
    Valida que el contexto tenga formato correcto
    
    Args:
        contexto: Instancia de ContextoProyecto
        
    Returns:
        (es_valido, mensaje)
    """
    if not isinstance(contexto, ContextoProyecto):
        return False, "Contexto debe ser instancia de ContextoProyecto"
    
    # Validar que los campos de texto no sean extremadamente largos
    MAX_LENGTH = 5000
    
    for campo, valor in contexto.to_dict().items():
        if len(valor) > MAX_LENGTH:
            return False, f"Campo '{campo}' excede longitud maxima ({MAX_LENGTH} caracteres)"
    
    return True, "Contexto valido"

