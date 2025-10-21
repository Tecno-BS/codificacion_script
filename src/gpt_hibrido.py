"""
Sistema GPT Hibrido v0.5
Combina asignacion de catalogo historico + generacion emergente de categorias
"""

import os
import json
import hashlib
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from contexto import ContextoProyecto

# Importar configuracion global
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import OPENAI_API_KEY, OPENAI_AVAILABLE

# Importar OpenAI solo si está disponible
if OPENAI_AVAILABLE:
    from openai import OpenAI


@dataclass
class RespuestaInput:
    """Representa una respuesta a codificar"""
    id: str
    texto: str
    pregunta: str


@dataclass
class Catalogo:
    """Representa el catalogo de codigos historicos"""
    pregunta: str
    codigos: List[Dict[str, str]]  # [{"codigo": "50", "descripcion": "..."}]


@dataclass
class ResultadoCodificacion:
    """Resultado de codificacion para una respuesta"""
    respuesta_id: str
    decision: str  # "asignar", "nuevo", "rechazar"
    codigos_historicos: List[str]  # ["50", "25"]
    codigo_nuevo: Optional[str]  # "NUEVO_Participacion_Ciudadana"
    descripcion_nueva: Optional[str]
    idea_principal: Optional[str]
    confianza: float
    justificacion: str


