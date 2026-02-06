# Informe Detallado del Software: IFT Tool
## Herramienta de Generación Sintética de Datasets para Instruction Fine-Tuning

---

## 1. Resumen Ejecutivo

**IFT Tool** es una herramienta de Python diseñada para generar sintéticamente datasets de conversaciones pregunta-respuesta a partir de un corpus de datos textuales, específicamente orientada a la creación de datos de entrenamiento para modelos de lenguaje mediante instruction fine-tuning. El sistema procesa documentos de texto (markdown o texto plano), extrae contextos relevantes, los clasifica según un tema específico, y utiliza modelos de lenguaje grandes (LLMs) para generar conversaciones realistas entre usuarios y asistentes.

**Versión:** 0.1.0  
**Lenguaje:** Python 3.10+  
**Propósito:** Generación sintética de datasets para fine-tuning de modelos de lenguaje

---

## 2. Arquitectura del Sistema

### 2.1 Estructura de Directorios

```
ift_tool/
├── data/
│   ├── classify.py          # Clasificación de archivos médicos
│   └── medicina/            # Carpeta de datos médicos (referencia)
├── results/                 # Directorio de salida para resultados
├── extract_contexts.py      # Extracción de contextos del corpus
├── json_formatter.py        # Formateo de conversaciones a formato estándar
├── llm.py                   # Cliente para LLMs (OpenAI/Fireworks)
├── main.py                  # Punto de entrada principal
├── model.py                 # Modelos Pydantic para validación
├── prompts.py               # Plantillas de prompts para LLMs
├── pyproject.toml           # Configuración del proyecto
└── requirements.txt         # Dependencias del proyecto
```

### 2.2 Flujo de Procesamiento

El sistema sigue un pipeline de procesamiento en 4 etapas principales:

1. **Extracción de Contextos** (`extract_contexts.py`)
2. **Clasificación de Relevancia** (`main.py` - Clasificador)
3. **Generación de Conversaciones** (`main.py` - Generador)
4. **Formateo y Normalización** (`json_formatter.py`)

---

## 3. Componentes Principales

### 3.1 `extract_contexts.py` - Extracción de Contextos

**Propósito:** Procesa archivos de texto y los divide en fragmentos (chunks) de tamaño configurable.

**Funcionalidad:**
- Lee archivos `.txt` y `.md` de un directorio especificado
- Divide cada archivo en chunks de tamaño fijo (`chunk_size`)
- Guarda los contextos en formato JSONL (JSON Lines)
- Controla el número máximo de contextos a extraer

**Parámetros:**
- `data_folder`: Directorio con archivos fuente
- `num_contexts`: Número máximo de contextos a extraer
- `output_file`: Archivo de salida (JSONL)
- `chunk_size`: Tamaño de cada chunk en caracteres (default: 1000)

**Características:**
- ✅ Procesamiento recursivo de archivos
- ✅ Manejo de errores por archivo individual
- ✅ Validación de archivos vacíos
- ✅ Progreso visual con emojis
- ✅ Formato JSONL para procesamiento eficiente

**Limitaciones:**
- Los chunks se dividen por posición de caracteres, no por límites semánticos (puede cortar palabras/oraciones)
- No hay solapamiento entre chunks
- No valida la calidad del contenido extraído

### 3.2 `data/classify.py` - Clasificación de Archivos Médicos

**Propósito:** Utilidad auxiliar para clasificar archivos markdown según contenido médico.

**Funcionalidad:**
- Busca archivos `.md` recursivamente
- Evalúa si el contenido contiene palabras clave médicas
- Copia archivos médicos a un directorio de destino

**Palabras Clave Médicas:**
```python
["salud", "medicina", "síntoma", "enfermedad", "tratamiento",
 "diagnóstico", "hospital", "clínica", "doctor", "paciente",
 "prescripción", "vacuna", "epidemia", "infección", "virus",
 "bacteria", "terapia", "cirugía", "farmacología"]
```

**Limitaciones:**
- Clasificación basada únicamente en presencia de palabras clave (muy básica)
- No utiliza técnicas avanzadas de NLP
- Puede generar falsos positivos/negativos

