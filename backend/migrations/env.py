from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os

# Load the Alembic configuration
config = context.config

# Interpret the config file for Python logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set up the target database URL from the environment variable or config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://van:1234@localhost/voting_db'") 
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Import your models
from app import Base  # Update 'yourapp' with the actual name of your app

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
