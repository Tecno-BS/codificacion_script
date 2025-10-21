"""
Extractor Automatico de Contexto desde Documentos
Soporta: DOCX, PDF, TXT, XLSX
"""

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any
import os

# Imports condicionales para diferentes formatos
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from contexto import ContextoProyecto


class ExtractorContexto:
    """
    Extrae automaticamente contexto del proyecto desde documentos
    """
    
    def __init__(self, usar_gpt: bool = True):
        """
        Args:
            usar_gpt: Si True, usa GPT para extraccion inteligente
                     Si False, usa patrones regex (menos preciso)
        """
        self.usar_gpt = usar_gpt and OPENAI_AVAILABLE
        
        if self.usar_gpt:
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key) if api_key else None
            if not self.client:
                print("[EXTRACTOR] OPENAI_API_KEY no encontrada, usando regex")
                self.usar_gpt = False
    
    def extraer_desde_archivo(self, ruta_archivo: str) -> ContextoProyecto:
        """
        Extrae contexto desde archivo (auto-detecta formato)
        
        Args:
            ruta_archivo: Ruta al archivo de contexto
            
        Returns:
            ContextoProyecto con informacion extraida
        """
        ruta = Path(ruta_archivo)
        extension = ruta.suffix.lower()
        
        print(f"[EXTRACTOR] Procesando: {ruta.name}")
        
        # Leer texto segun formato
        texto = ""
        
        if extension == ".txt":
            texto = self._leer_txt(ruta)
        elif extension in [".docx", ".doc"]:
            texto = self._leer_docx(ruta)
        elif extension == ".pdf":
            texto = self._leer_pdf(ruta)
        elif extension in [".xlsx", ".xls"]:
            texto = self._leer_excel(ruta)
        else:
            raise ValueError(f"Formato no soportado: {extension}. Soportados: TXT, DOCX, DOC, PDF, XLSX, XLS")
        
        if not texto.strip():
            print("[EXTRACTOR] Archivo vacio o no se pudo leer")
            return ContextoProyecto.vacio()
        
        print(f"[EXTRACTOR] Texto extraido: {len(texto)} caracteres")
        
        # Extraer campos estructurados
        if self.usar_gpt:
            contexto = self._extraer_con_gpt(texto)
        else:
            contexto = self._extraer_con_regex(texto)
        
        return contexto
    
    def _leer_txt(self, ruta: Path) -> str:
        """Lee archivo TXT"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(ruta, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _leer_docx(self, ruta: Path) -> str:
        """
        Lee archivo DOCX (y archivos .doc que en realidad son .docx)
        """
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx no instalado. Instala: pip install python-docx")
        
        try:
            doc = docx.Document(ruta)
            texto = "\n".join([p.text for p in doc.paragraphs])
            return texto
        except Exception as e:
            error_msg = str(e).lower()
            
            # Error común: archivo .doc que es realmente .docx
            if "not a word file" in error_msg or "content type" in error_msg:
                raise ValueError(
                    f"El archivo '{ruta.name}' tiene extensión .doc pero es formato .docx moderno. "
                    "Soluciones:\n"
                    "1. Renombra el archivo de .doc a .docx\n"
                    "2. Abre el archivo en Word y guárdalo como .docx\n"
                    "3. O guárdalo como .txt y súbelo de nuevo"
                )
            else:
                # Otro error
                raise ValueError(f"Error al leer documento Word: {e}")
    
    def _leer_pdf(self, ruta: Path) -> str:
        """Lee archivo PDF"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 no instalado. Instala: pip install PyPDF2")
        
        texto = ""
        with open(ruta, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
        return texto
    
    def _leer_excel(self, ruta: Path) -> str:
        """Lee archivo Excel (busca hoja de contexto)"""
        import pandas as pd
        
        try:
            # Intentar leer hoja "Contexto" o primera hoja
            try:
                df = pd.read_excel(ruta, sheet_name="Contexto")
            except:
                df = pd.read_excel(ruta, sheet_name=0)
            
            # Convertir a texto
            texto = ""
            for col in df.columns:
                texto += f"{col}:\n"
                texto += "\n".join(df[col].dropna().astype(str).tolist())
                texto += "\n\n"
            
            return texto
        except Exception as e:
            print(f"[EXTRACTOR] Error leyendo Excel: {e}")
            return ""
    
    def _extraer_con_gpt(self, texto: str) -> ContextoProyecto:
        """
        Extraccion inteligente usando GPT
        """
        print("[EXTRACTOR] Usando GPT para extraccion inteligente...")
        
        prompt = f"""Analiza el siguiente texto y extrae la informacion del proyecto de investigacion/encuesta.

TEXTO:
{texto[:3000]}  # Limitar a 3000 chars para no exceder tokens

Extrae los siguientes campos (si no encuentras informacion, deja vacio):
- nombre_proyecto: Nombre o titulo del proyecto/estudio
- cliente: Cliente u organizacion que solicita
- antecedentes: Contexto historico o antecedentes del proyecto
- objetivo: Objetivo principal del estudio
- grupo_objetivo: Poblacion objetivo o muestra (quien fue encuestado)
- notas_adicionales: Cualquier otra informacion relevante

Responde SOLO con JSON valido:
{{
  "nombre_proyecto": "...",
  "cliente": "...",
  "antecedentes": "...",
  "objetivo": "...",
  "grupo_objetivo": "...",
  "notas_adicionales": "..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en analisis de documentos de investigacion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            respuesta = response.choices[0].message.content.strip()
            
            # Limpiar markdown si existe
            if respuesta.startswith("```json"):
                respuesta = respuesta.replace("```json", "").replace("```", "").strip()
            
            # Parsear JSON
            datos = json.loads(respuesta)
            
            contexto = ContextoProyecto(
                nombre_proyecto=datos.get("nombre_proyecto", ""),
                cliente=datos.get("cliente", ""),
                antecedentes=datos.get("antecedentes", ""),
                objetivo=datos.get("objetivo", ""),
                grupo_objetivo=datos.get("grupo_objetivo", ""),
                notas_adicionales=datos.get("notas_adicionales", "")
            )
            
            print(f"[EXTRACTOR] Contexto extraido exitosamente: {contexto.resumen_corto()}")
            return contexto
            
        except Exception as e:
            print(f"[EXTRACTOR] Error con GPT: {e}, usando regex fallback")
            return self._extraer_con_regex(texto)
    
    def _extraer_con_regex(self, texto: str) -> ContextoProyecto:
        """
        Extraccion basica usando patrones regex
        Menos preciso que GPT pero funciona sin API
        """
        print("[EXTRACTOR] Usando extraccion por patrones regex...")
        
        contexto_dict = {
            "nombre_proyecto": "",
            "cliente": "",
            "antecedentes": "",
            "objetivo": "",
            "grupo_objetivo": "",
            "notas_adicionales": ""
        }
        
        # Patrones de busqueda (insensitive case)
        patrones = {
            "nombre_proyecto": [
                r"(?:proyecto|estudio|encuesta):\s*(.+?)(?:\n|$)",
                r"(?:nombre|titulo):\s*(.+?)(?:\n|$)",
                r"^(.+?)(?:\n|$)"  # Primera linea como fallback
            ],
            "cliente": [
                r"(?:cliente|solicitante|para):\s*(.+?)(?:\n|$)",
                r"(?:organizacion|entidad):\s*(.+?)(?:\n|$)"
            ],
            "antecedentes": [
                r"(?:antecedentes|contexto|background):\s*(.+?)(?:\n\n|\n[A-Z])",
                r"(?:historia|origen):\s*(.+?)(?:\n\n|\n[A-Z])"
            ],
            "objetivo": [
                r"(?:objetivo|proposito|meta|finalidad):\s*(.+?)(?:\n\n|\n[A-Z])",
                r"(?:busca|pretende|intenta):\s*(.+?)(?:\n\n|\n[A-Z])"
            ],
            "grupo_objetivo": [
                r"(?:grupo objetivo|poblacion|muestra|encuestados):\s*(.+?)(?:\n|$)",
                r"(?:participantes|respondentes):\s*(.+?)(?:\n|$)"
            ]
        }
        
        # Buscar cada campo
        for campo, lista_patrones in patrones.items():
            for patron in lista_patrones:
                match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
                if match:
                    valor = match.group(1).strip()
                    if len(valor) > 10:  # Minimo 10 chars para ser valido
                        contexto_dict[campo] = valor[:500]  # Limitar longitud
                        break
        
        # Si no se encontro nada relevante, usar primeras lineas como notas
        if not any(contexto_dict.values()):
            contexto_dict["notas_adicionales"] = texto[:500]
        
        contexto = ContextoProyecto(**contexto_dict)
        
        if contexto.tiene_contexto():
            print(f"[EXTRACTOR] Contexto extraido: {contexto.resumen_corto()}")
        else:
            print("[EXTRACTOR] No se pudo extraer contexto estructurado")
        
        return contexto


def probar_extractor(ruta_archivo: str):
    """
    Funcion de prueba
    """
    extractor = ExtractorContexto(usar_gpt=True)
    contexto = extractor.extraer_desde_archivo(ruta_archivo)
    
    print("\n" + "="*70)
    print("CONTEXTO EXTRAIDO:")
    print("="*70)
    print(contexto.to_prompt_text())
    print("="*70)
    
    return contexto


if __name__ == "__main__":
    # Prueba rapida
    import sys
    if len(sys.argv) > 1:
        probar_extractor(sys.argv[1])
    else:
        print("Uso: python extractor_contexto.py <ruta_archivo>")

