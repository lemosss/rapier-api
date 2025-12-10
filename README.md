# Rapier API

Uma API de autenticação, autorização e gerenciamento de usuários com suporte para múltiplos aplicativos (multi-app), criada em FastAPI. Ela centraliza as tarefas de registro, login, atualização e deleção de usuários, com controle de permissões (roles) e endpoints seguros para operações administrativas.

---

## Sumário

- [O que é](#o-que-é)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como rodar](#como-rodar)
- [Endpoints](#endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Testes](#testes)
- [Como expandir/multi-app](#como-expandirmulti-app)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## O que é

A Rapier Auth API é um serviço de autenticação e gerenciamento de usuários que pode ser facilmente integrado a múltiplos sistemas e aplicativos. Ela oferece registro e login seguro por JWT, gerenciamento de perfis e papéis de usuário (user/admin), e endpoints protegidos por autenticação — tudo pensado para fornecer um backend robusto para autenticação centralizada.

### Principais Casos de Uso

- Login único e seguro em vários apps/sistemas
- Gerenciamento centralizado de usuários e permissões
- Pronto para expansão com novos módulos/apps
- API documentada e fácil de testar via Swagger

---

## Estrutura do Projeto

```
rapier-auth/
├── apps/              # Apps modulares
│   └── auth/         # App de autenticação
│       ├── models.py
│       ├── schemas.py
│       ├── services.py
│       └── routes.py
├── core/             # Configurações e utilitários
│   ├── config.py
│   ├── database.py
│   └── security.py
├── tests/            # Testes
│   ├── test_auth/
│   └── test_core/
├── main.py           # Aplicação principal
└── requirements.txt
```

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):
```bash
# Crie um arquivo .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./rapier_auth.db
```

## Executando a Aplicação

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## Sistema de Autenticação

### Roles

- **user**: Usuário comum
- **admin**: Administrador com permissões completas

### Endpoints

#### Auth

##### Públicos
- `POST /api/v1/auth/register` - Registro de novo usuário
- `POST /api/v1/auth/login` - Login e obtenção de token

##### Autenticados (requer token)
- `GET /api/v1/auth/me` - Informações do usuário atual
- `PUT /api/v1/auth/me` - Atualizar os próprios dados

##### Admin apenas
- `POST /api/v1/auth/register/admin` - Criar novo admin
- `GET /api/v1/auth/users` - Listar todos os usuários
- `GET /api/v1/auth/users/{user_id}` - Obter usuário por ID
- `PUT /api/v1/auth/users/{user_id}` - Atualizar dados de um usuário
- `DELETE /api/v1/auth/users/{user_id}` - Deletar usuário

#### Companies

##### Admin apenas
- `POST /api/v1/companies` - Criar nova company

##### Usuário autenticado
- `GET /api/v1/companies` - Listar as companies em que o usuário atual é membro
- `GET /api/v1/companies/{company_id}` - Obter company por ID (se for membro)
- `PUT /api/v1/companies/{company_id}` - Atualizar company (se for membro)
- `POST /api/v1/companies/{company_id}/users` - Adicionar usuário a uma company (se for membro)
- `DELETE /api/v1/companies/{company_id}/users/{user_id}` - Remover usuário da company (se for membro)

#### Gerais
- `GET /` - Mensagem padrão da API
- `GET /health` - Verifica o status/saúde da API

## Testes

Execute os testes com cobertura:

```bash
pytest
```

O projeto mantém **95% de cobertura de testes**.

Para ver relatório detalhado:

```bash
pytest --cov-report=html
```

## Exemplos de Uso

### Registrar usuário
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "password123",
    "full_name": "User Name"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "password": "password123"
  }'
```

### Acessar endpoint protegido
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Próximos Passos

Este projeto está preparado para receber múltiplos apps. Para adicionar um novo app:

1. Crie uma nova pasta em `apps/`
2. Adicione models, schemas, services e routes
3. Registre o router em `main.py`

