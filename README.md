# Turistando - Sistema de Gestão de Turismo 🗺️

Plataforma web abrangente para gestão de turismo que permite aos usuários descobrir, avaliar e gerenciar pontos turísticos com galerias de fotos, avaliações e informações de hospedagem.

**Status**: Fases 1-8 Completas (Histórias 1-6) - 99/124 tarefas (80%)

## 📁 Estrutura do Projeto

```
turistando/
├── backend/                    # API REST com FastAPI
│   ├── src/
│   │   ├── api/               # Endpoints REST (auth, spots, photos, ratings, comments, accommodations, favorites)
│   │   ├── config/            # Configurações de conexão (PostgreSQL, MongoDB, Redis)
│   │   ├── models/            # Modelos SQLAlchemy (Usuario, PontoTuristico, Avaliacao, Hospedagem, Favorito)
│   │   ├── repositories/      # Camada de acesso a dados (padrão Repository)
│   │   ├── services/          # Lógica de negócio e validações
│   │   ├── schemas/           # Esquemas Pydantic para validação
│   │   ├── utils/             # Utilitários (JWT, segurança, bcrypt)
│   │   └── dependencies/      # Injeção de dependências FastAPI
│   ├── alembic/               # Migrações de banco de dados
│   ├── scripts/               # Scripts SQL de inicialização
│   ├── requirements.txt       # Dependências Python
│   ├── init_db_simple.py      # Script de inicialização do banco
│   └── .env                   # Variáveis de ambiente
├── frontend/                   # Interface Streamlit
│   ├── src/
│   │   ├── pages/             # Páginas (Home, Explore, Details, Register, Login, Favorites, Admin)
│   │   ├── components/        # Componentes reutilizáveis (forms, cards, buttons)
│   │   └── services/          # Cliente API HTTP
│   └── requirements.txt       # Dependências Python
├── specs/                      # Documentação e especificações
│   └── 001-tourism-platform/
│       ├── specification.md   # Requisitos funcionais
│       ├── plan.md            # Arquitetura técnica
│       └── tasks.md           # Tarefas de implementação
├── uploads/                    # Armazenamento de fotos
├── docker-compose.yml          # Configuração dos containers (PostgreSQL, MongoDB, Redis)
├── PHASE7_8_COMPLETE.md        # Documentação das últimas implementações
└── README.md                   # Este arquivo
```

## 🏗️ Decisões de Projeto

### Arquitetura

**Padrão Repository + Service Layer**
- **Repository**: Abstração do acesso a dados, facilita testes e troca de banco
- **Service**: Lógica de negócio centralizada, validações e regras de domínio
- **API**: Endpoints REST finos, delegam para services

**Separação Backend/Frontend**
- Backend: API REST stateless com FastAPI
- Frontend: SPA com Streamlit para prototipagem rápida
- Comunicação via HTTP/JSON

### Bancos de Dados (Polyglot Persistence)

**PostgreSQL** - Dados relacionais estruturados
- Usuários, pontos turísticos, avaliações, hospedagens, favoritos
- Integridade referencial e transações ACID
- Agregações complexas (médias, estatísticas)

**MongoDB** - Dados semi-estruturados
- Comentários (com aninhamento de respostas futuras)
- Metadados de fotos
- Flexibilidade de schema para evolução

**Redis** - Cache e sessões
- Cache de consultas frequentes (detalhes de pontos, listas)
- Sessões de usuário e blacklist de tokens
- TTL automático para expiração

### Autenticação e Segurança

**JWT (JSON Web Tokens)**
- Tokens stateless com expiração de 24h
- Claims incluem user_id e role (USER/ADMIN)
- Assinatura com chave secreta (HS256)

**Senhas**
- Hash bcrypt com salt automático
- Custo de 12 rounds (seguro e performático)
- Nunca armazenadas em texto plano

**Autorização**
- Role-based access control (RBAC)
- Endpoints admin protegidos via dependency injection
- Validação de ownership (usuário só edita próprios dados)

