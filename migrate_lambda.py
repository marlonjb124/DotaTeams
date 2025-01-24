import os
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine

def lambda_handler(event, context):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    # Configurar Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    # Ejecutar migraciones
    with engine.connect() as connection:
        command.upgrade(alembic_cfg, "head")
        print("Migraciones aplicadas correctamente.")

    return {"status": "success"}
