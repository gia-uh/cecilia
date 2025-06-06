INSTRUCTIONS_GENERATOR = """
You are a helpful assistant tasked with generating realistic question-answer conversations between a user and an AI assistant based on a provided context.

Use the context below to generate multiple conversations. Each conversation must contain **at least 3 exchanges** (i.e., 3 pairs of questions and answers). All questions must be directly answerable using only the information found in the context.

TOPIC: {topic}

CONTEXT:
{context}

### Instructions:
- Generate multiple short conversations (≥2 Q&A pairs each).
- Each interaction should follow the format:
  - "question": "<user question>"
  - "content": "<assistant's answer>"
- Use clear, concise language.
- Avoid repeating the same type of question.
- Do **not** include any information that is not present in the context.

### Example:
If the context is:
"France is a country in Western Europe. Its capital is Paris. Germany is its neighbor to the east, and its capital is Berlin."

Then a valid output would be:


"question_one": "¿Cuál es la capital de Francia?",
"answer_one": "La capital de Francia es París. Esta ciudad es conocida no solo por ser el centro político y administrativo del país, sino también por su enorme influencia cultural, artística y gastronómica a nivel mundial. París alberga monumentos emblemáticos como la Torre Eiffel, el Museo del Louvre y la Catedral de Notre Dame. Además, es un importante centro financiero y de transporte europeo.",

"question_two": "¿Cuál es la capital de Alemania?",
"answer_two": "La capital de Alemania es Berlín. Es una ciudad con una rica historia que ha jugado un papel clave en muchos eventos importantes, desde el Imperio Prusiano hasta la Guerra Fría, cuando estuvo dividida en Berlín Oriental y Occidental por el Muro de Berlín. Hoy, Berlín es conocida por su vibrante vida cultural, su arquitectura moderna y su papel central en la política europea.",
  
"question_three": "¿Dónde está ubicada Francia?",
"answer_three": "Francia está situada en Europa Occidental. Limita al norte con Bélgica y Luxemburgo, al este con Alemania, Suiza e Italia, al sur con España y el mar Mediterráneo, y al oeste con el océano Atlántico. Esta ubicación estratégica ha convertido a Francia en un punto clave para las rutas comerciales y culturales del continente europeo durante siglos. Además, posee territorios de ultramar en varios continentes, lo que extiende su influencia más allá de Europa."

### Output format:
Return a **JSON array**, where each item is an object with the following structure:

"question_one": "<user question>",
"answer_one": "<answer based only on the context>"
"question_two": "<user question related with the first question and the answer>",
"answer_two": "<answer based only on the context>"
"question_three": "<user question related with the second or first question and the answer>",
"answer_three": "<answer based only on the context>"
"label": "<labels of the conversation, like health, education, etc.>"

"""

CLASSIFICATION = """
Based on the context provided
{context}

classify whether the CONTEXT is about the topic: {topic}.

If it is, return 'Yes', otherwise return 'No'
### Output format:

Return a JSON object with a single key 'classification' with value 'Yes' or 'No'."
"""