### Performance e Escalabilidade

**Cache Strategy (Cache-Aside)**
- Cache de leitura: Check Redis → Miss → Query DB → Store Redis
- TTL diferenciado: 5min (detalhes), 1min (listas)
- Invalidação em writes (create, update, delete)

**Async/Await**
- FastAPI async endpoints (non-blocking I/O)
- AsyncIO para PostgreSQL (asyncpg) e MongoDB (Motor)
- Redis async para não bloquear event loop

**Paginação**
- Limit/offset para listas grandes
- Default 20 itens, máximo 100
- Cursor-based pagination para comentários

### Validação e Qualidade

**Pydantic Schemas**
- Validação automática de requests/responses
- Type hints para documentação automática
- Conversão de tipos e mensagens de erro claras

**Error Handling**
- HTTPException para erros de negócio (404, 409, 403)
- Status codes semânticos (201 Create, 204 No Content)
- Mensagens de erro descritivas

**Soft Delete**
- Pontos turísticos marcados como deletados (deleted_at)
- Preserva histórico e integridade referencial
- Filtro automático em queries

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.11+** (tested com Python 3.12)
- **Docker Desktop** (para PostgreSQL, MongoDB, Redis)
- **PowerShell** (para Windows)

### Passo 1: Iniciar os Containers Docker

```powershell
# Navegue até o diretório do projeto
cd "C:\Users\DELL\Documents\FACULDADE\Software para persistencia de dados\trabalho final\turistando"

# Inicie o Docker Desktop (se não estiver rodando)

# Inicie os containers
docker-compose up -d

# Aguarde ~15-20 segundos para os containers ficarem healthy
Start-Sleep -Seconds 20

# Verifique se os containers estão rodando
docker ps

# Você deve ver 3 containers:
# - turistando-postgres (healthy) - porta 5432
# - turistando-mongodb (healthy) - porta 27017
# - turistando-redis (healthy) - porta 6379
```

### Passo 2: Configurar o Backend

```powershell
# Entre no diretório backend
cd backend

# Crie e ative o ambiente virtual Python (se ainda não existir)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt

# Verifique se o arquivo .env existe e está correto
# (Ele já deve existir no projeto)
Get-Content .env
```

### Passo 3: Inicializar o Banco de Dados

```powershell
# Execute o script de inicialização simplificado
# Este script cria todas as tabelas diretamente no PostgreSQL via Docker
python init_db_simple.py

# Você deve ver:
# ✅ Tabelas criadas com sucesso!
# 📊 Verificando tabelas criadas...
# ✅ Banco de dados inicializado com sucesso!

# Para verificar as tabelas criadas:
docker exec turistando-postgres psql -U turistando -d turistando_db -c "\dt"

# Deve mostrar:
# - alembic_version
# - avaliacao
# - favorito
# - hospedagem
# - ponto_turistico
# - usuario
```

### Passo 4: Iniciar o Servidor Backend

```powershell
# Ainda no diretório backend/ com venv ativado
# Configure o PYTHONPATH para evitar erros de importação
$env:PYTHONPATH = $PWD.Path

# Inicie o servidor usando python -m uvicorn
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# O servidor irá iniciar em:
# http://localhost:8000
# Documentação da API: http://localhost:8000/docs
# Documentação ReDoc: http://localhost:8000/redoc
```

### Passo 5: Configurar e Iniciar o Frontend (Terminal Separado)

```powershell
# Abra um NOVO terminal PowerShell
cd "C:\Users\DELL\Documents\FACULDADE\Software para persistencia de dados\trabalho final\turistando"
cd frontend

# Crie e ative o ambiente virtual para o frontend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instale as dependências do frontend
pip install -r requirements.txt

# Inicie o aplicativo Streamlit
streamlit run src/Home.py

# O frontend abrirá automaticamente em:
# http://localhost:8501
```

