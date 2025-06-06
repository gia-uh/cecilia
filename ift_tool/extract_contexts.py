import os
import json
from pathlib import Path

def extract_contexts(data_folder: str, num_contexts: int, output_file: str = "contexts.json", chunk_size: int = 1000) -> None:
    folder = Path(data_folder)
    files = sorted([f for f in folder.iterdir() if f.suffix in ['.txt', '.md']])

    context_count = 0
    file_count = 0

    print(f"🔍 Procesando archivos en: {data_folder}")
    print(f"🎯 Meta: {num_contexts} contextos de {chunk_size} caracteres cada uno.\n")

    with open(output_file, "w", encoding="utf-8") as out_f:
        for file in files:
            try:
                with file.open("r", encoding="utf-8") as f:
                    text = f.read().strip()

                if not text:
                    print(f"⚠️  Archivo vacío: {file.name}")
                    continue

                index = 0
                local_chunks = 0

                while index < len(text) and context_count < num_contexts:
                    end = index + chunk_size
                    chunk = text[index:end].strip()

                    if chunk:
                        context_count += 1
                        local_chunks += 1
                        json.dump({"context": chunk}, out_f, ensure_ascii=False)
                        out_f.write("\n")  # Separador de líneas JSON

                        print(f"✅ Contexto {context_count}/{num_contexts} de '{file.name}'")

                    index = end
                    if end >= len(text):
                        break

                print(f"📄 Procesado '{file.name}': {local_chunks} chunk(s) extraídos\n")
                file_count += 1

                if context_count >= num_contexts:
                    print("✅ Límite alcanzado. Proceso finalizado.\n")
                    break

            except Exception as e:
                print(f"❌ Error leyendo {file.name}: {e}")
                continue

    print(f"\n📦 {context_count} contextos guardados en '{output_file}' desde {file_count} archivos.")
