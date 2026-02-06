"""
Script principal legacy para IFT Tool
Usa el nuevo sistema modularizado
"""
import json
from ift_tool.utils.extractor import extract_contexts
from ift_tool.utils.formatter import transform_file
from ift_tool.api.llm_client import OpenAIGenerator
from ift_tool.core.prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION
from ift_tool.core.processor import YesNoEnum, Conversation, Classifier


def main():
    """Función principal legacy - usar DatasetProcessor para nueva implementación"""
    extract_contexts(
        data_folder="data/medicina",
        num_contexts=20,
        output_file="results/ecured_contexts.json",
        chunk_size=2000
    )
    
    with open("results/ecured_contexts.json", "r", encoding="utf-8") as f:
        contexts = [json.loads(line)["context"] for line in f]

    generator = OpenAIGenerator(provider="fireworks")
    output_path = "results/ecured_conversations.jsonl"
    topic = "salud, medicina"

    for i, ctx in enumerate(contexts, 1):
        try:
            classification_prompt = CLASSIFICATION.format(context=ctx, topic=topic)
            parsed, usage = generator.generate_json(
                prompt=classification_prompt,
                json_model=Classifier
            )
            classification = parsed.classification
            print(f"Clasificación del contexto {i}: {classification}")

            if classification == YesNoEnum.YES:
                prompt = INSTRUCTIONS_GENERATOR.format(topic=topic, context=ctx)
                parsed_conv, usage_conv = generator.generate_json(
                    prompt=prompt,
                    json_model=Conversation
                )
                result = parsed_conv.model_dump()

                info = {
                    "id": i,
                    "classification": classification.value,
                    "context": ctx,
                    "questions": result
                }

                with open(output_path, "a", encoding="utf-8") as out_file:
                    out_file.write(json.dumps(info, ensure_ascii=False) + "\n")
                    out_file.flush()

                print(f"✅ Ejemplo {i} guardado.")
            else:
                print(f"🔶 Contexto {i} no relevante. Omitido.")

        except Exception as e:
            print(f"❌ Error al procesar contexto {i}: {e}")

    formatted_path = "results/formatted_conversations.json"
    transform_file(input_path=output_path, output_path=formatted_path)


if __name__ == "__main__":
    main()
