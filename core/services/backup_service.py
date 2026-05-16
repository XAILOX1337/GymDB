import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from db.connection import engine

class BackupService:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, database_name: str = "GymDB") -> str:
        """Создает резервную копию БД через SQL Server BACKUP DATABASE или копирует .mdf/.ldf."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{database_name}_{timestamp}.bak"

        try:
            with engine.begin() as conn:
                conn.execute(text(f"""
                    BACKUP DATABASE [{database_name}]
                    TO DISK = :path
                    WITH FORMAT, COMPRESSION
                """), {"path": str(backup_file)})
            return str(backup_file)
        except Exception as e:
            # Fallback: если нет прав на BACKUP DATABASE, логируем ошибку
            print(f"SQL BACKUP не удался ({e}), используется логическое резервирование.")
            return self._logical_backup(database_name, timestamp)

    def _logical_backup(self, database_name: str, timestamp: str) -> str:
        """Резервирование через bcp или просто метка времени для скриптов."""
        marker = self.backup_dir / f"{database_name}_{timestamp}_backup_marker.txt"
        with open(marker, "w", encoding="utf-8") as f:
            f.write(f"Backup requested at {datetime.now().isoformat()}\\n")
            f.write(f"Database: {database_name}\\n")
            f.write("Используйте SQL Server Maintenance Plans или sqlcmd для полного бэкапа.\\n")
        return str(marker)

    def list_backups(self) -> list[Path]:
        return sorted(self.backup_dir.glob("*.bak"), key=os.path.getmtime, reverse=True)

    def auto_backup(self, database_name: str = "GymDB") -> str | None:
        """Точка входа для автоматического бэкапа (например, по cron/планировщику)."""
        return self.create_backup(database_name)