class GptHibrido:
    """
    Sistema hibrido que usa GPT para:
    1. Asignar codigos del catalogo historico
    2. Generar nuevas categorias emergentes (estilo Power Automate)
    """
    
    def __init__(self, model: str = "gpt-5", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or OPENAI_API_KEY
        
        # Detectar si es GPT-5 o posterior (usa max_completion_tokens)
        self.is_gpt5_or_later = self._is_gpt5_or_later(model)
        
        # Inicializar cliente OpenAI
        if not OPENAI_AVAILABLE:
            raise RuntimeError(
                "Cliente OpenAI no disponible. Verifica que:\n"
                "1. La biblioteca 'openai' esté instalada: pip install openai\n"
                "2. OPENAI_API_KEY esté configurada en el archivo .env\n"
                "3. USE_GPT_MOCK=false en el archivo .env"
            )
        
        if not self.api_key:
            raise ValueError(
                "Error: Cliente OpenAI no inicializado. Configura OPENAI_API_KEY\n"
                "Verifica que el archivo .env tenga:\n"
                "OPENAI_API_KEY=sk-proj-tu-api-key-aqui"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.cache = {}
        self.costo_total = 0.0
        
        # Cache file
        self.cache_file = "result/modelos/gpt_hibrido_cache.json"
        self._cargar_cache()
        
        # Mostrar info del modelo
        if self.is_gpt5_or_later:
            token_limit = "8000"
            token_param = "max_completion_tokens"
        else:
            token_limit = "4000"
            token_param = "max_tokens"
        
        temp_info = "temperature=1 fija" if not self._supports_temperature(self.model) else "temperature=0.1"
        print(f"[GPT] Modelo: {self.model}")
        print(f"[GPT] Parametros: {token_param}={token_limit}, {temp_info}")
    
    def _is_gpt5_or_later(self, model: str) -> bool:
        """Detecta si es GPT-5 o posterior (requiere max_completion_tokens)"""
        model_lower = model.lower()
        # GPT-5 y posteriores usan max_completion_tokens
        if 'gpt-5' in model_lower or 'gpt-6' in model_lower:
            return True
        # o1 models también usan max_completion_tokens
        if model_lower.startswith('o1'):
            return True
        # GPT-4.1, GPT-4, GPT-3.5, GPT-4o, GPT-4o-mini usan max_tokens
        return False
    
    def _supports_temperature(self, model: str) -> bool:
        """Detecta si el modelo permite modificar temperature"""
        model_lower = model.lower()
        # GPT-5 y O1 no permiten modificar temperature
        if 'gpt-5' in model_lower or 'gpt-6' in model_lower:
            return False
        if model_lower.startswith('o1'):
            return False
        # Otros modelos sí permiten temperature
        return True
    
    def _cargar_cache(self):
        """Carga cache de disco si existe"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"[CACHE] Cargadas {len(self.cache)} entradas del cache")
        except Exception as e:
            print(f"[WARNING] Error al cargar cache: {e}")
            self.cache = {}
    
    def guardar_cache(self):
        """Guarda cache a disco"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            print(f"[CACHE] Guardadas {len(self.cache)} entradas")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar cache: {e}")
    
    def _cache_key(self, pregunta: str, respuestas: List[RespuestaInput], catalogo: Catalogo) -> str:
        """Genera clave unica para cache"""
        # Combinar pregunta + respuestas + catalogo
        payload = f"{pregunta}|"
        payload += "|".join([r.texto[:100] for r in respuestas])
        payload += "|" + "|".join([f"{c['codigo']}:{c['descripcion'][:50]}" for c in catalogo.codigos[:10]])
        payload += f"|{self.model}"
        
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    def _build_prompt(
        self, 
        pregunta: str, 
        respuestas: List[RespuestaInput], 
        catalogo: Catalogo,
        contexto: Optional[ContextoProyecto] = None
    ) -> str:
        """
        Construye el prompt hibrido que maneja AMBOS modos:
        - Asignacion de catalogo historico
        - Generacion emergente de nuevas categorias
        
        Args:
            pregunta: Texto de la pregunta
            respuestas: Lista de respuestas a codificar
            catalogo: Catalogo de codigos historicos
            contexto: Contexto del proyecto (opcional)
        """
        
        # Formatear contexto (si existe)
        contexto_texto = ""
        if contexto and contexto.tiene_contexto():
            contexto_texto = contexto.to_prompt_text() + "\n\n"
        
        # Formatear catalogo (limitado a 100 codigos mas relevantes)
        if catalogo.codigos:
            catalogo_texto = "\n".join([
                f"[{cod['codigo']}] {cod['descripcion']}"
                for cod in catalogo.codigos[:100]
            ])
        else:
            catalogo_texto = "No hay catalogo historico disponible para esta pregunta."
        
        # Formatear respuestas
        respuestas_texto = "\n".join([
            f"{i+1}. {resp.texto}"
            for i, resp in enumerate(respuestas)
        ])
        
        prompt = f"""Eres un experto en codificacion de respuestas de encuestas de opinion publica.

{contexto_texto}**PREGUNTA DE LA ENCUESTA:**
{pregunta}

**CATALOGO DE CODIGOS HISTORICOS ({len(catalogo.codigos)} codigos):**
{catalogo_texto}

**RESPUESTAS A CODIFICAR ({len(respuestas)}):**
{respuestas_texto}

**INSTRUCCIONES:**

Para CADA respuesta, debes decidir:

**OPCION A: ASIGNAR CODIGO(S) DEL CATALOGO** si:
   - La respuesta encaja claramente con codigo(s) existente(s)
   - Puedes asignar multiples codigos si aplican diferentes temas
   - Solo si la similitud semantica es alta (>85%)

**OPCION B: CREAR CODIGO NUEVO** si:
   - La respuesta NO encaja bien con ningun codigo del catalogo
   - Representa un tema/categoria emergente no contemplado
   - Agrupa con otras respuestas similares bajo la MISMA categoria nueva

**OPCION C: RECHAZAR** si:
   - La respuesta es irrelevante, vacia o incoherente
   - No aporta informacion sustantiva

**REGLAS IMPORTANTES:**
1. Precision > Cobertura (mejor dejar sin codigo que asignar incorrecto)
2. Si creas codigo nuevo, usa formato: NUEVO_[Nombre_Categoria_Descriptivo]
3. Agrupa multiples respuestas bajo el MISMO codigo nuevo si comparten tema
4. Para nombres propios (personas, lugares), verifica si ya existe en catalogo
5. Responde UNICAMENTE en JSON valido (sin texto adicional)

**FORMATO DE RESPUESTA (JSON):**
{{
  "codificaciones": [
    {{
      "respuesta_num": 1,
      "decision": "asignar",
      "codigos_historicos": ["50", "25"],
      "codigo_nuevo": null,
      "descripcion_nueva": null,
      "idea_principal": null,
      "confianza": 0.95,
      "justificacion": "Match claro con codigos historicos sobre representacion"
    }},
    {{
      "respuesta_num": 2,
      "decision": "nuevo",
      "codigos_historicos": [],
      "codigo_nuevo": "NUEVO_Participacion_Ciudadana",
      "descripcion_nueva": "Menciones sobre participacion activa de ciudadanos en democracia",
      "idea_principal": "Importancia de la participacion ciudadana en procesos democraticos",
      "confianza": 0.88,
      "justificacion": "Tema emergente no contemplado en catalogo historico"
    }},
    {{
      "respuesta_num": 3,
      "decision": "rechazar",
      "codigos_historicos": [],
      "codigo_nuevo": null,
      "descripcion_nueva": null,
      "idea_principal": null,
      "confianza": 0.92,
      "justificacion": "Respuesta vacia o irrelevante"
    }}
  ]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        return prompt.strip()
    
    async def codificar_batch(
        self, 
        pregunta: str,
        respuestas: List[RespuestaInput], 
        catalogo: Catalogo,
        contexto: Optional[ContextoProyecto] = None
    ) -> List[ResultadoCodificacion]:
        """
        Codifica un batch de respuestas usando GPT en modo hibrido
        
        Args:
            pregunta: Texto de la pregunta de encuesta
            respuestas: Lista de respuestas a codificar
            catalogo: Catalogo de codigos historicos
            contexto: Contexto del proyecto (opcional)
            
        Returns:
            Lista de ResultadoCodificacion
        """
        
        # Verificar cache
        cache_key = self._cache_key(pregunta, respuestas, catalogo)
        if cache_key in self.cache:
            print(f"[CACHE HIT] Usando resultado cacheado para {len(respuestas)} respuestas")
            return self._parse_resultados(self.cache[cache_key], respuestas)
        
        # Construir prompt (con contexto)
        prompt = self._build_prompt(pregunta, respuestas, catalogo, contexto)
        
        # Llamar a GPT
        try:
            if not self.client:
                raise Exception("Cliente OpenAI no inicializado. Configura OPENAI_API_KEY")
            
            print(f"[GPT] Enviando {len(respuestas)} respuestas a {self.model}...")
            
            # Construir parámetros según el modelo
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un experto en codificacion de respuestas abiertas de encuestas. Respondes UNICAMENTE en JSON valido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"}
            }
            
            # Solo agregar temperature si el modelo lo soporta
            if self._supports_temperature(self.model):
                api_params["temperature"] = 0.1
            # else: GPT-5 y O1 usan temperature=1 por defecto (no se puede cambiar)
            
            # Usar el parámetro correcto según el modelo
            if self.is_gpt5_or_later:
                # GPT-5 necesita más tokens para completar respuestas JSON complejas
                api_params["max_completion_tokens"] = 8000
                # GPT-5 podría no soportar response_format, lo removemos si es necesario
                # Algunos modelos GPT-5 no lo soportan aún
                try:
                    # Intentar primero con response_format
                    completion = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        **api_params
                    )
                except Exception as e:
                    if "response_format" in str(e).lower() or "unsupported" in str(e).lower():
                        print(f"[WARNING] {self.model} no soporta response_format, reintentando sin él...")
                        api_params.pop("response_format", None)
                        completion = await asyncio.to_thread(
                            self.client.chat.completions.create,
                            **api_params
                        )
                    else:
                        raise
            else:
                api_params["max_tokens"] = 4000
                completion = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    **api_params
                )
            
            # Extraer respuesta
            respuesta_json = completion.choices[0].message.content
            
            # Debug: Mostrar respuesta si es GPT-5
            if self.is_gpt5_or_later:
                print(f"[DEBUG] Respuesta GPT-5 (primeros 200 chars): {respuesta_json[:200] if respuesta_json else 'VACIO'}")
            
            if not respuesta_json or not respuesta_json.strip():
                raise Exception(f"GPT devolvió respuesta vacía. Tokens usados: {completion.usage.completion_tokens}")
            
            # Intentar parsear JSON
            try:
                data = json.loads(respuesta_json)
            except json.JSONDecodeError as e:
                # Si falla, intentar extraer JSON del texto
                print(f"[WARNING] JSON inválido, intentando extraer...")
                # Buscar el primer { y el último }
                start = respuesta_json.find('{')
                end = respuesta_json.rfind('}')
                if start != -1 and end != -1:
                    json_text = respuesta_json[start:end+1]
                    data = json.loads(json_text)
                else:
                    raise Exception(f"No se pudo parsear JSON: {e}\nRespuesta: {respuesta_json[:500]}")
            
            # Calcular costo
            costo = self._calcular_costo(
                completion.usage.prompt_tokens,
                completion.usage.completion_tokens
            )
            self.costo_total += costo
            
            print(f"[GPT] Respuesta recibida. Costo: ${costo:.4f}")
            
            # Guardar en cache
            self.cache[cache_key] = data
            
            # Parse resultados
            return self._parse_resultados(data, respuestas)
            
        except Exception as e:
            print(f"[ERROR] Error en llamada a GPT: {e}")
            # Retornar resultados vacios en caso de error
            return [
                ResultadoCodificacion(
                    respuesta_id=r.id,
                    decision="error",
                    codigos_historicos=[],
                    codigo_nuevo=None,
                    descripcion_nueva=None,
                    idea_principal=None,
                    confianza=0.0,
                    justificacion=f"Error: {str(e)}"
                )
                for r in respuestas
            ]
    
    def _parse_resultados(
        self, 
        data: Dict[str, Any], 
        respuestas: List[RespuestaInput]
    ) -> List[ResultadoCodificacion]:
        """Parse JSON de respuesta de GPT a objetos ResultadoCodificacion"""
        
        resultados = []
        codificaciones = data.get('codificaciones', [])
        
        for i, resp in enumerate(respuestas):
            # Buscar codificacion correspondiente
            cod_data = None
            for c in codificaciones:
                if c.get('respuesta_num') == i + 1:
                    cod_data = c
                    break
            
            if not cod_data:
                # No se encontro, crear resultado por defecto
                resultados.append(ResultadoCodificacion(
                    respuesta_id=resp.id,
                    decision="error",
                    codigos_historicos=[],
                    codigo_nuevo=None,
                    descripcion_nueva=None,
                    idea_principal=None,
                    confianza=0.0,
                    justificacion="No se encontro codificacion en respuesta GPT"
                ))
                continue
            
            # Parse resultado (convertir codigos a string por si vienen como int)
            codigos_hist = cod_data.get('codigos_historicos', [])
            codigos_hist_str = [str(c) for c in codigos_hist] if codigos_hist else []
            
            # Asegurar que codigo_nuevo también sea string si existe
            codigo_nuevo = cod_data.get('codigo_nuevo')
            if codigo_nuevo is not None:
                codigo_nuevo = str(codigo_nuevo)
            
            resultados.append(ResultadoCodificacion(
                respuesta_id=resp.id,
                decision=cod_data.get('decision', 'error'),
                codigos_historicos=codigos_hist_str,
                codigo_nuevo=codigo_nuevo,
                descripcion_nueva=cod_data.get('descripcion_nueva'),
                idea_principal=cod_data.get('idea_principal'),
                confianza=cod_data.get('confianza', 0.0),
                justificacion=cod_data.get('justificacion', '')
            ))
        
        return resultados
    
    def _calcular_costo(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calcula costo basado en tokens y modelo"""
        
        # Precios por 1M tokens (actualizado 2025)
        precios = {
            'gpt-4o-mini': {
                'input': 0.150,   # $0.150 per 1M input tokens
                'output': 0.600   # $0.600 per 1M output tokens
            },
            'gpt-4o': {
                'input': 2.50,
                'output': 10.00
            },
            'gpt-4.1': {
                'input': 3.00,    # Precio para GPT-4.1
                'output': 12.00   # Precio para GPT-4.1
            },
            'gpt-3.5-turbo': {
                'input': 0.50,
                'output': 1.50
            },
            'gpt-5': {
                'input': 5.00,    # Precio estimado para GPT-5
                'output': 15.00   # Precio estimado para GPT-5
            },
            'o1-preview': {
                'input': 15.00,
                'output': 60.00
            },
            'o1-mini': {
                'input': 3.00,
                'output': 12.00
            }
        }
        
        # Buscar precio exacto o por prefijo
        modelo_precios = precios.get(self.model)
        
        # Si no se encuentra, buscar por prefijo (ej: gpt-5-turbo -> gpt-5)
        if not modelo_precios:
            for key in precios:
                if self.model.startswith(key):
                    modelo_precios = precios[key]
                    break
        
        # Fallback a gpt-4o-mini
        if not modelo_precios:
            print(f"[WARNING] Precios no encontrados para {self.model}, usando gpt-4o-mini como referencia")
            modelo_precios = precios['gpt-4o-mini']
        
        costo_input = (prompt_tokens / 1_000_000) * modelo_precios['input']
        costo_output = (completion_tokens / 1_000_000) * modelo_precios['output']
        
        return costo_input + costo_output

