import json
from uuid import uuid4
from datetime import datetime
from pathlib import Path

# Parámetros fijos
AUTHOR_NAME = "Deborah Famadas Rodríguez"
AUTHOR_EMAIL = "deborahfamadas@gmail.com"
AUTHOR_INSTITUTION = "Universidad de La Habana"

def transform_entry(entry):
    messages = []

    # Nombres explícitos en lugar de f-strings
    q_keys = ["question_one", "question_two", "question_three"]
    a_keys = ["answer_one", "answer_two", "answer_three"]

    for q_key, a_key in zip(q_keys, a_keys):
        if q_key in entry and a_key in entry and entry[q_key] and entry[a_key]:
            messages.append({"role": "user", "content": entry[q_key]})
            messages.append({"role": "assistant", "content": entry[a_key]})

    return {
        "id": str(uuid4()),
        "contact_info": {
            "name": AUTHOR_NAME,
            "institution": AUTHOR_INSTITUTION,
            "email": AUTHOR_EMAIL
        },
        "example_type": "Pregunta",
        "tags": entry.get("label", []),
        "context": entry.get("context", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages
    }

def transform_file(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

    transformed_entries = []

    with input_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            transformed_entries.append(transform_entry(entry))

    with output_file.open("w", encoding="utf-8") as f_out:
        json.dump(transformed_entries, f_out, ensure_ascii=False, indent=2)

    print(f"✅ Conversaciones transformadas y guardadas en: {output_path}")

if __name__ == "__main__":
    # Archivos de entrada/salida
    input_path = "results/ecured_conversations.jsonl"       # Formato JSONL de entrada
    output_path = "results/formatted_conversations.json"            # Salida como arreglo JSON
    transform_file(input_path, output_path)
