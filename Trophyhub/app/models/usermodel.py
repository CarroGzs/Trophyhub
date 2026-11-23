from werkzeug.security import generate_password_hash, check_password_hash
from app.database import DatabaseConnection

class User:
    def __init__(self, username, email, password_hash=None, id=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    # --- Métodos de Instância ---

    def set_password(self, raw_password):
        """Gera e atribui o hash da senha enviada."""
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, raw_password):
        """Valida a senha fornecida comparando com o hash armazenado."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def save(self):
        """
        Insere um novo usuário (se self.id for None) ou atualiza um existente (UPDATE).
        Usa o Context Manager DatabaseConnection para execução segura em SQL puro.
        """
        with DatabaseConnection() as db:
            if self.id is None:
                query = """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                """
                db.cursor.execute(query, (self.username, self.email, self.password_hash))
                self.id = db.cursor.lastrowid
            else:
                query = """
                    UPDATE users
                    SET username = ?, email = ?, password_hash = ?
                    WHERE id = ?
                """
                db.cursor.execute(query, (self.username, self.email, self.password_hash, self.id))
        return self

    # --- Métodos de Classe (Factory / Queries) ---

    @classmethod
    def _from_row(cls, row):
        """Converte o retorno de sqlite3.Row em uma instância de User."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            created_at=row['created_at']
        )

    @classmethod
    def get_by_username(cls, username):
        """Busca por nome de usuário e retorna uma instância da classe User."""
        with DatabaseConnection() as db:
            query = "SELECT id, username, email, password_hash, created_at FROM users WHERE username = ?"
            db.cursor.execute(query, (username,))
            row = db.cursor.fetchone()
            return cls._from_row(row)

    @classmethod
    def get_by_email(cls, email):
        """Busca por e-mail e retorna uma instância da classe User."""
        with DatabaseConnection() as db:
            query = "SELECT id, username, email, password_hash, created_at FROM users WHERE email = ?"
            db.cursor.execute(query, (email,))
            row = db.cursor.fetchone()
            return cls._from_row(row)

    @classmethod
    def get_by_id(cls, user_id):
        """Busca por ID e retorna uma instância da classe User."""
        with DatabaseConnection() as db:
            query = "SELECT id, username, email, password_hash, created_at FROM users WHERE id = ?"
            db.cursor.execute(query, (user_id,))
            row = db.cursor.fetchone()
            return cls._from_row(row)