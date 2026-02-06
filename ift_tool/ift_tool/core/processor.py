"""
Módulo principal de procesamiento que orquesta la generación de datasets
"""
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from uuid import uuid4
from datetime import datetime

from ift_tool.utils.extractor import extract_contexts, ChunkResult
from ift_tool.api.llm_client import OpenAIGenerator
from ift_tool.core.prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION
from ift_tool.core.models import QAExample, ContactInfo, Message
from ift_tool.config.settings import AppConfig
from pydantic import BaseModel, Field
from enum import Enum


class YesNoEnum(str, Enum):
    YES = "Yes"
    NO = "No"


class Conversation(BaseModel):
    question_one: str = Field(description="The question asked by the user")
    answer_one: str = Field(description="The answer given by the assistant")
    question_two: str = Field(description="The question asked by the user")
    answer_two: str = Field(description="The answer given by the assistant")
    question_three: str = Field(description="The question asked by the user")
    answer_three: str = Field(description="The answer given by the assistant")
    label: List[str] = Field(description="The labels of the conversation")


class Classifier(BaseModel):
    classification: YesNoEnum = Field(
        description="The classification of the conversation, whether it is about a topic or not"
    )


class ProcessingStatus:
    """Estado del procesamiento"""
    def __init__(self):
        self.stage = "idle"  # idle, extracting, classifying, generating, formatting
        self.current = 0
        self.total = 0
        self.message = ""
        self.errors = []
        self.generated_count = 0
        self.rejected_count = 0


class DatasetProcessor:
    """Procesador principal de datasets"""
    
    def __init__(self, config: AppConfig, progress_callback: Optional[Callable] = None):
        self.config = config
        self.progress_callback = progress_callback
        self.status = ProcessingStatus()
        self.generator = OpenAIGenerator(**config.get_model_client_kwargs())
    
    def update_status(self, stage: str, current: int, total: int, message: str):
        """Actualiza el estado del procesamiento"""
        self.status.stage = stage
        self.status.current = current
        self.status.total = total
        self.status.message = message
        if self.progress_callback:
            self.progress_callback(self.status)
    
    def process_contexts(
        self,
        contexts: List[str],
        output_path: str,
        resume_from: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Procesa una lista de contextos y genera conversaciones.
        
        Args:
            contexts: Lista de contextos a procesar
            output_path: Ruta del archivo de salida (JSONL)
            resume_from: Índice desde el cual continuar (para resume)
        
        Returns:
            Lista de resultados generados
        """
        results = []
        start_idx = resume_from or 0
        topic = self.config.processing.topic
        classification_prompt_template = (
            self.config.processing.classification_prompt or CLASSIFICATION
        )
        
        # Asegurar que el directorio de salida existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        for i, ctx in enumerate(contexts[start_idx:], start=start_idx + 1):
            try:
                # Clasificación
                self.update_status("classifying", i, len(contexts), f"Clasificando contexto {i}/{len(contexts)}")
                
                classification_prompt = classification_prompt_template.format(
                    context=ctx,
                    topic=topic
                )
                
                parsed, usage = self.generator.generate_json(
                    prompt=classification_prompt,
                    json_model=Classifier,
                    model=self.config.model.model_name,
                    **self.config.get_generation_kwargs()
                )
                
                classification = parsed.classification
                
                if classification == YesNoEnum.YES:
                    # Generación de conversaciones
                    self.update_status("generating", i, len(contexts), f"Generando conversaciones para contexto {i}/{len(contexts)}")
                    
                    prompt = INSTRUCTIONS_GENERATOR.format(topic=topic, context=ctx)
                    parsed_conv, usage_conv = self.generator.generate_json(
                        prompt=prompt,
                        json_model=Conversation,
                        model=self.config.model.model_name,
                        **self.config.get_generation_kwargs()
                    )
                    
                    result = parsed_conv.model_dump()
                    
                    info = {
                        "id": i,
                        "classification": classification.value,
                        "context": ctx,
                        "questions": result,
                        "usage": {
                            "classification": usage,
                            "generation": usage_conv
                        }
                    }
                    
                    # Guardar incrementalmente
                    with open(output_path, "a", encoding="utf-8") as out_file:
                        out_file.write(json.dumps(info, ensure_ascii=False) + "\n")
                        out_file.flush()
                    
                    results.append(info)
                    self.status.generated_count += 1
                    
                    self.update_status("generating", i, len(contexts), f"✅ Ejemplo {i} guardado.")
                else:
                    self.status.rejected_count += 1
                    self.update_status("classifying", i, len(contexts), f"🔶 Contexto {i} no relevante. Omitido.")
            
            except Exception as e:
                error_msg = f"❌ Error al procesar contexto {i}: {e}"
                self.status.errors.append(error_msg)
                self.update_status("generating", i, len(contexts), error_msg)
                continue
        
        return results
    
    def format_results(
        self,
        input_path: str,
        output_path: str
    ) -> List[QAExample]:
        """
        Formatea los resultados al formato final QAExample.
        """
        self.update_status("formatting", 0, 1, "Formateando resultados...")
        
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        
        transformed_entries = []
        
        with input_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                entry = json.loads(line)
                messages = []
                
                questions = entry.get("questions", {})
                q_keys = ["question_one", "question_two", "question_three"]
                a_keys = ["answer_one", "answer_two", "answer_three"]
                
                for q_key, a_key in zip(q_keys, a_keys):
                    if questions.get(q_key) and questions.get(a_key):
                        messages.append({"role": "user", "content": questions[q_key]})
                        messages.append({"role": "assistant", "content": questions[a_key]})
                
                if messages:
                    qa_example = QAExample(
                        id=uuid4(),
                        contact_info=ContactInfo(
                            name=self.config.author.name,
                            institution=self.config.author.institution,
                            email=self.config.author.email
                        ),
                        example_type="Pregunta",
                        tags=questions.get("label", []),
                        context=entry.get("context", ""),
                        created_at=datetime.now(),
                        messages=[Message(**msg) for msg in messages]
                    )
                    transformed_entries.append(qa_example)
        
        # Guardar en formato JSON
        with open(output_path, "w", encoding="utf-8") as f_out:
            json.dump(
                [ex.model_dump(mode="json") for ex in transformed_entries],
                f_out,
                ensure_ascii=False,
                indent=2,
                default=str
            )
        
        self.update_status("formatting", 1, 1, f"✅ {len(transformed_entries)} ejemplos formateados.")
        
        return transformed_entries
