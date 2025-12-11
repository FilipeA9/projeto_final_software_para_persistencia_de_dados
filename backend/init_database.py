"""
Script para inicializar o banco de dados PostgreSQL.
Executa os scripts SQL diretamente sem usar migrations.
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "turistando",
    "password": "turistando123",
    "database": "turistando_db"
}

def read_sql_file(filename):
    """Lê um arquivo SQL."""
    sql_path = Path(__file__).parent / "scripts" / filename
    if not sql_path.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_path}")
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        return f.read()

def init_postgres():
    """Inicializa o banco de dados PostgreSQL."""
    print("🔧 Conectando ao PostgreSQL...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Conectado ao PostgreSQL!")
        print("📋 Executando script de criação de tabelas...")
        
        # Ler e executar o script SQL
        sql_content = read_sql_file("create_tables.sql")
        
        # Executar o script
        cursor.execute(sql_content)
        
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar tabelas criadas
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()
        
        print("\n📊 Tabelas no banco de dados:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar/inicializar PostgreSQL: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def check_postgres_connection():
    """Verifica se o PostgreSQL está acessível."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        return True
    except:
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Inicialização do Banco de Dados - Turistando")
    print("=" * 60)
    print()
    
    # Verificar conexão
    if not check_postgres_connection():
        print("❌ Não foi possível conectar ao PostgreSQL!")
        print("   Certifique-se de que:")
        print("   1. O Docker está rodando: docker ps")
        print("   2. O container PostgreSQL está ativo")
        print("   3. As configurações de conexão estão corretas")
        sys.exit(1)
    
    # Inicializar banco
    success = init_postgres()
    
    if success:
        print()
        print("=" * 60)
        print("  🎉 Inicialização concluída!")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)
