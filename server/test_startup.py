"""
Тестовый скрипт для проверки автоматического применения миграций
"""
import subprocess
import sys

print("="*60)
print("Проверка применения миграций...")
print("="*60)

result = subprocess.run(
    ["alembic", "current"],
    cwd="server",
    capture_output=True,
    text=True
)

print(f"Текущая ревизия: {result.stdout}")
print(f"Статус: {'OK' if result.returncode == 0 else 'ERR'}")

