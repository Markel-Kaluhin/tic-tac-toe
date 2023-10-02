from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool


def make_engine(settings) -> Engine:
    connect_args = {
        # 'connect_timeout': 3
    }
    if "external_host" in settings:
        connect_args["application_name"] = settings["external_host"]

    return create_engine(
        settings["db_url"],
        echo=settings.get("db_echo_flag", False),
        echo_pool=settings.get("db_echo_pool_flag", False),
        pool_recycle=settings.get("db_pool_recycle", 3600),
        pool_pre_ping=settings.get("db_pool_pre_ping", True),
        connect_args=connect_args,
        poolclass=NullPool,
    )


def make_session(engine, **kwargs) -> scoped_session:
    return scoped_session(sessionmaker(bind=engine, autoflush=False, **kwargs))


def delete_session(db_session) -> None:
    db_session.close()
    db_session.remove()
