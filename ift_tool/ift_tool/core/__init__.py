"""
Módulo core de IFT Tool - Lógica de negocio principal
"""

from ift_tool.core.models import QAExample, ContactInfo, Message
from ift_tool.core.processor import DatasetProcessor, ProcessingStatus
from ift_tool.core.prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION

__all__ = [
    "QAExample",
    "ContactInfo",
    "Message",
    "DatasetProcessor",
    "ProcessingStatus",
    "INSTRUCTIONS_GENERATOR",
    "CLASSIFICATION",
]
