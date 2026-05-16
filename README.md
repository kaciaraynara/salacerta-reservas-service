# SalaCerta - Back-end Python (Reservas)

API desenvolvida em Python com FastAPI para gerenciar a ocupação de salas de reunião, controle de agendas corporativas e validação de conflitos de horários. 

O serviço funciona de forma independente do sistema de login, consumindo o banco PostgreSQL através do SQLAlchemy.


## Decisões Técnicas e Arquitetura

* **FastAPI (Assíncrono):** Escolhido pelo suporte nativo a `async/await`. Toda a comunicação de entrada e saída com o banco de dados roda de forma assíncrona para otimizar o tempo de resposta sob múltiplas requisições.
* **SQLAlchemy & PostgreSQL:** Mapeamento relacional seguro. A regra que impede o agendamento de duas reuniões na mesma sala e horário foi implementada direto na query de validação, comparando os limites de início e fim antes de dar o commit.
* **Validação Descentralizada de JWT:** Para não sobrecarregar o back-end em C# (responsável pelo login), este serviço em Python valida a assinatura do token JWT direto em memória usando o `JWT_SECRET` compartilhado. Isso elimina requisições HTTP adicionais entre os servidores a cada clique do usuário.


## Endpoints da API

Todos os endpoints (com exceção do pre-flight do CORS) exigem o cabeçalho `Authorization: Bearer <token>`:

* `GET /api/locais` - Lista as filiais cadastradas.
* `GET /api/salas` - Lista as salas de reunião disponíveis.
* `GET /api/reservas` - Retorna a grade completa de agendamentos.
* `POST /api/reservas` - Valida o horário e cria uma nova reserva.
* `PUT /api/reservas/{id}` - Atualiza um agendamento existente revalidando choques de horário.
* `DELETE /api/reservas/{id}` - Cancela/remove uma reserva do banco de dados.


## Como Configurar e Rodar Localmente

### Pré-requisitos
* Python 3.10 ou superior
* Banco de dados PostgreSQL ativo

### Configuração do Ambiente

1. Crie um arquivo `.env` na raiz desta pasta com as variáveis de conexão:
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/salacerta_reservas
JWT_SECRET=ChaveMestreCompartilhadaDeSeguranca123!
No terminal, crie o ambiente virtual:

* python -m venv venv

Ative o ambiente virtual:

* Windows (PowerShell): .\venv\Scripts\Activate.ps1

* Windows (CMD): .\venv\Scripts\activate.bat

* Linux/Mac: source venv/bin/activate


Instale as dependências listadas no projeto:

* pip install -r requirements.txt
Inicialize o servidor de desenvolvimento:


* uvicorn main:app --reload --port 8000
O servidor vai subir em http://127.0.0.1:8000. Na primeira inicialização, a rotina de startup do código vai verificar o banco e criar automaticamente as tabelas e dados iniciais de teste (filiais e salas) se eles ainda não existirem no PostgreSQL.