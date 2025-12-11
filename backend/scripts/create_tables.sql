-- Script para criar as tabelas manualmente no PostgreSQL
-- Pode ser executado múltiplas vezes (idempotente)

-- Criar tipo ENUM para roles de usuário (se não existir)
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('USER', 'ADMIN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Criar tabela de usuários (se não existir)
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para usuario (se não existirem)
CREATE INDEX IF NOT EXISTS ix_usuario_id ON usuario(id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_usuario_login ON usuario(login);
CREATE UNIQUE INDEX IF NOT EXISTS ix_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS ix_usuario_role ON usuario(role);

-- Criar tabela de pontos turísticos (se não existir)
CREATE TABLE IF NOT EXISTS ponto_turistico (
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

-- Criar índices para ponto_turistico (se não existirem)
CREATE INDEX IF NOT EXISTS ix_ponto_turistico_id ON ponto_turistico(id);
CREATE INDEX IF NOT EXISTS ix_ponto_turistico_categoria ON ponto_turistico(categoria);
CREATE INDEX IF NOT EXISTS ix_ponto_turistico_cidade ON ponto_turistico(cidade);
CREATE INDEX IF NOT EXISTS ix_ponto_turistico_estado ON ponto_turistico(estado);
CREATE INDEX IF NOT EXISTS ix_ponto_turistico_criado_por_id ON ponto_turistico(criado_por_id);

-- Criar tabela de hospedagens (se não existir)
CREATE TABLE IF NOT EXISTS hospedagem (
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

-- Criar índices para hospedagem (se não existirem)
CREATE INDEX IF NOT EXISTS ix_hospedagem_id ON hospedagem(id);
CREATE INDEX IF NOT EXISTS ix_hospedagem_cidade ON hospedagem(cidade);
CREATE INDEX IF NOT EXISTS ix_hospedagem_estado ON hospedagem(estado);
CREATE INDEX IF NOT EXISTS ix_hospedagem_tipo ON hospedagem(tipo);
CREATE INDEX IF NOT EXISTS ix_hospedagem_criado_por_id ON hospedagem(criado_por_id);

-- Criar tabela de avaliações (se não existir)
CREATE TABLE IF NOT EXISTS avaliacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    ponto_turistico_id INTEGER NOT NULL REFERENCES ponto_turistico(id) ON DELETE CASCADE,
    nota INTEGER NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(usuario_id, ponto_turistico_id)
);

-- Criar índices para avaliacao (se não existirem)
CREATE INDEX IF NOT EXISTS ix_avaliacao_id ON avaliacao(id);
CREATE INDEX IF NOT EXISTS ix_avaliacao_usuario_id ON avaliacao(usuario_id);
CREATE INDEX IF NOT EXISTS ix_avaliacao_ponto_turistico_id ON avaliacao(ponto_turistico_id);
CREATE INDEX IF NOT EXISTS ix_avaliacao_nota ON avaliacao(nota);

-- Criar tabela de favoritos (se não existir)
CREATE TABLE IF NOT EXISTS favorito (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    ponto_turistico_id INTEGER NOT NULL REFERENCES ponto_turistico(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, ponto_turistico_id)
);

-- Criar índices para favorito (se não existirem)
CREATE INDEX IF NOT EXISTS ix_favorito_id ON favorito(id);
CREATE INDEX IF NOT EXISTS ix_favorito_usuario_id ON favorito(usuario_id);
CREATE INDEX IF NOT EXISTS ix_favorito_ponto_turistico_id ON favorito(ponto_turistico_id);

-- Mensagem de sucesso
SELECT 'Tabelas criadas com sucesso!' as status;