## 🌐 Pontos de Acesso

Quando tudo estiver rodando:

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Documentação da API (Swagger)**: http://localhost:8000/docs
- **Documentação da API (ReDoc)**: http://localhost:8000/redoc

### Acesso aos Bancos de Dados

```powershell
# PostgreSQL (dados relacionais: usuários, pontos turísticos, avaliações)
docker exec -it turistando-postgres psql -U turistando -d turistando_db

# MongoDB (fotos e metadados)
docker exec -it turistando-mongodb mongosh -u turistando -p turistando123 --authenticationDatabase admin

# Redis (cache e sessões)
docker exec -it turistando-redis redis-cli
```

## 🧪 Testar o Sistema

### 1. Testar a API Backend

```powershell
# Testar se a API está respondendo
curl http://localhost:8000

# Ou abra no navegador:
# http://localhost:8000/docs
```

### 2. Criar Usuário de Teste via API

Acesse http://localhost:8000/docs e use o endpoint **POST /api/auth/register**:

```json
{
  "login": "testuser",
  "email": "test@turistando.com",
  "senha": "senha123",
  "role": "USER"
}
```

### 3. Fazer Login

Use o endpoint **POST /api/auth/login**:

```json
{
  "login": "testuser",
  "senha": "senha123"
}
```

Você receberá um token JWT que pode ser usado nos outros endpoints.

### 4. Adicionar Dados de Teste (Opcional)

```powershell
# Execute este script SQL para criar dados de exemplo
Get-Content backend/scripts/test_data.sql | docker exec -i turistando-postgres psql -U turistando -d turistando_db
```

## 🔧 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'src'"

**Solução:**
```powershell
# No diretório backend, sempre configure o PYTHONPATH antes de executar:
$env:PYTHONPATH = $PWD.Path
python -m uvicorn src.main:app --reload
```

### Problema: Containers Docker não iniciam

**Solução:**
```powershell
# Pare e remova os containers
docker-compose down

# Verifique se as portas estão livres
netstat -ano | findstr "5432"
netstat -ano | findstr "27017"
netstat -ano | findstr "6379"

# Inicie novamente
docker-compose up -d
```

### Problema: Erro ao conectar ao PostgreSQL

**Solução:**
```powershell
# Verifique se o container está healthy
docker ps

# Teste a conexão
docker exec turistando-postgres pg_isready -U turistando

# Se necessário, reinicialize o banco de dados
python backend/init_database.py
```

### Problema: "uvicorn não é reconhecido"

**Solução:**
```powershell
# Use python -m uvicorn ao invés de apenas uvicorn
python -m uvicorn src.main:app --reload
```

## ✅ Funcionalidades Implementadas (Fases 1-8 Completas)

### História de Usuário 1: Descoberta de Pontos Turísticos ✅
- ✅ Navegar pontos com filtros (cidade, estado, país, busca)
- ✅ Visualizar detalhes do ponto com fotos e avaliações
- ✅ Ver estatísticas e distribuição de avaliações
- ✅ Suporte a paginação
- ✅ Cache Redis (5min para detalhes, 1min para listas)

### História de Usuário 2: Autenticação ✅
- ✅ Registro de usuário com validação
- ✅ Login (usuário ou email)
- ✅ Autenticação JWT (tokens 24h)
- ✅ Gerenciamento de sessão com Redis
- ✅ Logout com blacklist de tokens
- ✅ Exibição de perfil do usuário

### História de Usuário 3: Avaliações e Comentários ✅
- ✅ Submeter avaliações (1-5 estrelas) com comentários opcionais
- ✅ Editar próprias avaliações
- ✅ Ver distribuição e estatísticas de avaliações
- ✅ Postar comentários em pontos turísticos
- ✅ Curtir e reportar comentários
- ✅ Paginação e ordenação de comentários
- ✅ Moderação básica de conteúdo

