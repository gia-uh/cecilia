import json
import os
import random
from pathlib import Path

from anyio import Path as AnyIOPath
from dotenv import load_dotenv
from extract_contexts import extract_contexts
from model import Classifier, ContactInfo, Conversation, Entry, TagEnum, YesNoEnum
from llm import OpenAIGenerator
from prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION
from typing import Annotated, List, Optional, Dict, Any
from typer import Option, Typer

load_dotenv()

app = Typer()


def calculate_document_score(ranking_entry: Dict[str, Any]) -> Optional[float]:
    """
    Calculate the score of a document from its ranking entry.

    Args:
        ranking_entry: A dictionary containing document ranking information
                      (e.g., {"path": "...", "score": ..., "details": {...}})

    Returns:
        The calculated score for the document, or None if not implemented
    """
    return ranking_entry.get("score", 0.0)


@app.command("run")
def main(
    topics: Annotated[List[TagEnum], Option("--topic", "-t")],
    author_name: Annotated[str, Option("--author-name", "-n")],
    author_institution: Annotated[str, Option("--author-institution", "-i")],
    author_email: Annotated[str, Option("--author-email", "-e")],
    context_text: Annotated[str, Option("--context", "-c")] = "",
    use_local: Annotated[bool, Option("-l")] = False,
    ranking_file: Annotated[Optional[str], Option("--ranking-file", "-r")] = None,
):
    file_paths = None

    if ranking_file:
        print(f"📊 Cargando archivo de ranking: {ranking_file}")
        with open(ranking_file, "r", encoding="utf-8") as f:
            ranking_data = json.load(f)

        ranking = ranking_data.get("ranking", [])
        print(f"📈 Total de documentos en ranking: {len(ranking)}")

        # Calculate scores for all documents
        scored_documents = []
        for entry in ranking:
            score = calculate_document_score(entry)
            scored_documents.append((entry, score))

        # Sort by score (descending) and select top 100
        scored_documents.sort(key=lambda x: x[1], reverse=True)
        top_documents = [entry for entry, _ in scored_documents[:100]]

        # Extract file paths from selected documents
        file_paths = [Path(entry["path"].replace("\\", "/")) for entry in top_documents]

        threshold = (
            scored_documents[99][1]
            if len(scored_documents) >= 100
            else scored_documents[-1][1]
        )
        print(f"📊 Top 100 documentos seleccionados (threshold = {threshold:.2f})")
        print(f"✅ Archivos seleccionados para procesamiento: {len(top_documents)}")

    extract_contexts(
        data_folder="data/medicina",
        num_contexts=10000,
        output_file="results/contexts.jsonl",
        chunk_size=2000,
        file_paths=file_paths,
    )
    with open("results/contexts.jsonl", "r", encoding="utf-8") as f:
        contexts = [json.loads(line)["context"] for line in f]

    # Shuffle contexts for random order
    random.shuffle(contexts)

    generator = OpenAIGenerator(use_fireworks=not use_local)
    output_path = "results/conversations"
    os.makedirs(output_path, exist_ok=True)
    topic = ", ".join([tag.value for tag in topics])

    for i, ctx in enumerate(contexts, 1):
        try:
            # classification_prompt = CLASSIFICATION.format(context=ctx, topic=topic)
            # response = generator.generate_json(
            #     prompt=classification_prompt, json_model=Classifier
            # )
            # classification = response.choices[0].message.parsed.classification
            # print(f"Clasificación del contexto {i}: {classification}")

            # if classification == YesNoEnum.YES:
            if True:
                prompt = INSTRUCTIONS_GENERATOR.format(topic=topic, context=ctx)
                response = generator.generate_json(
                    prompt=prompt, json_model=Conversation
                )
                result = response.choices[0].message.parsed

                info = Entry(
                    messages=result.messages,
                    context=context_text,
                    tags=topics,
                    contact_info=ContactInfo(
                        name=author_name,
                        institution=author_institution,
                        email=author_email,
                    ),
                )

                with open(
                    AnyIOPath(output_path) / f"{info.id}.json", "a", encoding="utf-8"
                ) as out_file:
                    out_file.write(info.model_dump_json(ensure_ascii=False) + "\n")
                    out_file.flush()

                print(f"✅ Ejemplo {i} guardado.")
            else:
                print(f"🔶 Contexto {i} no relevante. Omitido.")

        except Exception as e:
            print(f"❌ Error al procesar contexto {i}: {e}")
            raise


if __name__ == "__main__":
    app()
