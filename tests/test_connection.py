# test_connection.py

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada no arquivo .env")

try:
    # Cria a conexão
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        print("✅ Conectado com sucesso!\n")

        print("📋 Tabelas encontradas:\n")

        result = connection.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        tables = result.fetchall()

        if not tables:
            print("⚠️ Nenhuma tabela encontrada.")
        else:
            for table in tables:
                print(f"• {table[0]}")

except SQLAlchemyError as e:
    print("❌ Erro ao conectar ao banco:")
    print(e)