import json
import random
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from config import *

@dataclass
class ItemGPT:
    id_respuesta: str
    pregunta: str
    texto: str
    candidatos: List[Dict[str, Any]]
    auxiliar: Optional[str]

@dataclass
class ResultadoGPT:
    id_respuesta: str
    pregunta: str
    raw: Dict[str, Any]
    costo_estimado: float = 0.0

class GptCodificadorMock:
    """
    Mock del agente GPT que simula respuestas sin usar la API real
    Ideal para desarrollo y pruebas sin costo
    """
    def __init__(self, model: Optional[str] = None, cache=None):
        self.model = model or "gpt-4o-mini-mock"
        self.cache = cache or {}
        self.costo_total = 0.0
        
        # Patrones de decisión basados en similitud
        self.umbrales_mock = {
            "asignar": 0.8,  # Si similitud > 0.8, asignar
            "nuevo": 0.3,    # Si similitud < 0.3, nuevo código
            "rechazar": 0.1  # Si similitud < 0.1, rechazar
        }
        
        print(f"Iniciando GPT Mock (Modelo: {self.model})")
        
    def _cache_key(self, item: ItemGPT) -> str:
        # Simular cache key (igual que el real)
        import hashlib
        payload = f"{item.pregunta}|{item.texto[:MAX_CHARS_TEXTO]}|{json.dumps(item.candidatos, sort_keys=True)}|{item.auxiliar or ''}|{self.model}|v1"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
    async def codificar_lote(self, items: List[ItemGPT], contexto_proyecto: Dict[str, str]) -> List[ResultadoGPT]:
        """
        Simula el procesamiento de GPT con respuestas realistas
        """
        print(f"🔄 Procesando lote mock de {len(items)} items...")
        resultados = []
        
        for i, item in enumerate(items):
            # Verificar cache
            cache_key = self._cache_key(item)
            if GPT_CACHE_ENABLED and cache_key in self.cache:
                resultados.append(ResultadoGPT(
                    item.id_respuesta, 
                    item.pregunta, 
                    self.cache[cache_key]
                ))
                continue
            
            # Simular decisión basada en similitud del mejor candidato
            mejor_similitud = 0.0
            if item.candidatos:
                mejor_similitud = max(cand["similitud"] for cand in item.candidatos)
            
            # Decidir basado en similitud y patrones realistas
            if mejor_similitud >= self.umbrales_mock["asignar"]:
                decision = "asignar"
                candidato_elegido = max(item.candidatos, key=lambda x: x["similitud"])
                codigos_asignados = [candidato_elegido["codigo"]]
                justificacion = f"Asignado código {candidato_elegido['codigo']} por alta similitud ({candidato_elegido['similitud']:.2f})"
                
            elif mejor_similitud >= self.umbrales_mock["nuevo"]:
                decision = "nuevo"
                codigos_asignados = []
                justificacion = f"Similitud insuficiente ({mejor_similitud:.2f}) para asignar código existente"
                
            else:
                decision = "rechazar"
                codigos_asignados = []
                justificacion = f"Respuesta irrelevante o vacía (similitud: {mejor_similitud:.2f})"
            
            # Generar propuesta de nuevo código si es necesario
            propuesta_codigo_nuevo = None
            if decision == "nuevo":
                propuesta_codigo_nuevo = {
                    "codigo_sugerido": f"NEW_{random.randint(1000, 9999)}",
                    "descripcion": self._generar_descripcion_inteligente(item.texto, item.pregunta)
                }
            
            # Simular costo realista
            costo_simulado = random.uniform(0.002, 0.008)
            self.costo_total += costo_simulado
            
            # Crear respuesta mock
            respuesta_mock = {
                "decision": decision,
                "codigos_asignados": codigos_asignados,
                "justificacion_breve": justificacion,
                "propuesta_codigo_nuevo": propuesta_codigo_nuevo
            }
            
            # Guardar en cache
            if GPT_CACHE_ENABLED:
                self.cache[cache_key] = respuesta_mock
            
            resultados.append(ResultadoGPT(
                item.id_respuesta,
                item.pregunta,
                respuesta_mock,
                costo_simulado
            ))
            
            # Simular latencia realista
            await asyncio.sleep(0.1)
        
        print(f"✅ Mock completado. Costo simulado: ${self.costo_total:.4f}")
        return resultados
    
    def _generar_descripcion_inteligente(self, texto: str, pregunta: str) -> str:
        """
        Genera descripciones más realistas basadas en el contenido
        """
        palabras_clave = texto.lower().split()[:5]
        descripciones_base = [
            "Respuesta relacionada con",
            "Comentario sobre",
            "Mención de",
            "Referencia a",
            "Opinión sobre"
        ]
        
        descripcion_base = random.choice(descripciones_base)
        palabras_relevantes = " ".join(palabras_clave[:3])
        
        return f"{descripcion_base} {palabras_relevantes}"
    
    def guardar_cache(self):
        if GPT_CACHE_ENABLED and GPT_CACHE_FILE:
            import os
            os.makedirs(os.path.dirname(GPT_CACHE_FILE), exist_ok=True)
            with open(GPT_CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
            print(f"💾 Cache mock guardado en {GPT_CACHE_FILE}")
    
    def cargar_cache(self):
        if GPT_CACHE_ENABLED and os.path.exists(GPT_CACHE_FILE):
            try:
                with open(GPT_CACHE_FILE, 'r') as f:
                    self.cache = json.load(f)
                print(f"📂 Cache mock cargado desde {GPT_CACHE_FILE}")
            except:
                self.cache = {}