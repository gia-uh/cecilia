import os
from typing import Type, TypeVar, Optional, Dict, Any
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class TokenUsage:
    """Clase para rastrear el uso de tokens"""
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def add_usage(self, usage):
        """Agrega tokens de una respuesta"""
        if hasattr(usage, 'prompt_tokens'):
            self.prompt_tokens += usage.prompt_tokens
        if hasattr(usage, 'completion_tokens'):
            self.completion_tokens += usage.completion_tokens
        if hasattr(usage, 'total_tokens'):
            self.total_tokens += usage.total_tokens
    
    def reset(self):
        """Reinicia el contador"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0


class OpenAIGenerator:
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        http_referer: Optional[str] = None,
        app_name: Optional[str] = None
    ):
        """
        Inicializa el generador de LLM.
        
        Args:
            provider: Proveedor a usar ('openai', 'fireworks', 'openrouter')
            api_key: API key (si None, usa variable de entorno)
            api_base: API base URL (para Fireworks/OpenRouter)
            http_referer: HTTP Referer para OpenRouter (opcional)
            app_name: Nombre de la app para OpenRouter (opcional)
        """
        # Determinar API key y base URL según el provider
        if api_key is None:
            if provider == "fireworks":
                api_key = os.getenv("FIREWORKS_API_KEY")
                api_base = api_base or os.getenv("FIREWORKS_API_BASE") or "https://api.fireworks.ai/inference/v1"
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                api_base = api_base or os.getenv("OPENROUTER_API_BASE") or "https://openrouter.ai/api/v1"
            else:  # openai
                api_key = os.getenv("OPENAI_API_KEY")
                api_base = None
        
        # Inicializar cliente OpenAI (compatible con todos los providers)
        # Para OpenRouter, necesitamos agregar headers especiales
        if provider == "openrouter":
            # OpenRouter requiere headers adicionales
            default_headers = {}
            if http_referer:
                default_headers["HTTP-Referer"] = http_referer
            if app_name:
                default_headers["X-Title"] = app_name
            
            # Intentar usar default_headers si está disponible (OpenAI >= 1.0.0)
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=api_base or "https://openrouter.ai/api/v1",
                    default_headers=default_headers if default_headers else None
                )
            except TypeError:
                # Si default_headers no está disponible, crear cliente normal
                # y los headers se agregarán manualmente en cada request
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=api_base or "https://openrouter.ai/api/v1"
                )
                # Guardar headers para agregarlos manualmente
                self._openrouter_headers = default_headers
        elif api_base:
            self.client = OpenAI(api_key=api_key, base_url=api_base)
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.provider = provider
        self.http_referer = http_referer
        self.app_name = app_name or "IFT Tool"
        self.token_usage = TokenUsage()
        
        # Para OpenRouter sin default_headers, inicializar dict vacío
        if provider == "openrouter" and not hasattr(self, '_openrouter_headers'):
            self._openrouter_headers = {}

    def generate_text(
        self,
        prompt: str = "",
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        Genera texto libre a partir de un prompt.
        
        Returns:
            Tupla (texto generado, uso de tokens)
        """
        if model_name is None:
            if self.provider == "fireworks":
                model_name = os.getenv("FIREWORKS_MODEL") or "accounts/fireworks/models/llama-v2-7b-chat"
            elif self.provider == "openrouter":
                model_name = os.getenv("OPENROUTER_MODEL") or "openai/gpt-4-turbo"
            else:
                model_name = "gpt-4-turbo-preview"
        
        # Los headers para OpenRouter ya están configurados en la inicialización del cliente
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            **kwargs
        )
        
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        self.token_usage.add_usage(response.usage)
        
        return response.choices[0].message.content, usage

    def generate_json(
        self,
        prompt: str = "",
        json_model: Type[T] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Genera respuestas estructuradas en formato JSON.
        
        Returns:
            Tupla (objeto parseado, uso de tokens)
        """
        if model is None:
            if self.provider == "fireworks":
                model = os.getenv("FIREWORKS_MODEL") or "accounts/fireworks/models/llama-v2-7b-chat"
            elif self.provider == "openrouter":
                model = os.getenv("OPENROUTER_MODEL") or "openai/gpt-4-turbo"
            else:
                model = "gpt-4-turbo-preview"
        
        # Asegurar que temperature esté en kwargs si no está
        if "temperature" not in kwargs:
            kwargs["temperature"] = 0
        
        # Para OpenRouter, structured outputs puede requerir formato diferente
        # Intentar usar structured outputs si está disponible
        try:
            # Los headers para OpenRouter ya están configurados en la inicialización del cliente
            response = self.client.beta.chat.completions.parse(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format=json_model,
                **kwargs,
            )
        except Exception as e:
            # Si structured outputs falla (algunos modelos no lo soportan),
            # intentar con generación normal y parsing manual
            if "structured" in str(e).lower() or "parse" in str(e).lower():
                # Fallback: generar texto y parsear manualmente
                import json as json_lib
                text_response, usage = self.generate_text(prompt=prompt, model_name=model, **kwargs)
                try:
                    parsed_data = json_lib.loads(text_response)
                    # Crear instancia del modelo Pydantic
                    parsed = json_model(**parsed_data)
                    return parsed, usage
                except Exception as parse_error:
                    raise Exception(f"Error parsing JSON response: {parse_error}. Original error: {e}")
            else:
                raise
        
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        self.token_usage.add_usage(response.usage)
        
        return response.choices[0].message.parsed, usage
