"""
Servicio para interacción con LLMs (OpenAI).
"""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ....config import OPENAI_API_KEY, supports_temperature, get_default_temperature
from ...utils import extraer_tokens


class LLMService:
    """
    Servicio para manejar llamadas a LLMs de forma consistente.
    """
    
    def __init__(self, modelo: str, api_key: Optional[str] = None):
        """
        Inicializa el servicio LLM.
        
        Args:
            modelo: Nombre del modelo a usar (ej: "gpt-5", "gpt-4o-mini")
            api_key: API key de OpenAI (opcional, usa la del config por defecto)
        """
        self.modelo = modelo
        self.api_key = api_key or OPENAI_API_KEY
        
        # Configurar temperature según el modelo
        llm_kwargs: Dict[str, Any] = {
            "model": self.modelo,
            "api_key": self.api_key
        }
        
        if supports_temperature(self.modelo):
            llm_kwargs["temperature"] = get_default_temperature(self.modelo)
        
        self.llm = ChatOpenAI(**llm_kwargs)
    
    def invoke(
        self,
        prompt_template: str,
        variables: Dict[str, Any],
        system_message: Optional[str] = None
    ) -> Any:
        """
        Invoca el LLM con un prompt template y variables.
        
        Args:
            prompt_template: Template del prompt (puede incluir {variables})
            variables: Diccionario con variables para el template
            system_message: Mensaje del sistema (opcional)
            
        Returns:
            Respuesta del LLM
        """
        messages = []
        
        if system_message:
            messages.append(("system", system_message))
        
        messages.append(("user", prompt_template))
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | self.llm
        
        return chain.invoke(variables)
    
    def invoke_with_system(
        self,
        system_template: str,
        user_template: str,
        variables: Dict[str, Any]
    ) -> Any:
        """
        Invoca el LLM con mensajes de sistema y usuario separados.
        
        Args:
            system_template: Template del mensaje del sistema
            user_template: Template del mensaje del usuario
            variables: Diccionario con variables para los templates
            
        Returns:
            Respuesta del LLM
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", user_template),
        ])
        chain = prompt | self.llm
        
        return chain.invoke(variables)
    
    def extract_tokens(self, response: Any) -> tuple[int, int, int]:
        """
        Extrae tokens de una respuesta del LLM.
        
        Args:
            response: Respuesta del LLM
            
        Returns:
            Tupla con (prompt_tokens, completion_tokens, total_tokens)
        """
        return extraer_tokens(response)