### 3.3 `llm.py` - Cliente de LLM

**Propósito:** Abstracción para interactuar con modelos de lenguaje (OpenAI API o Fireworks AI).

**Clase Principal:** `OpenAIGenerator`

**Métodos:**
1. **`generate_text(prompt, model_name, **kwargs)`**
   - Genera texto libre a partir de un prompt
   - Retorna el contenido de la respuesta

2. **`generate_json(prompt, json_model, model, **kwargs)`**
   - Genera respuestas estructuradas en formato JSON
   - Utiliza `structured_outputs` de OpenAI (beta)
   - Valida la respuesta contra un modelo Pydantic
   - Temperatura fija en 0 (determinístico)

**Configuración:**
- Soporta OpenAI estándar y Fireworks AI
- Variables de entorno requeridas:
  - `OPENAI_API_KEY` o `FIREWORKS_API_KEY`
  - `FIREWORKS_API_BASE` (para Fireworks)
  - `FIREWORKS_MODEL` (modelo por defecto)

**Características:**
- ✅ Validación de tipos con Pydantic
- ✅ Soporte para múltiples proveedores
- ✅ Parsing estructurado de respuestas

**Limitaciones:**
- No hay manejo de rate limiting
- No hay retry logic para errores de API
- No hay logging detallado de llamadas
- Imprime la respuesta completa (puede ser verboso)

### 3.4 `prompts.py` - Plantillas de Prompts

**Contiene dos prompts principales:**

#### 3.4.1 `INSTRUCTIONS_GENERATOR`
**Propósito:** Generar conversaciones pregunta-respuesta basadas en un contexto.

**Estructura:**
- Recibe `topic` y `context` como parámetros
- Instruye al LLM a generar al menos 3 intercambios Q&A
- Requiere que las respuestas sean basadas únicamente en el contexto
- Incluye ejemplo de formato esperado

**Formato de Salida Esperado:**
```json
{
  "question_one": "...",
  "answer_one": "...",
  "question_two": "...",
  "answer_two": "...",
  "question_three": "...",
  "answer_three": "...",
  "label": ["tag1", "tag2"]
}
```

#### 3.4.2 `CLASSIFICATION`
**Propósito:** Clasificar si un contexto es relevante para un tema específico.

**Estructura:**
- Recibe `context` y `topic` como parámetros
- Retorna "Yes" o "No"
- Simple clasificación binaria

### 3.5 `model.py` - Modelos de Datos

**Modelos Pydantic definidos:**

#### `ContactInfo`
```python
{
  "name": str,
  "institution": str,
  "email": EmailStr
}
```

#### `Message`
```python
{
  "role": Literal["user", "assistant"],
  "content": str
}
```

#### `QAExample`
Modelo completo para un ejemplo de Q&A:
```python
{
  "id": UUID,
  "contact_info": ContactInfo,
  "example_type": Literal["Pregunta"],
  "tags": List[str],
  "context": str,
  "created_at": datetime,
  "messages": List[Message]
}
```

**Uso:** Validación de estructura de datos y serialización JSON.

### 3.6 `main.py` - Orquestador Principal

**Propósito:** Coordina todo el pipeline de generación de datasets.

**Flujo de Ejecución:**

1. **Extracción de Contextos**
   ```python
   extract_contexts(
       data_folder="data/medicina",
       num_contexts=20,
       output_file="results/ecured_contexts.json",
       chunk_size=2000
   )
   ```

2. **Carga de Contextos**
   - Lee el archivo JSONL generado
   - Extrae solo el campo "context" de cada línea

3. **Procesamiento por Contexto**
   Para cada contexto:
   - **Clasificación:** Evalúa si es relevante al tema ("salud, medicina")
   - **Generación:** Si es relevante, genera conversaciones Q&A
   - **Guardado:** Almacena resultados en JSONL

4. **Formateo Final**
   - Transforma el JSONL a formato JSON estructurado
   - Aplica metadatos y formato estándar

**Modelos Pydantic Utilizados:**

