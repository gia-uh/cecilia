#!/usr/bin/env python
"""
Script de entrada para ejecutar la aplicación Streamlit
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para asegurar que el paquete sea encontrado
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Verificar que el paquete esté disponible
try:
    import ift_tool
except ImportError:
    print("⚠️  Advertencia: El paquete ift_tool no está instalado.")
    print("💡 Ejecuta: uv pip install -e .")
    print("   O: pip install -e .")
    sys.exit(1)

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Ejecutar Streamlit con el módulo de la app
    app_path = project_root / "ift_tool" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ Error: No se encontró la aplicación en {app_path}")
        sys.exit(1)
    
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        *sys.argv[1:]
    ]
    
    sys.exit(stcli.main())
