"""
IFT Tool - Generador de Datasets para Instruction Fine-Tuning

Herramienta completa para generar sintéticamente datasets de conversaciones
pregunta-respuesta a partir de un corpus de datos textuales.
"""

__version__ = "0.2.0"
__author__ = "Deborah Famadas Rodríguez"
__institution__ = "Universidad de La Habana"

from ift_tool.config import AppConfig
from ift_tool.core.models import QAExample, ContactInfo, Message
from ift_tool.core.processor import DatasetProcessor, ProcessingStatus

__all__ = [
    "AppConfig",
    "QAExample",
    "ContactInfo",
    "Message",
    "DatasetProcessor",
    "ProcessingStatus",
]