- `Conversation`: Estructura para las 3 preguntas/respuestas generadas
- `Classifier`: Modelo para la clasificación binaria
- `YesNoEnum`: Enum para "Yes"/"No"

**Características:**
- ✅ Procesamiento secuencial con manejo de errores por contexto
- ✅ Guardado incremental (append mode) para no perder datos
- ✅ Logging visual del progreso
- ✅ Clasificación previa para filtrar contextos irrelevantes

**Limitaciones:**
- Procesamiento secuencial (no paralelo)
- No hay persistencia de estado (si falla, reinicia desde el inicio)
- Tema hardcodeado en el código
- No hay validación de calidad de las conversaciones generadas

### 3.7 `json_formatter.py` - Formateador de Salida

**Propósito:** Transforma el formato interno a un formato estándar de dataset.

**Funcionalidad:**
- Lee archivo JSONL de conversaciones generadas
- Transforma cada entrada al formato `QAExample`
- Agrega metadatos:
  - UUID único por ejemplo
  - Información de contacto del autor
  - Timestamp de creación
  - Tags y contexto original

**Datos del Autor (Hardcodeados):**
- Nombre: "Deborah Famadas Rodríguez"
- Email: "deborahfamadas@gmail.com"
- Institución: "Universidad de La Habana"

**Formato de Salida:**
Array JSON con objetos `QAExample` formateados.

**Características:**
- ✅ Generación de UUIDs únicos
- ✅ Estructura de mensajes alternada (user/assistant)
- ✅ Preservación del contexto original
- ✅ Formato JSON indentado legible

---

## 4. Dependencias y Tecnologías

### 4.1 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `openai` | >=1.82.1 | Cliente para APIs de OpenAI/Fireworks |
| `pydantic` | >=2.11.5 | Validación de datos y modelos |
| `python-dotenv` | >=1.1.0 | Gestión de variables de entorno |
| `pyyaml` | >=6.0.2 | (No utilizado actualmente) |

### 4.2 Tecnologías Utilizadas

- **Python 3.10+**: Lenguaje base
- **Pydantic v2**: Validación de esquemas y parsing estructurado
- **OpenAI API**: Generación de texto y JSON estructurado
- **Fireworks AI**: Alternativa a OpenAI (configurable)
- **JSON/JSONL**: Formatos de datos

---

## 5. Análisis de Funcionalidad

### 5.1 Fortalezas

1. **Arquitectura Modular**
   - Separación clara de responsabilidades
   - Componentes reutilizables
   - Fácil mantenimiento

2. **Validación Robusta**
   - Uso de Pydantic para validación de tipos
   - Parsing estructurado con LLMs
   - Prevención de errores de formato

3. **Flexibilidad de Proveedores**
   - Soporte para OpenAI y Fireworks AI
   - Fácil cambio de proveedor

4. **Procesamiento Incremental**
   - Guardado en modo append
   - No se pierden datos si el proceso se interrumpe parcialmente

5. **Clasificación Previa**
   - Filtra contextos irrelevantes antes de generar
   - Ahorra costos de API
   - Mejora calidad del dataset

### 5.2 Limitaciones y Áreas de Mejora

1. **Procesamiento Secuencial**
   - No aprovecha paralelización
   - Lento para grandes volúmenes
   - **Mejora sugerida:** Implementar procesamiento asíncrono/paralelo

2. **Manejo de Errores Básico**
   - Solo captura excepciones genéricas
   - No hay retry logic para errores de API
   - No maneja rate limiting
   - **Mejora sugerida:** Implementar retry con exponential backoff

3. **Configuración Hardcodeada**
   - Tema, rutas y parámetros fijos en código
   - **Mejora sugerida:** Archivo de configuración (YAML/JSON)

4. **Chunking Simple**
   - División por caracteres sin considerar límites semánticos
   - Puede cortar palabras/oraciones
   - **Mejora sugerida:** Chunking inteligente con solapamiento

5. **Falta de Validación de Calidad**
   - No valida calidad de conversaciones generadas
   - No detecta alucinaciones o información fuera del contexto
   - **Mejora sugerida:** Validación automática de calidad

