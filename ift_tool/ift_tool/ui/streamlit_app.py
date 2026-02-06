"""
Aplicación Streamlit para IFT Tool
Interfaz web completa para generación de datasets de instruction fine-tuning
"""
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path antes de cualquier import
# Esto asegura que Python pueda encontrar el módulo ift_tool
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
import json
import os
import pandas as pd
from typing import List, Dict, Any, Optional
import threading
import time
from datetime import datetime

from ift_tool.config.settings import AppConfig, ModelConfig, ChunkingConfig, AuthorInfo, ProcessingConfig
from ift_tool.utils.extractor import extract_contexts
from ift_tool.core.processor import DatasetProcessor, ProcessingStatus
from ift_tool.utils.cost import calculate_cost, format_cost, estimate_tokens
from ift_tool.core.models import QAExample, Message
import plotly.express as px
import plotly.graph_objects as go


# Configuración de la página
st.set_page_config(
    page_title="IFT Tool - Generador de Datasets",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-indicator {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-idle { background-color: #e0e0e0; }
    .status-processing { background-color: #fff3cd; }
    .status-success { background-color: #d4edda; }
    .status-error { background-color: #f8d7da; }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


# Inicialización del estado de sesión
if 'config' not in st.session_state:
    st.session_state.config = AppConfig()
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'status' not in st.session_state:
    st.session_state.status = ProcessingStatus()
if 'results' not in st.session_state:
    st.session_state.results = []
if 'contexts' not in st.session_state:
    st.session_state.contexts = []
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'token_usage' not in st.session_state:
    st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
if 'curation_data' not in st.session_state:
    st.session_state.curation_data = []


def log_message(message: str, level: str = "info"):
    """Agrega un mensaje al log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.log_messages.append({
        "timestamp": timestamp,
        "level": level,
        "message": message
    })
    # Mantener solo los últimos 100 mensajes
    if len(st.session_state.log_messages) > 100:
        st.session_state.log_messages.pop(0)


def progress_callback(status: ProcessingStatus):
    """Callback para actualizar el estado del procesamiento"""
    st.session_state.status = status
    log_message(status.message, "info")


def render_sidebar():
    """Renderiza la barra lateral con métricas y estado"""
    with st.sidebar:
        st.markdown("## 📊 Estado del Sistema")
        
        # Estado de conexión API
        api_status = "🟢 Conectado" if st.session_state.config.model.api_key else "🔴 No configurado"
        st.markdown(f"**API Status:** {api_status}")
        
        # Modelo actual
        model_name = st.session_state.config.model.model_name
        provider = st.session_state.config.model.provider
        st.markdown(f"**Modelo Actual:** {model_name}")
        st.markdown(f"**Provider:** {provider.title()}")
        
        # Métricas de tokens
        st.markdown("---")
        st.markdown("### 💰 Uso de Tokens")
        token_usage = st.session_state.token_usage
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input Tokens", f"{token_usage['prompt_tokens']:,}")
        with col2:
            st.metric("Output Tokens", f"{token_usage['completion_tokens']:,}")
        
        st.metric("Total Tokens", f"{token_usage['total_tokens']:,}")
        
        # Cálculo de costo
        if token_usage['total_tokens'] > 0:
            cost = calculate_cost(
                provider,
                model_name,
                token_usage['prompt_tokens'],
                token_usage['completion_tokens']
            )
            st.metric("💰 Costo Estimado", format_cost(cost))
        
        # Estadísticas de procesamiento
        if st.session_state.status.total > 0:
            st.markdown("---")
            st.markdown("### 📈 Progreso")
            st.metric("Generados", st.session_state.status.generated_count)
            st.metric("Rechazados", st.session_state.status.rejected_count)
            
            if st.session_state.status.total > 0:
                progress = st.session_state.status.current / st.session_state.status.total
                st.progress(progress)
                st.caption(f"{st.session_state.status.current}/{st.session_state.status.total}")


def render_config_tab():
    """Tab de configuración"""
    st.markdown("## ⚙️ Configuración")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Orígenes de Datos",
        "✂️ Chunking",
        "🤖 Modelo LLM",
        "👤 Información del Autor"
    ])
    
    with tab1:
        st.markdown("### Gestión de Orígenes de Datos")
        
        # Selector de carpeta
        data_folder = st.text_input(
            "Carpeta con archivos fuente",
            value=st.session_state.config.processing.data_folder,
            help="Ruta a la carpeta que contiene archivos .txt o .md"
        )
        
        if data_folder and Path(data_folder).exists():
            # Listar archivos disponibles
            folder_path = Path(data_folder)
            files = list(folder_path.glob("*.txt")) + list(folder_path.glob("*.md"))
            
            if files:
                st.success(f"✅ {len(files)} archivos encontrados")
                
                # Visor previo
                with st.expander("📄 Vista previa de archivos"):
                    selected_file = st.selectbox(
                        "Seleccionar archivo para previsualizar",
                        options=files,
                        format_func=lambda x: x.name
                    )
                    
                    if selected_file:
                        try:
                            with open(selected_file, "r", encoding="utf-8") as f:
                                preview = f.read()[:1000]  # Primeros 1000 caracteres
                            st.text_area("Vista previa", preview, height=200)
                        except Exception as e:
                            st.error(f"Error al leer archivo: {e}")
            else:
                st.warning("⚠️ No se encontraron archivos .txt o .md en la carpeta")
        elif data_folder:
            st.error("❌ La carpeta no existe")
        
        st.session_state.config.processing.data_folder = data_folder
        
        # Configuración de tema
        st.markdown("---")
        st.markdown("### 🎯 Definición de Dominio")
        topic = st.text_input(
            "Tema del dominio",
            value=st.session_state.config.processing.topic,
            help="Ej: 'salud, medicina', 'derecho civil', etc."
        )
        st.session_state.config.processing.topic = topic
        
        # Prompt de clasificación personalizado
        custom_prompt = st.text_area(
            "Prompt de clasificación (opcional)",
            value=st.session_state.config.processing.classification_prompt or "",
            height=150,
            help="Dejar vacío para usar el prompt por defecto"
        )
        st.session_state.config.processing.classification_prompt = custom_prompt if custom_prompt else None
    
    with tab2:
        st.markdown("### Parámetros de Chunking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chunk_size = st.slider(
                "Tamaño del chunk (caracteres)",
                min_value=100,
                max_value=10000,
                value=st.session_state.config.chunking.chunk_size,
                step=100,
                help="Tamaño de cada fragmento de texto"
            )
            st.session_state.config.chunking.chunk_size = chunk_size
        
        with col2:
            overlap = st.slider(
                "Solapamiento (caracteres)",
                min_value=0,
                max_value=1000,
                value=st.session_state.config.chunking.overlap,
                step=50,
                help="Caracteres de solapamiento entre chunks consecutivos"
            )
            st.session_state.config.chunking.overlap = overlap
        
        num_contexts = st.number_input(
            "Número máximo de contextos",
            min_value=1,
            max_value=10000,
            value=st.session_state.config.chunking.num_contexts,
            step=10,
            help="Límite de contextos a extraer"
        )
        st.session_state.config.chunking.num_contexts = num_contexts
        
        # Visualización del solapamiento
        st.markdown("---")
        st.markdown("#### 📊 Visualización del Solapamiento")
        if overlap > 0:
            fig = go.Figure()
            chunk1_start, chunk1_end = 0, chunk_size
            chunk2_start, chunk2_end = chunk_size - overlap, chunk_size * 2 - overlap
            
            fig.add_trace(go.Scatter(
                x=[chunk1_start, chunk1_end, chunk1_end, chunk1_start, chunk1_start],
                y=[0, 0, 1, 1, 0],
                fill='toself',
                fillcolor='rgba(31, 119, 180, 0.3)',
                line=dict(color='rgb(31, 119, 180)'),
                name='Chunk 1'
            ))
            fig.add_trace(go.Scatter(
                x=[chunk2_start, chunk2_end, chunk2_end, chunk2_start, chunk2_start],
                y=[0, 0, 1, 1, 0],
                fill='toself',
                fillcolor='rgba(255, 127, 14, 0.3)',
                line=dict(color='rgb(255, 127, 14)'),
                name='Chunk 2'
            ))
            
            # Área de solapamiento
            overlap_start = chunk1_end - overlap
            fig.add_trace(go.Scatter(
                x=[overlap_start, chunk1_end, chunk1_end, overlap_start, overlap_start],
                y=[0, 0, 1, 1, 0],
                fill='toself',
                fillcolor='rgba(44, 160, 44, 0.5)',
                line=dict(color='rgb(44, 160, 44)', width=2),
                name=f'Solapamiento ({overlap} chars)'
            ))
            
            fig.update_layout(
                title="Distribución de Chunks con Solapamiento",
                xaxis_title="Posición en el texto (caracteres)",
                yaxis_title="",
                height=200,
                showlegend=True,
                yaxis=dict(showticklabels=False, range=[-0.1, 1.1])
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Configuración del Modelo LLM")
        
        provider = st.selectbox(
            "Provider",
            options=["openai", "fireworks", "openrouter"],
            index=["openai", "fireworks", "openrouter"].index(st.session_state.config.model.provider) if st.session_state.config.model.provider in ["openai", "fireworks", "openrouter"] else 0,
            help="Selecciona el proveedor de LLM"
        )
        st.session_state.config.model.provider = provider
        
        # API Key
        api_key = st.text_input(
            "API Key",
            value=st.session_state.config.model.api_key or "",
            type="password",
            help="Tu API key (se guardará en la sesión)"
        )
        if api_key:
            st.session_state.config.model.api_key = api_key
        
        # API Base (para Fireworks y OpenRouter)
        if provider == "fireworks":
            api_base = st.text_input(
                "API Base URL",
                value=st.session_state.config.model.api_base or "https://api.fireworks.ai/inference/v1",
                help="URL base de la API de Fireworks"
            )
            st.session_state.config.model.api_base = api_base
        elif provider == "openrouter":
            api_base = st.text_input(
                "API Base URL",
                value=st.session_state.config.model.api_base or "https://openrouter.ai/api/v1",
                help="URL base de la API de OpenRouter"
            )
            st.session_state.config.model.api_base = api_base
            
            # HTTP Referer y App Name para OpenRouter (opcionales pero recomendados)
            http_referer = st.text_input(
                "HTTP Referer (opcional)",
                value=st.session_state.config.model.http_referer or "",
                help="URL de referencia para OpenRouter (ej: https://tu-dominio.com)"
            )
            st.session_state.config.model.http_referer = http_referer if http_referer else None
            
            app_name = st.text_input(
                "Nombre de la App (opcional)",
                value=st.session_state.config.model.app_name or "IFT Tool",
                help="Nombre de tu aplicación para OpenRouter"
            )
            st.session_state.config.model.app_name = app_name
        
        # Modelo
        if provider == "openai":
            model_options = [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4o",
                "gpt-3.5-turbo"
            ]
        elif provider == "fireworks":
            model_options = [
                "accounts/fireworks/models/llama-v2-7b-chat",
                "accounts/fireworks/models/llama-v2-13b-chat",
                "accounts/fireworks/models/mixtral-8x7b-instruct"
            ]
        else:  # openrouter
            model_options = [
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "openai/gpt-4o",
                "openai/gpt-3.5-turbo",
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
                "meta-llama/llama-3-70b-instruct",
                "meta-llama/llama-3-8b-instruct",
                "mistralai/mistral-large",
                "mistralai/mixtral-8x7b-instruct",
                "google/gemini-pro",
                "google/gemini-pro-1.5"
            ]
        
        model_name = st.selectbox(
            "Modelo",
            options=model_options,
            index=0,
            help="Modelo a utilizar"
        )
        st.session_state.config.model.model_name = model_name
        
        # Hiperparámetros
        st.markdown("---")
        st.markdown("#### 🎛️ Hiperparámetros")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.config.model.temperature,
                step=0.1,
                help="Controla la aleatoriedad (0 = determinístico)"
            )
            st.session_state.config.model.temperature = temperature
        
        with col2:
            top_p = st.slider(
                "Top-p",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.config.model.top_p,
                step=0.05,
                help="Nucleus sampling"
            )
            st.session_state.config.model.top_p = top_p
        
        with col3:
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=1,
                max_value=8000,
                value=st.session_state.config.model.max_tokens or 2000,
                help="Máximo de tokens en la respuesta"
            )
            st.session_state.config.model.max_tokens = max_tokens if max_tokens > 0 else None
    
    with tab4:
        st.markdown("### Información del Autor")
        
        author_name = st.text_input(
            "Nombre",
            value=st.session_state.config.author.name,
            help="Nombre del autor del dataset"
        )
        st.session_state.config.author.name = author_name
        
        institution = st.text_input(
            "Institución",
            value=st.session_state.config.author.institution,
            help="Institución del autor"
        )
        st.session_state.config.author.institution = institution
        
        email = st.text_input(
            "Email",
            value=st.session_state.config.author.email,
            help="Email de contacto"
        )
        st.session_state.config.author.email = email
        
        # Botones de guardar/cargar configuración
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Guardar Configuración"):
                config_path = "config.json"
                st.session_state.config.save(config_path)
                st.success(f"✅ Configuración guardada en {config_path}")
                log_message(f"Configuración guardada en {config_path}", "success")
        
        with col2:
            if st.button("📂 Cargar Configuración"):
                config_path = "config.json"
                if Path(config_path).exists():
                    st.session_state.config = AppConfig.load(config_path)
                    st.success(f"✅ Configuración cargada desde {config_path}")
                    st.rerun()
                else:
                    st.error(f"❌ Archivo {config_path} no encontrado")


def render_execution_tab():
    """Tab de ejecución"""
    st.markdown("## 🚀 Ejecución del Pipeline")
    
    # Verificar si hay archivos intermedios para resume
    intermediate_file = Path("results/ecured_conversations.jsonl")
    can_resume = intermediate_file.exists() and intermediate_file.stat().st_size > 0
    
    if can_resume:
        st.info("📌 Se detectó un archivo de resultados intermedio. Puedes continuar desde donde quedó.")
        resume_choice = st.radio(
            "¿Qué deseas hacer?",
            ["Continuar desde el último punto", "Empezar desde cero"],
            horizontal=True
        )
        resume = resume_choice == "Continuar desde el último punto"
        
        if resume:
            # Contar líneas existentes
            with open(intermediate_file, "r", encoding="utf-8") as f:
                existing_lines = sum(1 for _ in f)
            st.caption(f"Se encontraron {existing_lines} ejemplos ya procesados")
    else:
        resume = False
    
    # Botón de inicio
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        start_button = st.button("▶️ Iniciar Procesamiento", type="primary", disabled=st.session_state.processing)
    
    with col2:
        if st.session_state.processing:
            stop_button = st.button("⏹️ Detener", type="secondary")
            if stop_button:
                st.session_state.processing = False
                log_message("Procesamiento detenido por el usuario", "warning")
    
    # Pipeline visual
    st.markdown("---")
    st.markdown("### 📊 Pipeline de Procesamiento")
    
    stages = ["Extracción", "Clasificación", "Generación", "Formateo"]
    current_stage_idx = {
        "idle": 0,
        "extracting": 0,
        "classifying": 1,
        "generating": 2,
        "formatting": 3
    }.get(st.session_state.status.stage, 0)
    
    # Barras de progreso por etapa
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with cols[i]:
            if i <= current_stage_idx:
                if i == current_stage_idx and st.session_state.processing:
                    st.markdown(f"🔄 **{stage}**")
                    if st.session_state.status.total > 0:
                        progress = st.session_state.status.current / st.session_state.status.total
                        st.progress(progress)
                        st.caption(f"{st.session_state.status.current}/{st.session_state.status.total}")
                else:
                    st.markdown(f"✅ **{stage}**")
            else:
                st.markdown(f"⏳ **{stage}**")
    
    # Log consola
    st.markdown("---")
    st.markdown("### 📝 Log de Procesamiento")
    
    # Filtro de nivel
    log_level = st.selectbox("Filtrar por nivel", ["Todos", "info", "success", "warning", "error"], index=0)
    
    # Mostrar logs
    log_container = st.container()
    with log_container:
        logs_to_show = st.session_state.log_messages
        if log_level != "Todos":
            logs_to_show = [log for log in logs_to_show if log["level"] == log_level]
        
        # Mostrar últimos logs (más recientes primero)
        for log in reversed(logs_to_show[-50:]):  # Últimos 50
            level_emoji = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }.get(log["level"], "ℹ️")
            
            st.text(f"[{log['timestamp']}] {level_emoji} {log['message']}")
    
    # Ejecutar procesamiento
    if start_button and not st.session_state.processing:
        st.session_state.processing = True
        st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        log_message("Iniciando procesamiento...", "info")
        
        try:
            # Etapa 1: Extracción de contextos
            st.session_state.status.stage = "extracting"
            output_file = "results/ecured_contexts.json"
            
            def extract_progress(current, total, message):
                st.session_state.status.current = current
                st.session_state.status.total = total
                st.session_state.status.message = message
                log_message(message, "info")
            
            contexts_data = extract_contexts(
                data_folder=st.session_state.config.processing.data_folder,
                num_contexts=st.session_state.config.chunking.num_contexts,
                output_file=output_file,
                chunk_size=st.session_state.config.chunking.chunk_size,
                overlap=st.session_state.config.chunking.overlap,
                progress_callback=extract_progress
            )
            
            # Cargar contextos
            with open(output_file, "r", encoding="utf-8") as f:
                contexts = [json.loads(line)["context"] for line in f]
            
            st.session_state.contexts = contexts
            log_message(f"✅ Extraídos {len(contexts)} contextos", "success")
            
            # Etapa 2 y 3: Clasificación y Generación
            processor = DatasetProcessor(
                config=st.session_state.config,
                progress_callback=progress_callback
            )
            
            conversations_file = "results/ecured_conversations.jsonl"
            resume_from = None
            
            if resume and intermediate_file.exists():
                # Contar líneas existentes para determinar desde dónde continuar
                with open(intermediate_file, "r", encoding="utf-8") as f:
                    resume_from = sum(1 for _ in f)
                log_message(f"Reanudando desde el contexto {resume_from + 1}", "info")
            
            results = processor.process_contexts(
                contexts=contexts,
                output_path=conversations_file,
                resume_from=resume_from
            )
            
            # Actualizar uso de tokens
            total_prompt = sum(r.get("usage", {}).get("classification", {}).get("prompt_tokens", 0) + 
                              r.get("usage", {}).get("generation", {}).get("prompt_tokens", 0) 
                              for r in results)
            total_completion = sum(r.get("usage", {}).get("classification", {}).get("completion_tokens", 0) + 
                                  r.get("usage", {}).get("generation", {}).get("completion_tokens", 0) 
                                  for r in results)
            
            st.session_state.token_usage = {
                "prompt_tokens": total_prompt,
                "completion_tokens": total_completion,
                "total_tokens": total_prompt + total_completion
            }
            
            # Etapa 4: Formateo
            st.session_state.status.stage = "formatting"
            formatted_path = "results/formatted_conversations.json"
            processor.format_results(
                input_path=conversations_file,
                output_path=formatted_path
            )
            
            # Cargar resultados formateados para curaduría
            with open(formatted_path, "r", encoding="utf-8") as f:
                formatted_results = json.load(f)
            
            st.session_state.curation_data = formatted_results
            st.session_state.results = results
            st.session_state.processing = False
            
            log_message("✅ Procesamiento completado exitosamente", "success")
            st.success("🎉 Procesamiento completado! Revisa la pestaña 'Curaduría' para validar los resultados.")
            st.rerun()
            
        except Exception as e:
            st.session_state.processing = False
            error_msg = f"Error durante el procesamiento: {str(e)}"
            log_message(error_msg, "error")
            st.error(f"❌ {error_msg}")
            st.exception(e)


def render_curation_tab():
    """Tab de curaduría y edición"""
    st.markdown("## ✏️ Curaduría y Validación")
    
    if not st.session_state.curation_data:
        st.info("ℹ️ No hay datos para curar. Ejecuta el procesamiento primero.")
        return
    
    # Estadísticas
    total_examples = len(st.session_state.curation_data)
    st.metric("Total de Ejemplos", total_examples)
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        filter_status = st.multiselect(
            "Estado",
            options=["Todos", "Aceptados", "Rechazados", "Requiere Edición"],
            default=["Todos"]
        )
    
    with col2:
        search_term = st.text_input("🔎 Buscar en contexto", "")
    
    # Preparar datos para la tabla
    curation_df_data = []
    for idx, example in enumerate(st.session_state.curation_data):
        # Extraer preguntas y respuestas
        messages = example.get("messages", [])
        qa_pairs = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                qa_pairs.append({
                    "question": messages[i]["content"],
                    "answer": messages[i + 1]["content"]
                })
        
        # Crear texto de contexto truncado
        context = example.get("context", "")[:200] + "..." if len(example.get("context", "")) > 200 else example.get("context", "")
        
        curation_df_data.append({
            "id": str(example.get("id", idx)),
            "context": context,
            "qa_pairs": qa_pairs,
            "tags": ", ".join(example.get("tags", [])),
            "status": "Pendiente",  # Estado inicial
            "full_data": example
        })
    
    # Aplicar filtros
    filtered_data = curation_df_data
    if search_term:
        filtered_data = [d for d in filtered_data if search_term.lower() in d["context"].lower()]
    
    # Tabla interactiva
    st.markdown("### 📋 Dataset Generado")
    
    for idx, item in enumerate(filtered_data):
        with st.expander(f"Ejemplo {idx + 1} - ID: {item['id'][:8]}...", expanded=False):
            # Estado
            status_col1, status_col2, status_col3 = st.columns(3)
            with status_col1:
                if st.button(f"✅ Aceptar", key=f"accept_{idx}"):
                    item["status"] = "Aceptado"
                    st.success("Marcado como aceptado")
            with status_col2:
                if st.button(f"❌ Rechazar", key=f"reject_{idx}"):
                    item["status"] = "Rechazado"
                    st.warning("Marcado como rechazado")
            with status_col3:
                if st.button(f"✏️ Editar", key=f"edit_{idx}"):
                    item["status"] = "Requiere Edición"
                    st.info("Marcado para edición")
            
            # Contexto completo
            st.markdown("#### 📄 Contexto")
            st.text_area("Contexto completo", item["full_data"]["context"], height=150, key=f"context_{idx}")
            
            # Preguntas y respuestas editables
            st.markdown("#### 💬 Conversación")
            for qa_idx, qa_pair in enumerate(item["qa_pairs"]):
                st.markdown(f"**Pregunta {qa_idx + 1}:**")
                edited_question = st.text_area(
                    "Pregunta",
                    value=qa_pair["question"],
                    key=f"q_{idx}_{qa_idx}",
                    height=80
                )
                
                st.markdown(f"**Respuesta {qa_idx + 1}:**")
                edited_answer = st.text_area(
                    "Respuesta",
                    value=qa_pair["answer"],
                    key=f"a_{idx}_{qa_idx}",
                    height=120
                )
                
                # Actualizar datos si se editó
                if edited_question != qa_pair["question"] or edited_answer != qa_pair["answer"]:
                    item["full_data"]["messages"][qa_idx * 2]["content"] = edited_question
                    item["full_data"]["messages"][qa_idx * 2 + 1]["content"] = edited_answer
                    item["status"] = "Editado"
            
            # Tags
            tags = st.text_input("Tags (separados por comas)", value=item["tags"], key=f"tags_{idx}")
            if tags:
                item["full_data"]["tags"] = [t.strip() for t in tags.split(",")]
    
    # Exportar dataset final
    st.markdown("---")
    st.markdown("### 💾 Exportar Dataset")
    
    # Filtrar solo aceptados y editados
    accepted_data = [item["full_data"] for item in filtered_data if item["status"] in ["Aceptado", "Editado", "Pendiente"]]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar Dataset Final", type="primary"):
            output_path = "results/final_dataset.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(accepted_data, f, ensure_ascii=False, indent=2, default=str)
            st.success(f"✅ Dataset exportado a {output_path}")
            log_message(f"Dataset exportado: {len(accepted_data)} ejemplos", "success")
    
    with col2:
        st.download_button(
            "⬇️ Descargar JSON",
            data=json.dumps(accepted_data, ensure_ascii=False, indent=2, default=str),
            file_name=f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def render_analytics_tab():
    """Tab de análisis y visualización"""
    st.markdown("## 📊 Análisis y Visualización")
    
    if not st.session_state.curation_data:
        st.info("ℹ️ No hay datos para analizar. Ejecuta el procesamiento primero.")
        return
    
    # Estadísticas generales
    st.markdown("### 📈 Estadísticas Generales")
    
    total_examples = len(st.session_state.curation_data)
    total_messages = sum(len(ex.get("messages", [])) for ex in st.session_state.curation_data)
    total_questions = total_messages // 2
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Ejemplos", total_examples)
    with col2:
        st.metric("Total de Preguntas", total_questions)
    with col3:
        st.metric("Total de Mensajes", total_messages)
    
    # Distribución de tokens
    st.markdown("---")
    st.markdown("### 📏 Distribución de Longitud de Respuestas")
    
    answer_lengths = []
    question_lengths = []
    
    for example in st.session_state.curation_data:
        messages = example.get("messages", [])
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                question = messages[i]["content"]
                answer = messages[i + 1]["content"]
                question_lengths.append(estimate_tokens(question))
                answer_lengths.append(estimate_tokens(answer))
    
    if answer_lengths:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_q = px.histogram(
                x=question_lengths,
                nbins=30,
                title="Distribución de Tokens en Preguntas",
                labels={"x": "Tokens", "y": "Frecuencia"}
            )
            st.plotly_chart(fig_q, use_container_width=True)
        
        with col2:
            fig_a = px.histogram(
                x=answer_lengths,
                nbins=30,
                title="Distribución de Tokens en Respuestas",
                labels={"x": "Tokens", "y": "Frecuencia"}
            )
            st.plotly_chart(fig_a, use_container_width=True)
        
        # Estadísticas
        st.markdown("#### 📊 Estadísticas de Longitud")
        stats_df = pd.DataFrame({
            "Tipo": ["Preguntas", "Respuestas"],
            "Media": [sum(question_lengths) / len(question_lengths), sum(answer_lengths) / len(answer_lengths)],
            "Mediana": [sorted(question_lengths)[len(question_lengths) // 2], sorted(answer_lengths)[len(answer_lengths) // 2]],
            "Mínimo": [min(question_lengths), min(answer_lengths)],
            "Máximo": [max(question_lengths), max(answer_lengths)]
        })
        st.dataframe(stats_df, use_container_width=True)
    
    # Distribución de tags
    st.markdown("---")
    st.markdown("### 🏷️ Distribución de Tags")
    
    all_tags = []
    for example in st.session_state.curation_data:
        all_tags.extend(example.get("tags", []))
    
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts()
        fig_tags = px.bar(
            x=tag_counts.index,
            y=tag_counts.values,
            title="Frecuencia de Tags",
            labels={"x": "Tag", "y": "Frecuencia"}
        )
        st.plotly_chart(fig_tags, use_container_width=True)


def main():
    """Función principal"""
    st.markdown('<div class="main-header">🤖 IFT Tool - Generador de Datasets</div>', unsafe_allow_html=True)
    st.markdown("Herramienta para generar sintéticamente datasets de instruction fine-tuning")
    
    # Sidebar
    render_sidebar()
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ Configuración",
        "🚀 Ejecución",
        "✏️ Curaduría",
        "📊 Análisis"
    ])
    
    with tab1:
        render_config_tab()
    
    with tab2:
        render_execution_tab()
    
    with tab3:
        render_curation_tab()
    
    with tab4:
        render_analytics_tab()


if __name__ == "__main__":
    main()
