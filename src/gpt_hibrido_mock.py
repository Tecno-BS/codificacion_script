"""
Sistema GPT Hibrido MOCK v0.5
Simula comportamiento de GPT sin consumir API
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from gpt_hibrido import (
    RespuestaInput,
    Catalogo,
    ResultadoCodificacion
)
from contexto import ContextoProyecto


class GptHibridoMock:
    """
    Mock del sistema hibrido que simula decisiones inteligentes sin usar API
    Ideal para desarrollo y pruebas sin costo
    """
    
    def __init__(self, model: str = "gpt-4o-mini-mock", api_key: Optional[str] = None):
        self.model = model
        self.costo_total = 0.0
        
        print(f"[MOCK] Iniciando GPT Hibrido Mock (Modelo: {self.model})")
        print("[MOCK] No se consumira API real de OpenAI")
    
    async def codificar_batch(
        self, 
        pregunta: str,
        respuestas: List[RespuestaInput], 
        catalogo: Catalogo,
        contexto: Optional[ContextoProyecto] = None
    ) -> List[ResultadoCodificacion]:
        """
        Simula codificacion inteligente sin llamar a GPT
        
        Logica de simulacion:
        1. Busca keywords en catalogo vs respuesta
        2. Si match alto (>3 palabras comunes) → asignar
        3. Si match medio (1-2 palabras) → 50% asignar, 50% nuevo
        4. Si match bajo (0 palabras) → crear nuevo
        5. Respuestas muy cortas (<3 palabras) → rechazar
        
        Args:
            pregunta: Texto de la pregunta
            respuestas: Lista de respuestas a codificar
            catalogo: Catalogo de codigos historicos
            contexto: Contexto del proyecto (opcional, usado para logging)
        """
        
        if contexto and contexto.tiene_contexto():
            print(f"[MOCK] Contexto del proyecto: {contexto.resumen_corto()}")
        
        print(f"[MOCK] Simulando codificacion de {len(respuestas)} respuestas...")
        
        # Simular latencia de GPT
        await asyncio.sleep(0.2 * len(respuestas) / 10)  # ~0.2 seg por cada 10 respuestas
        
        resultados = []
        
        for resp in respuestas:
            resultado = self._decidir_codificacion(resp, catalogo)
            resultados.append(resultado)
        
        # Simular costo
        costo_simulado = len(respuestas) * random.uniform(0.001, 0.003)
        self.costo_total += costo_simulado
        
        print(f"[MOCK] Codificacion simulada completada. Costo simulado: ${costo_simulado:.4f}")
        
        return resultados
    
    def _decidir_codificacion(
        self, 
        respuesta: RespuestaInput, 
        catalogo: Catalogo
    ) -> ResultadoCodificacion:
        """
        Logica de decision simulada para una respuesta
        """
        
        texto = respuesta.texto.lower()
        palabras_respuesta = set(texto.split())
        
        # Caso 1: Respuesta muy corta o vacia
        if len(palabras_respuesta) < 3:
            return ResultadoCodificacion(
                respuesta_id=respuesta.id,
                decision="rechazar",
                codigos_historicos=[],
                codigo_nuevo=None,
                descripcion_nueva=None,
                idea_principal=None,
                confianza=0.9,
                justificacion="[MOCK] Respuesta muy corta o vacia"
            )
        
        # Caso 2: Buscar match con catalogo
        mejor_match = None
        max_palabras_comunes = 0
        
        # DEBUG: Verificar si hay catálogo
        if not catalogo.codigos:
            print(f"[MOCK DEBUG] Sin catálogo para pregunta: {catalogo.pregunta}")
        else:
            print(f"[MOCK DEBUG] Buscando en catálogo de {len(catalogo.codigos)} códigos")
        
        for cod in catalogo.codigos:
            descripcion = cod['descripcion'].lower()
            palabras_cod = set(descripcion.split())
            
            # Calcular palabras en comun
            comunes = palabras_respuesta & palabras_cod
            num_comunes = len(comunes)
            
            if num_comunes > max_palabras_comunes:
                max_palabras_comunes = num_comunes
                mejor_match = cod
        
        # DEBUG: Mostrar mejor match
        if mejor_match:
            print(f"[MOCK DEBUG] Mejor match: {mejor_match['codigo']} ({max_palabras_comunes} palabras)")
        
        # Caso 3: Match alto (>= 2 palabras comunes) - UMBRAL REDUCIDO
        if max_palabras_comunes >= 2 and mejor_match:
            # Buscar si hay otros codigos similares para multicodificacion
            # Convertir códigos a string por si vienen como int del Excel
            codigos_asignados = [str(mejor_match['codigo'])]
            
            for cod in catalogo.codigos:
                if cod['codigo'] == mejor_match['codigo']:
                    continue
                    
                descripcion = cod['descripcion'].lower()
                palabras_cod = set(descripcion.split())
                comunes = palabras_respuesta & palabras_cod
                
                if len(comunes) >= 2 and len(codigos_asignados) < 3:
                    codigos_asignados.append(str(cod['codigo']))
                    print(f"[MOCK DEBUG] Multicodigo agregado: {cod['codigo']} ({len(comunes)} palabras)")
            
            # Logging de multicodificación
            if len(codigos_asignados) > 1:
                print(f"[MOCK DEBUG] MULTICODIFICACION: {len(codigos_asignados)} codigos asignados: {', '.join(codigos_asignados)}")
            
            return ResultadoCodificacion(
                respuesta_id=respuesta.id,
                decision="asignar",
                codigos_historicos=codigos_asignados,
                codigo_nuevo=None,
                descripcion_nueva=None,
                idea_principal=None,
                confianza=0.85 + (max_palabras_comunes * 0.03),  # 0.85-0.95
                justificacion=f"[MOCK] {'Multicodigo' if len(codigos_asignados) > 1 else 'Match alto'} con catalogo ({max_palabras_comunes} palabras comunes, {len(codigos_asignados)} codigo(s))"
            )
        
        # Caso 4: Match medio (1-2 palabras comunes)
        elif max_palabras_comunes >= 1 and mejor_match:
            # 50% asignar, 50% nuevo
            if random.random() < 0.5:
                return ResultadoCodificacion(
                    respuesta_id=respuesta.id,
                    decision="asignar",
                    codigos_historicos=[str(mejor_match['codigo'])],  # Convertir a string
                    codigo_nuevo=None,
                    descripcion_nueva=None,
                    idea_principal=None,
                    confianza=0.70 + (max_palabras_comunes * 0.05),
                    justificacion=f"[MOCK] Match medio con catalogo ({max_palabras_comunes} palabras comunes)"
                )
            else:
                return self._generar_codigo_nuevo(respuesta, catalogo, "match_medio")
        
        # Caso 5: Sin match - crear nuevo
        else:
            return self._generar_codigo_nuevo(respuesta, catalogo, "sin_match")
    
    def _generar_codigo_nuevo(
        self, 
        respuesta: RespuestaInput,
        catalogo: Catalogo,
        razon: str
    ) -> ResultadoCodificacion:
        """
        Genera un codigo nuevo simulado con numero secuencial
        """
        
        # Calcular próximo código numérico disponible
        codigos_numericos = []
        for cod in catalogo.codigos:
            try:
                codigos_numericos.append(int(cod['codigo']))
            except (ValueError, TypeError):
                pass
        proximo_codigo = max(codigos_numericos) + 1 if codigos_numericos else 1
        
        # Extraer primeras palabras significativas (>3 letras) para descripción
        palabras = [p for p in respuesta.texto.split() if len(p) > 3]
        palabras_categoria = palabras[:3] if len(palabras) >= 3 else palabras
        
        # Generar descripción DIRECTA (sin "Menciones sobre...", "Referencias a...")
        # Estilo: "Regencia de farmacia", "Manejo de medicamentos", etc.
        if palabras_categoria:
            # Capitalizar primera letra de cada palabra
            descripcion = " ".join([p.capitalize() for p in palabras_categoria])
        else:
            descripcion = f"Categoría emergente {random.randint(100, 999)}"
        
        # Generar idea principal más detallada
        if len(palabras) > 3:
            idea_principal = " ".join([p.capitalize() for p in palabras[:5]])
        else:
            idea_principal = descripcion
        
        confianza = 0.75 if razon == "match_medio" else 0.65
        justificacion_razon = "similitud media con catalogo" if razon == "match_medio" else "tema no contemplado en catalogo"
        
        return ResultadoCodificacion(
            respuesta_id=respuesta.id,
            decision="nuevo",
            codigos_historicos=[],
            codigo_nuevo=str(proximo_codigo),  # Código numérico secuencial
            descripcion_nueva=descripcion,
            idea_principal=idea_principal,
            confianza=confianza,
            justificacion=f"[MOCK] Codigo nuevo generado - {justificacion_razon}"
        )