6. **Clasificación Básica**
   - `classify.py` usa solo palabras clave
   - **Mejora sugerida:** Usar embeddings o modelos de clasificación

7. **Sin Persistencia de Estado**
   - Si falla, reinicia desde el inicio
   - **Mejora sugerida:** Checkpointing y resume capability

8. **Logging Limitado**
   - Solo prints a consola
   - **Mejora sugerida:** Sistema de logging estructurado

9. **Metadatos Hardcodeados**
   - Información del autor en código
   - **Mejora sugerida:** Configuración externa

10. **Falta de Tests**
    - No hay tests unitarios ni de integración
    - **Mejora sugerida:** Suite de tests completa

---

## 6. Flujo de Datos Detallado

### 6.1 Pipeline Completo

```
Archivos .txt/.md
    ↓
[extract_contexts.py]
    ↓
JSONL: {"context": "..."}
    ↓
[main.py - Carga]
    ↓
Lista de contextos (strings)
    ↓
Para cada contexto:
    ↓
[Clasificación con LLM]
    ↓
¿Es relevante? → NO → Omitir
    ↓ SÍ
[Generación de conversaciones con LLM]
    ↓
Conversation object (Pydantic)
    ↓
JSONL: {"id": 1, "classification": "Yes", "context": "...", "questions": {...}}
    ↓
[json_formatter.py]
    ↓
JSON: [QAExample, QAExample, ...]
```

### 6.2 Formato de Datos

**Entrada (Corpus):**
- Archivos de texto plano o markdown
- Contenido en español (especializado en medicina/salud)

**Intermedio (Contextos):**
```jsonl
{"context": "Texto del contexto extraído..."}
```

**Intermedio (Conversaciones):**
```jsonl
{
  "id": 1,
  "classification": "Yes",
  "context": "...",
  "questions": {
    "question_one": "...",
    "answer_one": "...",
    "question_two": "...",
    "answer_two": "...",
    "question_three": "...",
    "answer_three": "...",
    "label": ["salud", "medicina"]
  }
}
```

**Salida Final:**
```json
[
  {
    "id": "uuid-here",
    "contact_info": {
      "name": "Deborah Famadas Rodríguez",
      "institution": "Universidad de La Habana",
      "email": "deborahfamadas@gmail.com"
    },
    "example_type": "Pregunta",
    "tags": ["salud", "medicina"],
    "context": "...",
    "created_at": "2024-01-01 12:00:00",
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."},
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."},
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  }
]
```

---

## 7. Casos de Uso

### 7.1 Uso Principal
Generar datasets de instrucción para fine-tuning de modelos de lenguaje en dominios específicos (ej: medicina, salud).

### 7.2 Casos de Uso Secundarios
1. **Clasificación de Corpus:** Filtrar documentos por tema
2. **Extracción de Contextos:** Dividir documentos grandes en fragmentos manejables
3. **Generación de Datos Sintéticos:** Crear ejemplos de entrenamiento sin anotación manual

---

## 8. Consideraciones de Seguridad y Privacidad

### 8.1 Seguridad
- ✅ Variables de entorno para API keys (no hardcodeadas)
- ⚠️ No hay validación de inputs de archivos (riesgo de path traversal)
- ⚠️ No hay sanitización de contenido antes de enviar a APIs externas

### 8.2 Privacidad
- ⚠️ El contenido se envía a APIs externas (OpenAI/Fireworks)
- ⚠️ No hay anonimización de datos sensibles
- ⚠️ Metadatos del autor incluidos en cada ejemplo generado

### 8.3 Recomendaciones
- Validar y sanitizar paths de archivos
- Implementar anonimización para datos sensibles
- Revisar políticas de privacidad de APIs utilizadas
- Considerar procesamiento local si los datos son confidenciales

---

## 9. Rendimiento y Escalabilidad

### 9.1 Rendimiento Actual
- **Procesamiento:** Secuencial, ~1 contexto/segundo (depende de API)
- **Memoria:** Bajo consumo (procesa un contexto a la vez)
- **Almacenamiento:** JSONL eficiente para grandes volúmenes

