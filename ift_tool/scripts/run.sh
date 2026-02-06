#!/bin/bash
# Script helper para ejecutar la aplicación Streamlit
# Uso: ./scripts/run.sh

cd "$(dirname "$0")/.." || exit

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Verificar que el paquete esté instalado
if ! python -c "import ift_tool" 2>/dev/null; then
    echo "⚠️  El paquete ift_tool no está instalado."
    echo "💡 Instalando en modo desarrollo..."
    uv pip install -e . || pip install -e .
fi

# Ejecutar Streamlit
streamlit run ift_tool/ui/streamlit_app.py "$@"
