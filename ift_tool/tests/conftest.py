"""
Configuración de pytest para IFT Tool
"""
import pytest
from pathlib import Path

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def project_root():
    """Retorna el directorio raíz del proyecto"""
    return PROJECT_ROOT


@pytest.fixture
def test_data_dir(project_root):
    """Retorna el directorio de datos de prueba"""
    return project_root / "data"
