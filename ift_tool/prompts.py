INSTRUCTIONS_GENERATOR = """
You are a helpful assistant tasked with generating realistic question-answer conversations between a user and an AI assistant based on what's provided.

Use the context below to generate multiple conversations. Each conversation must contain **at least 3 exchanges** (i.e., 3 pairs of questions and answers). All questions must be directly answerable using only the information found next to this prompt.

TOPIC: {topic}

CONTEXT:
{context}

### Instructions:
- Generate multiple short conversations (≥2 Q&A pairs each).
- Each interaction should follow the format:
  - "question": "<user question>"
  - "content": "<assistant's answer>"
- Use clear language.
- Avoid repeating the same type of question.
- Do **not** include any information that is not present here.
- The whole conversation must be in spanish.
- The text corresponds to cuban texts so avoid using european or other countries specific vocabulary.
- Do not talk about the context as a thing. The context is not a known thing for the reader of the conversation.

### Example:
If the context is:
"Sancti Spíritus. Provincia cubana que conserva en sus ciudades un genuino ambiente colonial. El centro histórico urbano de su ciudad capital, Sancti Spíritus, fue declarado Monumento Nacional el 10 de octubre de 1978. Y es la única provincia cubana que tiene en su territorio dos de las primeras siete villas fundadas en el Siglo XVI: Sancti Spíritus y Trinidad."

Then a valid output would be:

"messages": [
  
    "role": "user",
    "content": "¿Qué es Sancti Spíritus?"
    
    "role": "assistant",
    "content": "Sancti Spíritus es una provincia de Cuba reconocida por preservar un auténtico ambiente colonial en sus ciudades. El centro histórico de su ciudad capital fue declarado Monumento Nacional el 10 de octubre de 1978. Además, es la única provincia cubana que cuenta con dos de las primeras siete villas fundadas en el siglo XVI: Sancti Spíritus y Trinidad."
  ]
]

### Output format:
Return a **JSON object** with the following structure:

"messages": [
    "role": "user",
    "content": "<user question>"
  
    "role": "assistant",
    "content": "<answer based only on the context>"
  
]


"""

CLASSIFICATION = """
Based on the context provided
{context}

classify whether the CONTEXT is about the topic: {topic}.

If it is, return 'Yes', otherwise return 'No'
### Output format:

Return a JSON object with a single key 'classification' with value 'Yes' or 'No'."
"""
