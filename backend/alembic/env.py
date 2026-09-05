import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

# Add backend directory to sys.path so app module is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import Base, DATABASE_URL, engine
from app.models.models import (
    User,
    Case,
    CaseEvent,
    Document,
    Communication,
    Specialist,
    Appointment,
    Escalation,
    FollowUp,
    AgentObservation,
    Bottleneck,
    AgentRecommendation,
    Action,
    ActionVerification,
    AgentRun,
    AgentRunStep,
)

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy target metadata
target_metadata = Base.metadata

if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url") or DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True if url and "sqlite" in url else False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use existing database engine
    is_sqlite = DATABASE_URL.startswith("sqlite")
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
