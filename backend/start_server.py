"""
Script para iniciar o servidor da aplicação.
Verifica dependências e inicia o servidor FastAPI.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Define variáveis de ambiente
os.environ.setdefault("PYTHONPATH", str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("  Turistando API Server")
    print("=" * 60)
    print()
    print("🚀 Iniciando servidor FastAPI...")
    print("📍 Acesse: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print()
    
    # Iniciar servidor
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
