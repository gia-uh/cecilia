import json
import os

from anyio import Path
from dotenv import load_dotenv
from extract_contexts import extract_contexts
from model import Classifier, ContactInfo, Conversation, Entry, TagEnum, YesNoEnum
from llm import OpenAIGenerator
from prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION
from typing import Annotated, List
from typer import Option, Typer

load_dotenv()

app = Typer()


@app.command("run")
def main(
    topics: Annotated[List[TagEnum], Option("--topic", "-t")],
    author_name: Annotated[str, Option("--author-name", "-n")],
    author_institution: Annotated[str, Option("--author-institution", "-i")],
    author_email: Annotated[str, Option("--author-email", "-e")],
    context_text: Annotated[str, Option("--context", "-c")] = "",
):
    extract_contexts(
        data_folder="data",
        num_contexts=100,
        output_file="results/contexts.json",
        chunk_size=2000,
    )
    with open("results/contexts.json", "r", encoding="utf-8") as f:
        contexts = [json.loads(line)["context"] for line in f]

    generator = OpenAIGenerator(use_fireworks=True)
    output_path = "results/conversations"
    os.makedirs(output_path, exist_ok=True)
    topic = ", ".join([tag.value for tag in topics])

    for i, ctx in enumerate(contexts, 1):
        try:
            classification_prompt = CLASSIFICATION.format(context=ctx, topic=topic)
            response = generator.generate_json(
                prompt=classification_prompt, json_model=Classifier
            )
            classification = response.choices[0].message.parsed.classification
            print(f"Clasificación del contexto {i}: {classification}")

            if classification == YesNoEnum.YES:
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
                    Path(output_path) / f"{info.id}.json", "a", encoding="utf-8"
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
