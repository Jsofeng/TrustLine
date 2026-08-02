#alembic/env.py tells Alembic how to connect to your database and which SQLAlchemy models it should watch when creating migrations.
#Alembic is a tracked set of instructions that safely updates a relational database's schema (e.g., adding tables, columns, or constraints) over time
import os 
from logging.config import fileConfig # Loads Alembic's logging configuration -> Make Alembic output logs properly

from alembic import context #This is Alembic's control object its what gives it control
from sqlalchemy import engine_from_config, pool 

from app.db.base import Base
from app.db import models


config = context.config

#Loads logging settings.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

#DATABASE CONNECTION
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("MIGRATION_DATABASE_URL", config.get_main_option("sqlalchemy.url")),
)

target_metadata = Base.metadata #These are the tables I should compare against the database


def run_migration_offline() -> None: #generates SQL without connecting to the database.
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migration_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool) #connects to engine and from config.get_section -> Gets settings from: alembic.ini starting with the word "sqlalchemy." poolclass=pool.NullPool Create a fresh connection. Don't save it
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode:
    run_migration_offline()

else:
    run_migration_online()