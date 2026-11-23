from app.database import DatabaseConnection

class Achievement:
    def __init__(self, nome, descricao, game_id, user_id, id=None):
        self.nome = nome
        self.descricao = descricao
        self.game_id = game_id
        self.user_id = user_id
        self.id = id

    @classmethod
    def _from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            nome=row['nome'],
            descricao=row['descricao'],
            game_id=row['game_id'],
            user_id=row['user_id']
        )

    @classmethod
    def get_by_game(cls, game_id, user_id):
        with DatabaseConnection() as db:
            query = "SELECT id, nome, descricao, game_id, user_id FROM achievements WHERE game_id = ? AND user_id = ?"
            db.cursor.execute(query, (game_id, user_id))
            return [cls._from_row(row) for row in db.cursor.fetchall()]

    @classmethod
    def get_by_user_grouped(cls, user_id):
        """Retorna os jogos e a lista de conquistas que o jogador possui em cada um."""
        with DatabaseConnection() as db:
            query = """
                SELECT a.id, a.nome, a.descricao, g.nome AS game_nome, g.genero AS game_genero
                FROM achievements a
                JOIN games g ON a.game_id = g.id
                WHERE a.user_id = ?
                ORDER BY g.nome
            """
            db.cursor.execute(query, (user_id,))
            rows = db.cursor.fetchall()

            jogos_agrupados = {}
            for row in rows:
                jogo = row['game_nome']
                if jogo not in jogos_agrupados:
                    jogos_agrupados[jogo] = {
                        'genero': row['game_genero'],
                        'conquistas': []
                    }
                jogos_agrupados[jogo]['conquistas'].append({
                    'id': row['id'],
                    'nome': row['nome'],
                    'descricao': row['descricao']
                })
            return jogos_agrupados

    @classmethod
    def create(cls, nome, descricao, game_id, user_id):
        with DatabaseConnection() as db:
            query = """
                INSERT INTO achievements (nome, descricao, game_id, user_id)
                VALUES (?, ?, ?, ?)
            """
            db.cursor.execute(query, (nome, descricao, game_id, user_id))

    @classmethod
    def delete(cls, achievement_id, user_id):
        with DatabaseConnection() as db:
            query = "DELETE FROM achievements WHERE id = ? AND user_id = ?"
            db.cursor.execute(query, (achievement_id, user_id))

    @classmethod
    def get_descricao_by_game_and_nome(cls, game_id, nome):
        with DatabaseConnection() as db:
            query = "SELECT descricao FROM achievements WHERE game_id = ? AND nome = ? LIMIT 1"
            db.cursor.execute(query, (game_id, nome))
            row = db.cursor.fetchone()
            if row and row['descricao']:
                return row['descricao']
            return "Conquista desbloqueada pelo jogador"

    @classmethod
    def user_has_achievement(cls, user_id, game_id, nome):
        """Verifica se o jogador já possui essa conquista neste jogo."""
        with DatabaseConnection() as db:
            query = "SELECT id FROM achievements WHERE user_id = ? AND game_id = ? AND nome = ?"
            db.cursor.execute(query, (user_id, game_id, nome))
            return db.cursor.fetchone() is not None