### História de Usuário 4: Gerenciamento Admin ✅
- ✅ Dashboard administrativo com estatísticas
- ✅ Criar novos pontos turísticos
- ✅ Editar pontos existentes
- ✅ Exclusão suave (soft delete) de pontos
- ✅ Upload de fotos (individual e em lote)
- ✅ Gerenciar galerias de fotos
- ✅ Controle de acesso baseado em função (RBAC)

### História de Usuário 5: Hospedagens ✅
- ✅ Listar hospedagens próximas aos pontos turísticos
- ✅ Filtrar por tipo (hotel, pousada, hostel) e faixa de preço
- ✅ Ver detalhes e links de reserva
- ✅ Admin: criar, editar e deletar hospedagens
- ✅ Estatísticas de hospedagens (contagem, preço médio, tipos)
- ✅ Integrado na página de detalhes do ponto

### História de Usuário 6: Favoritos ✅
- ✅ Adicionar/remover pontos dos favoritos
- ✅ Toggle de status favorito com um clique
- ✅ Ver todos os favoritos em página dedicada
- ✅ Buscar e ordenar favoritos
- ✅ Botão de favorito nas listagens
- ✅ Favoritos privados por usuário

## 🧪 Testando o Sistema

### 1. Testar Registro de Usuário
1. Abra http://localhost:8501
2. Clique em "Cadastro" na barra lateral
3. Preencha o formulário:
   - Login: `testemvp`
   - Email: `teste@mvp.com`
   - Senha: `senha123`
4. Deve ver mensagem de sucesso e redirecionamento

### 2. Testar Login
1. Clique em "Login" na barra lateral
2. Digite: `testemvp` / `senha123`
3. Deve ver o perfil do usuário na barra lateral

### 3. Testar Descoberta de Pontos
1. Clique em "Explorar Pontos"
2. Experimente os filtros (cidade, estado, busca)
3. Clique em "Ver Detalhes" em um ponto
4. Visualize fotos e avaliações

### 4. Testar Endpoints da API

```powershell
# Registrar novo usuário
$body = @{
    login = "apitest"
    email = "api@test.com"
    password = "test123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" -ContentType "application/json" -Body $body

# Salvar token
$token = $response.access_token

# Obter usuário atual
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/auth/me" -Headers $headers

# Listar pontos turísticos
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/spots?limit=5"
```

## 🛠️ Desenvolvimento

### Hot Reload (Recarga Automática)

Backend e frontend suportam hot reload:
- **Backend**: `uvicorn` com flag `--reload`
- **Frontend**: Streamlit detecta mudanças automaticamente

### Migrações de Banco de Dados

```powershell
# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Reverter uma migração
alembic downgrade -1

# Ver histórico de migrações
alembic history
```

### Parando os Serviços

```powershell
# Parar backend: Ctrl+C no terminal
# Parar frontend: Ctrl+C no terminal

# Parar containers Docker
docker-compose down

# Remover volumes (deleta todos os dados)
docker-compose down -v
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Framework**: FastAPI 0.104.1 (framework web Python assíncrono)
- **ORM**: SQLAlchemy 2.0.23 (async com asyncpg)
- **Migrações**: Alembic 1.13.0
- **MongoDB**: Motor 3.3.2 (PyMongo assíncrono)
- **Cache**: Redis 5.0.1 (com suporte async)
- **Autenticação**: JWT (python-jose) + bcrypt (passlib)
- **Validação**: Pydantic 2.5.0
- **Servidor**: Uvicorn (ASGI server)

### Frontend
- **Framework**: Streamlit 1.28.2
- **Cliente HTTP**: requests (com suporte a sessões)

### Bancos de Dados
- **PostgreSQL 15**: Usuários, pontos turísticos, hospedagens, avaliações, favoritos
- **MongoDB 7**: Comentários, fotos e metadados
- **Redis 7**: Armazenamento de sessões, blacklist de tokens, cache de respostas

### Padrões Arquiteturais
- **Repository Pattern**: Abstração de acesso a dados
- **Service Layer**: Lógica de negócio com cache
- **Dependency Injection**: Dependências do FastAPI
- **Cache-Aside Pattern**: Estratégia de cache Redis
- **REST API**: Arquitetura stateless

## 🐛 Solução de Problemas

### Problemas com Docker

**Problema**: `docker-compose up -d` falha
```powershell
# Solução: Inicie o Docker Desktop primeiro
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 20
docker-compose up -d
```

**Problema**: Containers não ficam saudáveis (unhealthy)
```powershell
# Verificar logs
docker logs turistando-postgres
docker logs turistando-mongodb
docker logs turistando-redis

