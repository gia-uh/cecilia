"""
Módulo para calcular costos de uso de APIs de LLM
"""
from typing import Dict, Optional


# Precios por 1K tokens (actualizados a 2024)
PRICING: Dict[str, Dict[str, Dict[str, float]]] = {
    "openai": {
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4o": {"input": 0.005, "output": 0.015},
    },
    "fireworks": {
        "default": {"input": 0.0001, "output": 0.0001},  # Precio aproximado
    },
    "openrouter": {
        # Modelos OpenAI vía OpenRouter
        "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "openai/gpt-4": {"input": 0.03, "output": 0.06},
        "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "openai/gpt-4o": {"input": 0.005, "output": 0.015},
        # Modelos Anthropic vía OpenRouter
        "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
        "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        # Modelos Meta vía OpenRouter
        "meta-llama/llama-3-70b-instruct": {"input": 0.00059, "output": 0.00079},
        "meta-llama/llama-3-8b-instruct": {"input": 0.00005, "output": 0.00005},
        # Modelos Mistral vía OpenRouter
        "mistralai/mistral-large": {"input": 0.002, "output": 0.006},
        "mistralai/mixtral-8x7b-instruct": {"input": 0.00024, "output": 0.00024},
        # Modelos Google vía OpenRouter
        "google/gemini-pro": {"input": 0.0005, "output": 0.0015},
        "google/gemini-pro-1.5": {"input": 0.00125, "output": 0.005},
        # Default para modelos no listados (precio promedio)
        "default": {"input": 0.001, "output": 0.003},
    }
}


def calculate_cost(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> float:
    """
    Calcula el costo en USD basado en el uso de tokens.
    
    Args:
        provider: 'openai', 'fireworks' o 'openrouter'
        model: Nombre del modelo
        prompt_tokens: Tokens de entrada
        completion_tokens: Tokens de salida
    
    Returns:
        Costo en USD
    """
    if provider not in PRICING:
        return 0.0
    
    pricing = PRICING[provider]
    
    # Para OpenRouter, buscar el modelo exacto o por prefijo
    if provider == "openrouter":
        # Buscar modelo exacto primero
        if model in pricing:
            model_pricing = pricing[model]
        else:
            # Buscar por prefijo (ej: "openai/gpt-4" -> "openai/gpt-4-turbo")
            model_parts = model.split("/")
            if len(model_parts) == 2:
                # Buscar modelos del mismo proveedor
                provider_prefix = model_parts[0] + "/"
                matching_models = {k: v for k, v in pricing.items() if k.startswith(provider_prefix)}
                if matching_models:
                    # Usar el primer modelo encontrado del mismo proveedor
                    model_pricing = list(matching_models.values())[0]
                else:
                    model_pricing = pricing.get("default", {"input": 0.001, "output": 0.003})
            else:
                model_pricing = pricing.get("default", {"input": 0.001, "output": 0.003})
    else:
        # Para otros providers, buscar modelo exacto o default
        if model in pricing:
            model_pricing = pricing[model]
        elif "default" in pricing:
            model_pricing = pricing["default"]
        else:
            return 0.0
    
    input_cost = (prompt_tokens / 1000) * model_pricing.get("input", 0)
    output_cost = (completion_tokens / 1000) * model_pricing.get("output", 0)
    
    return input_cost + output_cost


def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto.
    Aproximación: ~4 caracteres por token para español/inglés.
    """
    return len(text) // 4


def format_cost(cost: float) -> str:
    """Formatea el costo para mostrar"""
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1:
        return f"${cost:.2f}"
    else:
        return f"${cost:.2f}"
