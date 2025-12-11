"""
Script simples para inicializar o banco de dados.
Usa variáveis de ambiente para evitar problemas de encoding.
"""
import subprocess
import sys

# SQL para criar as tabelas
CREATE_TABLES_SQL = """
-- Dropar tabelas existentes (na ordem correta devido às foreign keys)
DROP TABLE IF EXISTS favorito CASCADE;
DROP TABLE IF EXISTS avaliacao CASCADE;
DROP TABLE IF EXISTS hospedagem CASCADE;
DROP TABLE IF EXISTS ponto_turistico CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

-- Criar tipo ENUM para roles de usuário
CREATE TYPE user_role AS ENUM ('USER', 'ADMIN');

-- Criar tabela de usuários
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuario
CREATE INDEX ix_usuario_id ON usuario(id);
CREATE UNIQUE INDEX ix_usuario_login ON usuario(login);
CREATE UNIQUE INDEX ix_usuario_email ON usuario(email);
CREATE INDEX ix_usuario_role ON usuario(role);

-- Criar tabela de pontos turísticos
CREATE TABLE ponto_turistico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    criado_por_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Índices para ponto_turistico
CREATE INDEX ix_ponto_turistico_id ON ponto_turistico(id);
CREATE INDEX ix_ponto_turistico_categoria ON ponto_turistico(categoria);
CREATE INDEX ix_ponto_turistico_cidade ON ponto_turistico(cidade);
CREATE INDEX ix_ponto_turistico_estado ON ponto_turistico(estado);
CREATE INDEX ix_ponto_turistico_criado_por_id ON ponto_turistico(criado_por_id);

-- Criar tabela de hospedagens
CREATE TABLE hospedagem (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    endereco VARCHAR(500) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    preco_diaria NUMERIC(10, 2) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    comodidades TEXT[] DEFAULT '{}',
    criado_por_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Índices para hospedagem
CREATE INDEX ix_hospedagem_id ON hospedagem(id);
CREATE INDEX ix_hospedagem_cidade ON hospedagem(cidade);
CREATE INDEX ix_hospedagem_estado ON hospedagem(estado);
CREATE INDEX ix_hospedagem_tipo ON hospedagem(tipo);
CREATE INDEX ix_hospedagem_criado_por_id ON hospedagem(criado_por_id);

-- Criar tabela de avaliações
CREATE TABLE avaliacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    ponto_turistico_id INTEGER NOT NULL REFERENCES ponto_turistico(id) ON DELETE CASCADE,
    nota INTEGER NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(usuario_id, ponto_turistico_id)
);

-- Índices para avaliacao
CREATE INDEX ix_avaliacao_id ON avaliacao(id);
CREATE INDEX ix_avaliacao_usuario_id ON avaliacao(usuario_id);
CREATE INDEX ix_avaliacao_ponto_turistico_id ON avaliacao(ponto_turistico_id);
CREATE INDEX ix_avaliacao_nota ON avaliacao(nota);

-- Criar tabela de favoritos
CREATE TABLE favorito (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    ponto_turistico_id INTEGER NOT NULL REFERENCES ponto_turistico(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, ponto_turistico_id)
);

-- Índices para favorito
CREATE INDEX ix_favorito_id ON favorito(id);
CREATE INDEX ix_favorito_usuario_id ON favorito(usuario_id);
CREATE INDEX ix_favorito_ponto_turistico_id ON favorito(ponto_turistico_id);

SELECT 'Tabelas criadas com sucesso!' as status;
"""

def main():
    print("=" * 60)
    print("  Inicialização do Banco de Dados - Turistando")
    print("=" * 60)
    print()
    
    # Executar o SQL via docker exec
    print("🔧 Criando tabelas no PostgreSQL...")
    
    try:
        # Usar docker exec para executar o SQL diretamente
        result = subprocess.run(
            ["docker", "exec", "-i", "turistando-postgres", 
             "psql", "-U", "turistando", "-d", "turistando_db"],
            input=CREATE_TABLES_SQL,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ Tabelas criadas com sucesso!")
            print()
            print(result.stdout)
            
            # Listar tabelas
            print("\n📊 Verificando tabelas criadas...")
            list_result = subprocess.run(
                ["docker", "exec", "turistando-postgres",
                 "psql", "-U", "turistando", "-d", "turistando_db",
                 "-c", "\\dt"],
                capture_output=True,
                text=True
            )
            print(list_result.stdout)
            
            print("\n✅ Banco de dados inicializado com sucesso!")
            print()
            print("Próximos passos:")
            print("  1. Inicie o backend: python -m uvicorn src.main:app --reload")
            print("  2. Acesse a documentação: http://localhost:8000/docs")
            return 0
        else:
            print(f"❌ Erro ao criar tabelas:")
            print(result.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
