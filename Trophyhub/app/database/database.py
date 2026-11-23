import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'trophyhub.db')

class DatabaseConnection:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                # Se ocorreu alguma exceção durante o 'with', cancela as alterações
                self.conn.rollback()
            else:
                # Sem erros: confirma as alterações
                self.conn.commit()
            
            self.cursor.close()
            self.conn.close()
            
        # Retorna False para permitir que exceções tratadas continuem seu fluxo
        return False

