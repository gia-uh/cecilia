# IFT Tool - Generador de Datasets para Instruction Fine-Tuning

Herramienta completa para generar sintéticamente datasets de conversaciones pregunta-respuesta a partir de un corpus de datos textuales, diseñada específicamente para crear datos de entrenamiento para modelos de lenguaje mediante instruction fine-tuning.

## 🚀 Características Principales

### ✨ Interfaz Web Completa
- **Dashboard de Configuración**: Gestión visual de todos los parámetros
- **Monitor en Tiempo Real**: Seguimiento del pipeline con barras de progreso y métricas
- **Curaduría Interactiva**: Validación y edición manual de resultados
- **Análisis y Visualización**: Estadísticas y gráficos del dataset generado

### 🔧 Funcionalidades Técnicas

1. **Extracción de Contextos con Solapamiento Semántico**
   - Chunking inteligente que respeta límites de oraciones y párrafos
   - Solapamiento configurable para mantener contexto entre chunks
   - Visualización del proceso de chunking

2. **Clasificación Automática**
   - Filtrado de contextos relevantes antes de generar conversaciones
   - Prompt de clasificación personalizable
   - Ahorro de costos al procesar solo contenido relevante

3. **Generación de Conversaciones**
   - Generación de múltiples pares pregunta-respuesta por contexto
   - Soporte para OpenAI, Fireworks AI y **OpenRouter**
   - Acceso a múltiples modelos (GPT-4, Claude, Llama, Mistral, Gemini, etc.)
   - Control de hiperparámetros (temperature, top_p, max_tokens)

4. **Human-in-the-Loop**
   - Edición directa de preguntas y respuestas generadas
   - Sistema de aprobación/rechazo de ejemplos
   - Filtrado y búsqueda en el dataset

5. **Gestión de Costos**
   - Cálculo en tiempo real de tokens consumidos
   - Estimación de costos monetarios
   - Visualización de distribución de tokens

6. **Resume Capability**
   - Continuar procesamiento desde el último punto
   - Detección automática de archivos intermedios
   - No perder progreso en caso de interrupción

## 📦 Instalación

