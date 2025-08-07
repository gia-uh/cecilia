import json
from deep_translator import GoogleTranslator


def chunk_text(text, max_length=4500):
    """
    Splits the input text into chunks of max_length or less,
    preferably breaking at sentence ends (period + space).
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Consider slice up to max_length ahead
        end = start + max_length
        if end >= text_length:
            # Last chunk
            chunks.append(text[start:])
            break

        # Try to break at last period before end
        slice_ = text[start:end]
        last_period = slice_.rfind('. ')
        if last_period == -1:
            # No period found, just break at max_length
            last_period = max_length - 1

        # Adjust end to break at period + space
        end = start + last_period + 1  # +1 to include the period
        chunks.append(text[start:end].strip())
        start = end + 1  # Skip the space after period

    return chunks


def translate_jsonl_file(input_file, output_file, target_language='es'):
    """
    Reads a JSONL file where each line is a JSON object containing a 'conversations' list,
    translates each text (splitting into chunks if longer than 4500 chars) using deep_translator,
    and writes a new JSONL file with the 'conversations' replaced by their translations.
    """
    translator = GoogleTranslator(source='auto', target=target_language)

    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            conversations = data.get('conversations', [])
            translated_texts = []

            for text in conversations:
                try:
                    if len(text) <= 4500:
                        # Translate directly if short enough
                        translation = translator.translate(text)
                    else:
                        # Break long text into chunks, translate each, then join
                        chunks = chunk_text(text, max_length=4500)
                        translated_chunks = [translator.translate(chunk) for chunk in chunks]
                        translation = ' '.join(translated_chunks)
                    translated_texts.append(translation)
                except Exception as e:
                    print(f"Error translating text: {text[:30]}... Error: {e}")
                    translated_texts.append(text)  # Keep original if fails

            # Prepare output JSON with translations
            output_data = {
                **data,
                'conversations': translated_texts
            }

            fout.write(json.dumps(output_data, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    input_filename = 'train.jsonl'              # Your input JSONL file
    output_filename = 'train_translated.jsonl'  # File to save translations

    translate_jsonl_file(input_filename, output_filename, target_language='es')
    print(f"Translation completed and saved to {output_filename}")