### 9.2 Escalabilidad
- ⚠️ Limitado por procesamiento secuencial
- ⚠️ Sin límites de rate limiting implementados
- ✅ Formato JSONL permite procesamiento streaming

### 9.3 Optimizaciones Sugeridas
1. Procesamiento asíncrono/paralelo
2. Batching de requests a API
3. Caching de clasificaciones similares
4. Checkpointing para resume

---

## 10. Mantenibilidad y Extensibilidad

### 10.1 Mantenibilidad
- ✅ Código bien estructurado y modular
- ✅ Separación de responsabilidades clara
- ⚠️ Falta documentación inline
- ⚠️ No hay tests

### 10.2 Extensibilidad
- ✅ Fácil agregar nuevos proveedores de LLM
- ✅ Fácil modificar formato de salida
- ✅ Fácil agregar nuevos tipos de prompts
- ⚠️ Configuración hardcodeada limita flexibilidad

---

## 11. Recomendaciones de Mejora

### 11.1 Prioridad Alta
1. **Configuración Externa**
   - Archivo YAML/JSON para parámetros
   - Variables de entorno para secrets

2. **Manejo de Errores Robusto**
   - Retry logic con exponential backoff
   - Manejo de rate limiting
   - Logging estructurado

3. **Procesamiento Paralelo**
   - Async/await para llamadas a API
   - Procesamiento concurrente de contextos

### 11.2 Prioridad Media
4. **Chunking Inteligente**
   - División por límites semánticos
   - Solapamiento entre chunks

5. **Validación de Calidad**
   - Detección de alucinaciones
   - Validación de coherencia
   - Métricas de calidad

6. **Checkpointing**
   - Guardar estado de progreso
   - Capacidad de resume

### 11.3 Prioridad Baja
7. **Tests Unitarios**
   - Coverage de funciones principales
   - Tests de integración

8. **Documentación**
   - Docstrings en funciones
   - README con ejemplos
   - Guía de uso

9. **CLI Mejorado**
   - Argumentos de línea de comandos
   - Interfaz más amigable

---

## 12. Conclusión

**IFT Tool** es una herramienta funcional y bien estructurada para generar datasets sintéticos de instruction fine-tuning. Su arquitectura modular y uso de tecnologías modernas (Pydantic, OpenAI API) la hacen robusta y mantenible. Sin embargo, presenta limitaciones en escalabilidad, manejo de errores y configurabilidad que deberían abordarse para uso en producción.

**Evaluación General:**
- **Funcionalidad:** ⭐⭐⭐⭐ (4/5) - Cumple su propósito principal
- **Código:** ⭐⭐⭐⭐ (4/5) - Bien estructurado pero falta documentación
- **Escalabilidad:** ⭐⭐ (2/5) - Limitada por procesamiento secuencial
- **Robustez:** ⭐⭐⭐ (3/5) - Manejo de errores básico
- **Mantenibilidad:** ⭐⭐⭐⭐ (4/5) - Buena estructura, falta tests

**Recomendación:** Herramienta adecuada para prototipado y uso en investigación. Requiere mejoras antes de uso en producción a gran escala.

---

## 13. Información Técnica Adicional

### 13.1 Requisitos del Sistema
- Python 3.10 o superior
- Acceso a internet (para APIs)
- Variables de entorno configuradas:
  - `OPENAI_API_KEY` o `FIREWORKS_API_KEY`
  - `FIREWORKS_API_BASE` (si usa Fireworks)
  - `FIREWORKS_MODEL` (modelo por defecto)

### 13.2 Instalación
```bash
pip install -r requirements.txt
# o
pip install -e .
```

### 13.3 Uso Básico
```bash
python main.py
```

### 13.4 Archivos de Salida
- `results/ecured_contexts.json`: Contextos extraídos (JSONL)
- `results/ecured_conversations.jsonl`: Conversaciones generadas (JSONL)
- `results/formatted_conversations.json`: Dataset final formateado (JSON)

---

**Fecha de Análisis:** 2024  
**Versión Analizada:** 0.1.0  
**Analista:** AI Assistant
