import os
import json
import re
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class ChunkResult:
    """Resultado de un chunk extraído"""
    context: str
    source_file: str
    chunk_index: int
    start_pos: int
    end_pos: int


def find_semantic_boundaries(text: str, position: int, lookback: int = 100) -> int:
    """
    Encuentra un límite semántico cerca de la posición dada.
    Busca puntos de oración, párrafos o espacios en blanco.
    """
    # Buscar hacia atrás desde la posición
    search_start = max(0, position - lookback)
    search_text = text[search_start:position]
    
    # Buscar el último punto seguido de espacio o salto de línea
    sentence_end = search_text.rfind('. ')
    if sentence_end != -1:
        return search_start + sentence_end + 2
    
    # Buscar último salto de línea doble (párrafo)
    paragraph_end = search_text.rfind('\n\n')
    if paragraph_end != -1:
        return search_start + paragraph_end + 2
    
    # Buscar último salto de línea simple
    line_end = search_text.rfind('\n')
    if line_end != -1:
        return search_start + line_end + 1
    
    # Si no hay límite semántico claro, usar la posición original
    return position


def extract_contexts(
    data_folder: str,
    num_contexts: int,
    output_file: str = "contexts.json",
    chunk_size: int = 1000,
    overlap: int = 0,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[ChunkResult]:
    """
    Extrae contextos de archivos de texto con solapamiento semántico.
    
    Args:
        data_folder: Directorio con archivos fuente
        num_contexts: Número máximo de contextos a extraer
        output_file: Archivo de salida (JSONL)
        chunk_size: Tamaño del chunk en caracteres
        overlap: Solapamiento entre chunks en caracteres
        progress_callback: Función callback para reportar progreso (current, total, message)
    
    Returns:
        Lista de ChunkResult con los contextos extraídos
    """
    folder = Path(data_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {data_folder}")
    
    files = sorted([f for f in folder.iterdir() if f.suffix in ['.txt', '.md']])
    
    if not files:
        raise ValueError(f"No se encontraron archivos .txt o .md en {data_folder}")

    context_count = 0
    file_count = 0
    chunks = []

    if progress_callback:
        progress_callback(0, num_contexts, f"🔍 Procesando archivos en: {data_folder}")

    with open(output_file, "w", encoding="utf-8") as out_f:
        for file in files:
            try:
                with file.open("r", encoding="utf-8") as f:
                    text = f.read().strip()

                if not text:
                    if progress_callback:
                        progress_callback(context_count, num_contexts, f"⚠️  Archivo vacío: {file.name}")
                    continue

                index = 0
                local_chunks = 0
                last_chunk_end = 0

                while index < len(text) and context_count < num_contexts:
                    # Calcular posición final del chunk
                    target_end = index + chunk_size
                    
                    # Si hay solapamiento, empezar desde antes
                    if overlap > 0 and index > 0:
                        overlap_start = max(0, index - overlap)
                        # Buscar límite semántico para el inicio del solapamiento
                        semantic_start = find_semantic_boundaries(text, overlap_start, lookback=50)
                        chunk_start = semantic_start
                    else:
                        chunk_start = index
                    
                    # Ajustar el final del chunk si excede el texto
                    if target_end >= len(text):
                        chunk_end = len(text)
                    else:
                        # Buscar límite semántico para el final
                        chunk_end = find_semantic_boundaries(text, target_end, lookback=100)
                        # Asegurar que el chunk tenga al menos un tamaño mínimo
                        if chunk_end - chunk_start < chunk_size * 0.5:
                            chunk_end = min(len(text), chunk_start + chunk_size)

                    chunk = text[chunk_start:chunk_end].strip()

                    if chunk and len(chunk) >= chunk_size * 0.3:  # Mínimo 30% del tamaño objetivo
                        context_count += 1
                        local_chunks += 1
                        
                        chunk_result = ChunkResult(
                            context=chunk,
                            source_file=str(file.name),
                            chunk_index=local_chunks,
                            start_pos=chunk_start,
                            end_pos=chunk_end
                        )
                        chunks.append(chunk_result)
                        
                        json.dump({
                            "context": chunk,
                            "source_file": str(file.name),
                            "chunk_index": local_chunks,
                            "start_pos": chunk_start,
                            "end_pos": chunk_end
                        }, out_f, ensure_ascii=False)
                        out_f.write("\n")

                        if progress_callback:
                            progress_callback(
                                context_count,
                                num_contexts,
                                f"✅ Contexto {context_count}/{num_contexts} de '{file.name}'"
                            )

                    # Mover al siguiente chunk con solapamiento
                    if chunk_end >= len(text):
                        break
                    
                    # Calcular siguiente posición considerando overlap
                    if overlap > 0:
                        index = chunk_end - overlap
                    else:
                        index = chunk_end
                    
                    # Evitar bucles infinitos
                    if index <= last_chunk_end:
                        index = last_chunk_end + 1
                    last_chunk_end = chunk_end

                if progress_callback:
                    progress_callback(
                        context_count,
                        num_contexts,
                        f"📄 Procesado '{file.name}': {local_chunks} chunk(s) extraídos"
                    )
                file_count += 1

                if context_count >= num_contexts:
                    if progress_callback:
                        progress_callback(context_count, num_contexts, "✅ Límite alcanzado. Proceso finalizado.")
                    break

            except Exception as e:
                if progress_callback:
                    progress_callback(context_count, num_contexts, f"❌ Error leyendo {file.name}: {e}")
                continue

    if progress_callback:
        progress_callback(
            context_count,
            num_contexts,
            f"📦 {context_count} contextos guardados en '{output_file}' desde {file_count} archivos."
        )

    return chunks
