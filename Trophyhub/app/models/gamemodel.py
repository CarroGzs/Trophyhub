from app.database import DatabaseConnection
import json

class Game:
    def __init__(self, nome, genero, conquistas, id):
        self.nome=nome
        self.genero=genero
        self.conquistas=conquistas
        self.id=id


    @classmethod
    def _from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            nome=row['nome'],
            genero=row['genero'],
            conquistas=json.loads(row['conquistas']),        
)

    @classmethod
    def get_all_games(cls):
        with DatabaseConnection() as db:
            query = "SELECT id, nome, genero, conquistas FROM games"
            db.cursor.execute(query)
            lista = db.cursor.fetchall()
            listaGames = []
            for linha in lista:
                listaGames.append(cls._from_row(linha))
            return listaGames
        
    @classmethod
    def create(cls, nome, genero, conquistas, user_id):
        with DatabaseConnection() as db:
            query = """
                INSERT INTO games (nome, genero, conquistas, user_id)
                VALUES (?, ?, ?, ?)
            """
            db.cursor.execute(
                query,
                (nome, genero, json.dumps(conquistas), user_id)
            )

    @classmethod
    def get_by_id(cls, game_id, user_id):
        with DatabaseConnection() as db:
            query = "SELECT id, nome, genero, conquistas FROM games WHERE id = ? AND user_id = ?"
            db.cursor.execute(query, (game_id, user_id))
            row = db.cursor.fetchone()
            return cls._from_row(row)

    @classmethod
    def delete(cls, game_id, user_id):
        with DatabaseConnection() as db:
            query = "DELETE FROM games WHERE id = ? AND user_id = ?"
            db.cursor.execute(query, (game_id, user_id))

    @classmethod
    def add_conquista_nome(cls, game_id, nome_conquista, user_id):
        game = cls.get_by_id(game_id, user_id)
        if game:
            if nome_conquista not in game.conquistas:
                game.conquistas.append(nome_conquista)
                with DatabaseConnection() as db:
                    query = "UPDATE games SET conquistas = ? WHERE id = ? AND user_id = ?"
                    db.cursor.execute(query, (json.dumps(game.conquistas), game_id, user_id))
    @classmethod
    def search_games(cls, termo):
        with DatabaseConnection() as db:
            query = """
                SELECT id, nome, genero, conquistas, user_id 
                FROM games 
                WHERE nome LIKE ? OR genero LIKE ?
                ORDER BY nome
            """
            padrao = f"%{termo}%"
            db.cursor.execute(query, (padrao, padrao))
            return [cls._from_row(row) for row in db.cursor.fetchall()]
    
    @classmethod
    def remove_conquista_nome(cls, game_id, nome_conquista):
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT conquistas FROM games WHERE id = ?", (game_id,))
            row = db.cursor.fetchone()
            if row:
                conquistas = json.loads(row['conquistas']) if row['conquistas'] else []
                if nome_conquista in conquistas:
                    conquistas.remove(nome_conquista)
                    db.cursor.execute(
                        "UPDATE games SET conquistas = ? WHERE id = ?",
                        (json.dumps(conquistas, ensure_ascii=False), game_id)
                    )
            db.cursor.execute(
                "DELETE FROM achievements WHERE game_id = ? AND nome = ?",
                (game_id, nome_conquista)
            )
    
    @classmethod
    def get_by_id_global(cls, game_id):
        """Busca um jogo no catálogo global pelo ID (para validar resgates de jogadores)."""
        with DatabaseConnection() as db:
            query = "SELECT id, nome, genero, conquistas, user_id FROM games WHERE id = ?"
            db.cursor.execute(query, (game_id,))
            return cls._from_row(db.cursor.fetchone())