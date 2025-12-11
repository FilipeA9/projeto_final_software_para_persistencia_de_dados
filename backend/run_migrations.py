"""
Script para executar migrações do Alembic de forma mais robusta.
Resolve problemas de encoding no Windows.
"""
import os
import sys

# Força encoding UTF-8
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Adiciona o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Define variáveis de ambiente diretamente (evita problemas com o .env)
os.environ["DATABASE_URL"] = "postgresql://turistando:turistando123@localhost:5432/turistando_db"
os.environ["MONGODB_URL"] = "mongodb://turistando:turistando123@localhost:27017/turistando_db"
os.environ["MONGODB_DATABASE"] = "turistando_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ["ALGORITHM"] = "HS256"

# Executa o Alembic
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", "postgresql+psycopg2://turistando:turistando123@localhost:5432/turistando_db")

try:
    print("Executando migrações...")
    command.upgrade(alembic_cfg, "head")
    print("✓ Migrações executadas com sucesso!")
except Exception as e:
    print(f"✗ Erro ao executar migrações: {e}")
    sys.exit(1)
