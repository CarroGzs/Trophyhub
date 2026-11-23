# TrophyHub

Aplicação web em **Flask** (padrão **MVC**) para gerenciar um catálogo de jogos e as conquistas (troféus) que cada jogador desbloqueia. Utiliza **SQLite** com SQL puro.

## Entidades

| Entidade | Tabela | Descrição |
|---|---|---|
| Usuário | `users` | Conta de acesso (username, e-mail, senha com hash). |
| Jogo | `games` | Jogo do catálogo (nome, gênero e lista de conquistas disponíveis). |
| Conquista | `achievements` | Conquista de um jogo resgatada por um jogador. |

## Funcionalidades

- Cadastro, login e logout com senha armazenada em hash e sessão.
- Rotas protegidas por middleware (`login_required`).
- Perfil **admin**: cadastrar e excluir jogos, adicionar e remover conquistas do catálogo.
- Perfil **jogador**: buscar jogos por nome ou gênero, resgatar conquistas e removê-las de "Meus Jogos".
- Tema claro/escuro (salvo em cookie), página 404 personalizada e logs de eventos.

## Estrutura (MVC)

```
Trophyhub/
├── app/
│   ├── __init__.py        # create_app (fábrica da aplicação)
│   ├── controllers/       # Controllers (rotas / Blueprints)
│   ├── models/            # Models (User, Game, Achievement)
│   ├── views/             # Views (templates HTML)
│   ├── middlewares/       # login_required
│   ├── database/          # conexão com o SQLite
│   └── statics/           # CSS
├── iniciar_bd.py          # cria as tabelas e os dados iniciais
├── run.py                 # inicia o servidor
├── requirements.txt
└── README.md
```

## Como executar

```bash
pip install -r requirements.txt
python iniciar_bd.py
python run.py
```

Acesse http://127.0.0.1:5000

## Usuários de teste (criados por `iniciar_bd.py`)

| Perfil | Usuário | Senha |
|---|---|---|
| Administrador | `admin` | `123` |
| Jogador | `jogador1` | `abc` |
