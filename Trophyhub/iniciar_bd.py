import json
from app.database import DatabaseConnection
from app.models.usermodel import User

def inicializar_banco():
    with DatabaseConnection() as db:
        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                genero TEXT NOT NULL,
                conquistas TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

    # Cadastra os usuários iniciais usando o método save() do Model
    if not User.get_by_username('admin'):
        admin = User('admin', 'admin@trophyhub.com')
        admin.set_password('123')
        admin.save()
        print("Usuário 'admin' (senha: 123) criado com sucesso!")

    if not User.get_by_username('jogador1'):
        jogador = User('jogador1', 'jogador1@trophyhub.com')
        jogador.set_password('abc')
        jogador.save()
        print("Usuário 'jogador1' (senha: abc) criado com sucesso!")

    # Cadastra os jogos iniciais vinculados ao admin
    admin = User.get_by_username('admin')
    jogos = [
        ("Persona 5 Royal", "JRPG", ["The Ultimate Phantom Thief"]),
        ("Hollow Knight", "Metroidvania", ["Embrace the Void"]),
        ("Minecraft", "Sandbox", ["Free the End"]),
        ("Stardew Valley", "Simulação", ["Legend"]),
        ("Celeste", "Plataforma", ["Farewell"])
    ]

    with DatabaseConnection() as db:
        for nome, genero, conquistas in jogos:
            db.cursor.execute("SELECT id FROM games WHERE nome = ?", (nome,))
            if not db.cursor.fetchone():
                db.cursor.execute("""
                    INSERT INTO games (nome, genero, conquistas, user_id)
                    VALUES (?, ?, ?, ?)
                """, (nome, genero, json.dumps(conquistas, ensure_ascii=False), admin.id))
                print(f"Jogo '{nome}' criado com sucesso!")

if __name__ == '__main__':
    inicializar_banco()