### Requisitos
- Python 3.10 o superior
- [uv](https://github.com/astral-sh/uv) (recomendado) o pip
- Acceso a internet (para APIs de LLM)

### Instalación con uv (Recomendado)

`uv` es un gestor de paquetes Python rápido y moderno. Si no lo tienes instalado:

```bash
# Instalar uv (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# O con pip
pip install uv
```

**Pasos de instalación:**

1. **Navegar al directorio del proyecto**
```bash
cd ift_tool
```

2. **Crear entorno virtual con uv**
```bash
uv venv
```

3. **Activar el entorno virtual**
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. **Instalar dependencias**
```bash
uv pip install -r requirements.txt
```

5. **Verificar instalación**
```bash
python -c "import streamlit; import openai; import pydantic; print('✅ Dependencias instaladas correctamente')"
```

### Instalación con pip (Alternativa)

Si prefieres usar pip tradicional:

1. **Navegar al directorio del proyecto**
```bash
cd ift_tool
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar el entorno virtual**
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### Configurar variables de entorno (opcional)
Crea un archivo `.env` en la raíz del proyecto:
```env
# OpenAI
OPENAI_API_KEY=tu_api_key_aqui

# Fireworks AI
FIREWORKS_API_KEY=tu_api_key_aqui
FIREWORKS_API_BASE=https://api.fireworks.ai/inference/v1
FIREWORKS_MODEL=accounts/fireworks/models/llama-v2-7b-chat

# OpenRouter (opcional - permite acceso a múltiples modelos)
OPENROUTER_API_KEY=sk-or-v1-tu_api_key_aqui
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4-turbo
```

**Nota**: Para más información sobre OpenRouter, consulta `OPENROUTER_SETUP.md`

## 🎯 Uso

### Modo Interfaz Web (Recomendado)

**Importante:** Asegúrate de tener el entorno virtual activado antes de ejecutar la aplicación.

1. **Activar el entorno virtual (si no está activo)**
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

2. **Iniciar la aplicación Streamlit**
```bash
streamlit run app.py
```

3. **Abrir en el navegador**
La aplicación se abrirá automáticamente en `http://localhost:8501`

4. **Configurar parámetros**
   - **Tab Configuración**: Establece rutas, parámetros de chunking, modelo LLM y autor
   - Guarda la configuración para reutilizarla

5. **Ejecutar procesamiento**
   - **Tab Ejecución**: Inicia el pipeline y monitorea el progreso
   - Observa las métricas de tokens y costo en tiempo real

6. **Curar resultados**
   - **Tab Curaduría**: Revisa, edita y aprueba los ejemplos generados
   - Exporta el dataset final

7. **Analizar resultados**
   - **Tab Análisis**: Visualiza estadísticas y distribuciones

### Modo Línea de Comandos (Legacy)

**Importante:** Asegúrate de tener el entorno virtual activado.

1. **Activar el entorno virtual (si no está activo)**
```bash
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate  # Windows
```

2. **Ejecutar el script**
```bash
python main.py
```

## 📁 Estructura del Proyecto

```
ift_tool/
├── app.py                  # Aplicación Streamlit principal
├── config.py               # Gestión de configuración
├── extract_contexts.py     # Extracción de contextos con solapamiento
├── llm.py                  # Cliente de LLM mejorado
├── processor.py             # Procesador principal de datasets
├── cost_calculator.py      # Cálculo de costos
├── model.py                # Modelos Pydantic
├── prompts.py              # Plantillas de prompts
├── json_formatter.py       # Formateador de salida (legacy)
├── main.py                 # Script principal (legacy)
├── data/
│   └── classify.py         # Clasificación de archivos médicos
├── results/                # Directorio de salida
└── requirements.txt        # Dependencias
```

## ⚙️ Configuración

### Parámetros de Chunking

- **chunk_size**: Tamaño de cada fragmento en caracteres (100-10000)
- **overlap**: Solapamiento entre chunks consecutivos (0-1000)
- **num_contexts**: Número máximo de contextos a extraer

### Configuración del Modelo

- **Provider**: OpenAI o Fireworks AI
- **Modelo**: Selección del modelo específico
- **Temperature**: Control de aleatoriedad (0.0-2.0)
- **Top-p**: Nucleus sampling (0.0-1.0)
- **Max Tokens**: Límite de tokens en respuestas

### Información del Autor

- **Nombre**: Nombre del autor del dataset
- **Institución**: Institución del autor
- **Email**: Email de contacto

## 📊 Formatos de Salida

### Archivo Intermedio (JSONL)
```json
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
    "label": ["tag1", "tag2"]
  },
  "usage": {
    "classification": {...},
    "generation": {...}
  }
}
```

### Dataset Final (JSON)
```json
[
  {
    "id": "uuid",
    "contact_info": {
      "name": "...",
      "institution": "...",
      "email": "..."
    },
    "example_type": "Pregunta",
    "tags": ["tag1", "tag2"],
    "context": "...",
    "created_at": "2024-01-01T12:00:00",
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  }
]
```

## 🔍 Características Avanzadas

### Solapamiento Semántico

El sistema ahora implementa chunking inteligente que:
- Respeta límites de oraciones (busca puntos seguidos de espacio)
- Respeta límites de párrafos (busca saltos de línea dobles)
- Mantiene un tamaño mínimo de chunk (30% del tamaño objetivo)
- Visualiza gráficamente el solapamiento entre chunks

### Cálculo de Costos

El sistema calcula automáticamente:
- Tokens de entrada (prompt)
- Tokens de salida (completion)
- Costo estimado en USD según el modelo utilizado

Precios actualizados para modelos comunes:
- GPT-4 Turbo: $0.01/1K input, $0.03/1K output
- GPT-4: $0.03/1K input, $0.06/1K output
- GPT-3.5 Turbo: $0.0005/1K input, $0.0015/1K output

### Resume Capability

Si el procesamiento se interrumpe:
1. El sistema detecta archivos intermedios existentes
2. Ofrece continuar desde el último punto procesado
3. Cuenta automáticamente los ejemplos ya generados
4. Continúa desde el siguiente contexto pendiente

## 🐛 Solución de Problemas

### Error: "API Key no configurada"
- Configura la API key en el tab de Configuración → Modelo LLM
- O crea un archivo `.env` con las variables necesarias

### Error: "Directorio no encontrado"
- Verifica que la ruta a la carpeta de datos sea correcta
- Asegúrate de que la carpeta contenga archivos .txt o .md

### La aplicación se congela durante el procesamiento
- Esto es normal, el procesamiento es secuencial
- Monitorea el progreso en el tab de Ejecución
- Los logs muestran el estado actual

## 📝 Notas

- El procesamiento es secuencial para evitar rate limiting
- Los resultados se guardan incrementalmente (no se pierden datos)
- La curaduría permite filtrar y editar antes de exportar
- El formato final es compatible con estándares de datasets de fine-tuning

## 🤝 Contribuciones

Las mejoras y sugerencias son bienvenidas. El código está estructurado modularmente para facilitar extensiones.

## 📄 Licencia

Ver archivo LICENSE en el repositorio principal.

## 👥 Autores

- Deborah Famadas Rodríguez
- Universidad de La Habana

---

**Versión:** 2.0.0  
**Última actualización:** 2024
