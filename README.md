# 🚀 FastAPI + Dropbox + JWT + PostgreSQL

Este projeto é uma API desenvolvida com **FastAPI** que permite:

- Autenticação com JWT usando CNH + senha
- Upload de arquivos no **Dropbox**
- Criação e listagem de pastas
- Armazenamento e segurança com PostgreSQL

---

## 📦 Requisitos

- Python 3.11+
- PostgreSQL 13+
- (Opcional) Docker + Docker Compose

---

## ⚙️ Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz com:

DATABASE_URL=postgresql://usuario:senha@localhost:5432/seubanco 
DROPBOX_REFRESH_TOKEN=seu_refresh_token 
DROPBOX_CLIENT_ID=seu_client_id 
DROPBOX_CLIENT_SECRET=seu_client_secret

---

## 🧪 Instalação local (modo simples)

```bash
# 1. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # ou venv\\Scripts\\activate no Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Crie as tabelas no PostgreSQL
python -m app.db.init_db

# 4. Crie o usuário inicial
python -m app.db.create_admin

# 5. Rode a aplicação
uvicorn app.main:app --reload --port=80


🔐 Como usar JWT no Swagger (FastAPI Docs)
A API usa autenticação JWT com token de acesso gerado ao fazer login com CNH e senha.

✅ 1. Obtenha o token
Faça uma requisição para:
POST /v2/login
Exemplo de payload:

{
  "cnh": "123",
  "password": "senha123"
}

Você receberá uma resposta como:

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

✅ 2. Autorize no Swagger UI
Vá até http://localhost:8000/docs
Clique no botão 🔒 Authorize
No campo que aparecer (OAuth2PasswordBearer (OAuth2, password)), cole o token assim:
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Atenção: inclua "Bearer " antes do token (com espaço)
Clique em Authorize e depois em Close
Agora você poderá testar todas as rotas protegidas diretamente no Swagger.

