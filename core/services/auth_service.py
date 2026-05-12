import os
import hashlib
from sqlalchemy import text
from db.connection import engine

class AuthService:
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Генерирует соль и PBKDF2-хеш, упаковывает в 64 байта."""
        salt = os.urandom(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 15000, dklen=32
        )
        return salt + pwd_hash

    @staticmethod
    def verify_password(stored_data: bytes, password: str) -> bool:
        """Проверяет пароль против 64-байтового блока (соль + хеш)."""
        if len(stored_data) != 64:
            return False
        salt = stored_data[:32]
        stored_hash = stored_data[32:]
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 15000, dklen=32
        )
        return computed_hash == stored_hash

    def authenticate(self, login: str, password: str) -> dict | None:
        """Аутентификация сотрудника."""
        query = text("""
            SELECT e.EmployeeID, e.FirstName, e.LastName, e.PasswordHash,
                   p.AccessLevel, p.Title
            FROM dbo.Employees e
            JOIN dbo.Positions p ON e.PositionID = p.PositionID
            WHERE e.Login = :login AND e.DeletedAt IS NULL
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"login": login}).fetchone()

        if not result or not self.verify_password(result.PasswordHash, password):
            return None

        return {
            "id": result.EmployeeID,
            "name": f"{result.FirstName} {result.LastName}",
            "access_level": result.AccessLevel,
            "position": result.Title
        }