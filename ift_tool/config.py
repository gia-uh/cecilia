"""
Módulo de configuración para IFT Tool
Gestiona parámetros de configuración y estado de la aplicación
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pydantic import BaseModel, EmailStr, Field, field_validator


class ModelConfig(BaseModel):
    """Configuración del modelo LLM"""
    provider: str = Field(default="openai", description="Proveedor: 'openai', 'fireworks' o 'openrouter'")
    model_name: str = Field(default="gpt-4-turbo-preview", description="Nombre del modelo")
    api_key: Optional[str] = Field(default=None, description="API Key")
    api_base: Optional[str] = Field(default=None, description="API Base URL (solo para Fireworks/OpenRouter)")
    http_referer: Optional[str] = Field(default=None, description="HTTP Referer para OpenRouter (opcional)")
    app_name: Optional[str] = Field(default="IFT Tool", description="Nombre de la app para OpenRouter (opcional)")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Temperatura del modelo")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Máximo de tokens")


class ChunkingConfig(BaseModel):
    """Configuración de chunking"""
    chunk_size: int = Field(default=2000, ge=100, le=10000, description="Tamaño del chunk en caracteres")
    overlap: int = Field(default=200, ge=0, le=1000, description="Solapamiento entre chunks")
    num_contexts: int = Field(default=20, ge=1, le=10000, description="Número máximo de contextos")


class AuthorInfo(BaseModel):
    """Información del autor del dataset"""
    name: str = Field(default="", description="Nombre del autor")
    institution: str = Field(default="", description="Institución")
    email: str = Field(default="author@example.com", description="Email del autor")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v


class ProcessingConfig(BaseModel):
    """Configuración de procesamiento"""
    data_folder: str = Field(default="data/medicina", description="Carpeta con archivos fuente")
    topic: str = Field(default="salud, medicina", description="Tema del dominio")
    classification_prompt: Optional[str] = Field(default=None, description="Prompt personalizado de clasificación")
    output_folder: str = Field(default="results", description="Carpeta de salida")


class AppConfig(BaseModel):
    """Configuración completa de la aplicación"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    author: AuthorInfo = Field(default_factory=AuthorInfo)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    def save(self, path: str = "config.json"):
        """Guarda la configuración en un archivo JSON"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str = "config.json") -> "AppConfig":
        """Carga la configuración desde un archivo JSON"""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def get_model_client_kwargs(self) -> Dict[str, Any]:
        """Retorna los kwargs para inicializar el cliente LLM"""
        kwargs = {
            "provider": self.model.provider,
            "api_key": self.model.api_key,
            "api_base": self.model.api_base,
            "http_referer": self.model.http_referer,
            "app_name": self.model.app_name,
        }
        return kwargs
    
    def get_generation_kwargs(self) -> Dict[str, Any]:
        """Retorna los kwargs para la generación"""
        kwargs = {
            "temperature": self.model.temperature,
            "top_p": self.model.top_p,
        }
        if self.model.max_tokens:
            kwargs["max_tokens"] = self.model.max_tokens
        return kwargs
