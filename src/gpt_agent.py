import os
import json
import hashlib
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from config import *
from utils import clean_text

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

class GptCodificador:
    def __init__(self, model: Optional[str] = None, cache=None):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model or OPENAI_MODEL
        self.cache = cache or {}
        self.costo_total = 0.0
        
    def _cache_key(self, item: ItemGPT) -> str:
        payload = f"{item.pregunta}|{item.texto[:MAX_CHARS_TEXTO]}|{json.dumps(item.candidatos, sort_keys=True)}|{item.auxiliar or ''}|{self.model}|v1"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
    def _build_prompt(self, item: ItemGPT, contexto_proyecto: Dict[str, str]) -> str:
        # Truncar texto
        texto_truncado = item.texto[:MAX_CHARS_TEXTO]
        
        # Construir candidatos
        candidatos_texto = ""
        if item.candidatos:
            for i, cand in enumerate(item.candidatos[:GPT_TOP_K], 1):
                candidatos_texto += f"{i}. {cand['codigo']}: {cand['descripcion']} (similitud={cand['similitud']:.2f})\n"
        else:
            candidatos_texto = "No hay candidatos del catálogo."
        
        # Contexto del proyecto
        contexto = f"""
PROYECTO:
- Objetivo: {contexto_proyecto.get('objetivo', 'Codificación de respuestas abiertas')}
- Target: {contexto_proyecto.get('target', 'Encuestados')}

PREGUNTA: {item.pregunta}
RESPUESTA: {texto_truncado}

CANDIDATOS_TOP_{GPT_TOP_K}:
{candidatos_texto}

POLÍTICAS:
- Máximo códigos por respuesta: {MAX_CODIGOS}
- Usa catálogo si encaja razonablemente; si no, propone 'nuevo' con título claro.
- No usar 'irrelevante' si hay mención sustantiva.
- Responde únicamente en JSON válido.
"""
        
        if item.auxiliar:
            contexto += f"\nAUXILIAR DETECTADO: {item.auxiliar}\n"
        
        return contexto.strip()
    
    async def codificar_lote(self, items: List[ItemGPT], contexto_proyecto: Dict[str, str]) -> List[ResultadoGPT]:
        resultados = []
        
        for item in items:
            # Verificar cache
            cache_key = self._cache_key(item)
            if GPT_CACHE_ENABLED and cache_key in self.cache:
                resultados.append(ResultadoGPT(
                    item.id_respuesta, 
                    item.pregunta, 
                    self.cache[cache_key]
                ))
                continue
            
            # Construir prompt
            prompt = self._build_prompt(item, contexto_proyecto)
            
            # Llamar a OpenAI
            try:
                completion = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un analista experto en codificación de respuestas abiertas. Debes asignar códigos del catálogo o proponer uno nuevo. Responde únicamente en JSON válido conforme al esquema."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=GPT_TEMPERATURE,
                    max_tokens=GPT_MAX_TOKENS,
                    response_format={"type": "json_object"}
                )
                
                respuesta = completion.choices[0].message.content
                data = json.loads(respuesta)
                
                # Validar estructura
                if not self._validar_json(data):
                    data = {"decision": "rechazar", "codigos_asignados": [], "justificacion_breve": "Error en formato JSON"}
                
                # Guardar en cache
                if GPT_CACHE_ENABLED:
                    self.cache[cache_key] = data
                
                # Calcular costo estimado
                costo = self._calcular_costo(completion.usage.prompt_tokens, completion.usage.completion_tokens)
                self.costo_total += costo
                
                resultados.append(ResultadoGPT(item.id_respuesta, item.pregunta, data, costo))
                
            except Exception as e:
                print(f"Error en GPT para {item.id_respuesta}: {e}")
                resultados.append(ResultadoGPT(
                    item.id_respuesta, 
                    item.pregunta, 
                    {"decision": "rechazar", "codigos_asignados": [], "justificacion_breve": f"Error: {str(e)}"}
                ))
        
        return resultados
    
    def _validar_json(self, data: Dict[str, Any]) -> bool:
        campos_requeridos = ["decision", "codigos_asignados"]
        return all(campo in data for campo in campos_requeridos)
    
    def _calcular_costo(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Precios aproximados GPT-4o-mini (USD por 1K tokens)
        if self.model == "gpt-4o-mini":
            return (prompt_tokens * 0.00015 + completion_tokens * 0.0006) / 1000
        return 0.0
    
    def guardar_cache(self):
        if GPT_CACHE_ENABLED and GPT_CACHE_FILE:
            os.makedirs(os.path.dirname(GPT_CACHE_FILE), exist_ok=True)
            with open(GPT_CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
    
    def cargar_cache(self):
        if GPT_CACHE_ENABLED and os.path.exists(GPT_CACHE_FILE):
            try:
                with open(GPT_CACHE_FILE, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}