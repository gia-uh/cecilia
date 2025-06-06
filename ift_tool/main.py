import json
from extract_contexts import extract_contexts
from llm import OpenAIGenerator
from prompts import INSTRUCTIONS_GENERATOR, CLASSIFICATION
from pydantic import BaseModel, Field
from typing import List
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


def main():
    extract_contexts(data_folder="data/ecured/salud", num_contexts=1000, output_file="results/ecured_contexts.json", chunk_size=2000)
    with open("results/ecured_contexts.json", "r", encoding="utf-8") as f:
        contexts = [json.loads(line)["context"] for line in f]

    generator = OpenAIGenerator(use_fireworks=True)
    output_path = "results/ecured_conversations.jsonl"
    log_path = "results/logs.jsonl"
    topic = "salud, medicina"

    for i, ctx in enumerate(contexts, 1):
        try:
            classification_prompt = CLASSIFICATION.format(context=ctx, topic=topic)
            response = generator.generate_json(prompt=classification_prompt, json_model=Classifier)
            classification = response.choices[0].message.parsed.classification
            print(f"Clasificación del contexto {i}: {classification}")


            with open(log_path, "a", encoding="utf-8") as log_file:
                info = {
                    "id": i,
                    "classification": classification,
                    "context": ctx
                }
                log_file.write(json.dumps(info, ensure_ascii=False) + "\n")
                log_file.flush()

            if classification == YesNoEnum.YES:
                prompt = INSTRUCTIONS_GENERATOR.format(topic=topic, context=ctx)
                response = generator.generate_json(prompt=prompt, json_model=Conversation)
                result = response.choices[0].message.parsed.model_dump()


                with open(output_path, "a", encoding="utf-8") as out_file:
                    out_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    out_file.flush()

                print(f"✅ Ejemplo {i} guardado.")
            else:
                print(f"🔶 Contexto {i} no relevante. Omitido.")

        except Exception as e:
            print(f"❌ Error al procesar contexto {i}: {e}")


if __name__ == "__main__":
    main()