# Reiniciar container específico
docker-compose restart postgres
```

### Problemas com Ambiente Python

**Problema**: `alembic: command not found`
```powershell
# Solução: Ativar venv primeiro
cd backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

**Problema**: Erros de importação
```powershell
# Solução: Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problemas de Conexão com Banco de Dados

**Problema**: Erros `Connection refused`
```powershell
# Verificar se containers estão rodando
docker ps

# Verificar se portas estão disponíveis
netstat -ano | findstr "5432"  # PostgreSQL
netstat -ano | findstr "27017" # MongoDB
netstat -ano | findstr "6379"  # Redis
```

**Problema**: Migração falha
```powershell
# Verificar se banco está acessível
docker exec -it turistando-postgres psql -U turistando -d turistando_db -c "SELECT 1"

# Deletar tabelas e recriar (CUIDADO: deleta dados)
docker-compose down -v
docker-compose up -d
cd backend
alembic upgrade head
```

### Problemas no Frontend

**Problema**: "Não consegue conectar à API"
```powershell
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar se porta 8000 está em uso
netstat -ano | findstr "8000"
```

## 📚 Documentação do Projeto

- **PHASE3_COMPLETE.md**: Detalhes da implementação da História 1
- **PHASE4_COMPLETE.md**: Detalhes da implementação da História 2
- **PHASE7_8_COMPLETE.md**: Detalhes das implementações das Histórias 5-6
- **specs/001-tourism-platform/**: Especificação completa do projeto
  - `specification.md`: Requisitos funcionais e histórias de usuário
  - `plan.md`: Arquitetura técnica e decisões de design
  - `tasks.md`: Tarefas de implementação (99/124 completas - 80%)

## 🎯 Próximos Passos

### Implementação Restante (Fases 9-10)

**Fase 9: Direções (US7)** - 4 tarefas
- Integrar serviço de direções
- Criar componente de mapa com rotas
- Adicionar direções à página de detalhes

**Fase 10: Importar/Exportar (US8)** - 9 tarefas
- Construir utilitários de exportação CSV/JSON
- Criar utilitários de importação de dados
- Adicionar UI de importação/exportação no admin

**Fase Final: Polimento** - 12 tarefas
- Adicionar validação abrangente
- Implementar middleware de tratamento de erros
- Configurar logging
- Criar documentação de API e deployment

## 📖 Documentação da API

Documentação completa da API disponível em http://localhost:8000/docs

### Principais Endpoints

**Autenticação**
- `POST /api/auth/register` - Criar conta
- `POST /api/auth/login` - Obter token JWT
- `POST /api/auth/logout` - Invalidar sessão
- `GET /api/auth/me` - Informações do usuário atual

**Pontos Turísticos**
- `GET /api/spots` - Listar com filtros
- `GET /api/spots/{id}` - Detalhes do ponto

**Fotos**
- `GET /api/spots/{id}/photos` - Fotos do ponto

**Avaliações**
- `GET /api/spots/{id}/ratings` - Avaliações do ponto
- `GET /api/spots/{id}/ratings/stats` - Estatísticas de avaliações
- `POST /api/spots/{id}/ratings` - Criar avaliação (requer autenticação)
- `PUT /api/ratings/{id}` - Atualizar avaliação (requer autenticação)

**Comentários**
- `GET /api/spots/{id}/comments` - Comentários do ponto com paginação
- `POST /api/spots/{id}/comments` - Criar comentário (requer autenticação)
- `POST /api/comments/{id}/like` - Curtir comentário
- `POST /api/comments/{id}/report` - Reportar comentário

**Admin - Pontos**
- `POST /api/spots` - Criar ponto (apenas admin)
- `PUT /api/spots/{id}` - Atualizar ponto (apenas admin)
- `DELETE /api/spots/{id}` - Deletar ponto (apenas admin)

**Admin - Fotos**
- `POST /api/spots/{id}/photos` - Upload de foto (apenas admin)
- `DELETE /api/photos/{id}` - Deletar foto (apenas admin)

**Hospedagens**
- `GET /api/spots/{id}/accommodations` - Listar hospedagens de um ponto
- `GET /api/spots/{id}/accommodations/statistics` - Estatísticas de hospedagens
- `GET /api/accommodations/{id}` - Obter detalhes da hospedagem
- `POST /api/accommodations` - Criar hospedagem (apenas admin)
- `PUT /api/accommodations/{id}` - Atualizar hospedagem (apenas admin)
- `DELETE /api/accommodations/{id}` - Deletar hospedagem (apenas admin)

**Favoritos**
- `GET /api/favorites` - Obter favoritos do usuário (requer autenticação)
- `POST /api/spots/{id}/favorite` - Adicionar aos favoritos (requer autenticação)
- `DELETE /api/spots/{id}/favorite` - Remover dos favoritos (requer autenticação)
- `POST /api/spots/{id}/favorite/toggle` - Alternar status de favorito (requer autenticação)
- `GET /api/spots/{id}/favorite/status` - Verificar status de favorito (requer autenticação)

## 📝 Modelo de Dados

### PostgreSQL (Relacional)

**usuario** - Usuários do sistema
- id (PK), login (unique), email (unique), senha_hash, role (USER/ADMIN), created_at

**ponto_turistico** - Pontos turísticos
- id (PK), nome, descricao, cidade, estado, pais, latitude, longitude, endereco
- criado_por (FK → usuario), avg_rating, rating_count, deleted_at (soft delete)

**avaliacao** - Avaliações de pontos
- id (PK), ponto_id (FK), usuario_id (FK), nota (1-5), comentario, created_at
- Constraint: um usuário pode avaliar cada ponto apenas uma vez

**hospedagem** - Hospedagens próximas
- id (PK), ponto_id (FK), nome, endereco, telefone, preco_medio, tipo (enum), link_reserva

**favorito** - Favoritos dos usuários
- id (PK), usuario_id (FK), ponto_id (FK), created_at
- Constraint: um usuário pode favoritar cada ponto apenas uma vez

### MongoDB (Documentos)

**photos** - Fotos e metadados
```json
{
  "_id": ObjectId,
  "pontoId": int,
  "titulo": string,
  "filename": string,
  "uploadedBy": int,
  "createdAt": datetime,
  "metadata": {
    "size": int,
    "mimetype": string
  }
}
```

**comments** - Comentários em pontos
```json
{
  "_id": ObjectId,
  "pontoId": int,
  "usuarioId": int,
  "texto": string,
  "createdAt": datetime,
  "metadata": {
    "likes": int,
    "reports": int,
    "isModerated": bool
  }
}
```

### Redis (Cache/Sessões)

- **spot_detail:{id}** - Cache de detalhes (TTL 5min)
- **spot_list:{hash}** - Cache de listagens (TTL 1min)
- **session:{token}** - Sessões de usuário (TTL 24h)
- **blacklist:{token}** - Tokens invalidados (TTL 24h)

## 👥 Autores

Projeto acadêmico para a disciplina **Software para Persistência de Dados**.

## 📄 Licença

Uso educacional apenas - Plataforma de Turismo para demonstração de persistência de dados.
