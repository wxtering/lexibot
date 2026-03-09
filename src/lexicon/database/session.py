from configuration.cfg import DatabaseConfig
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

dbconfig = DatabaseConfig()

engine = create_async_engine(dbconfig.db_url, echo=dbconfig.db_echo)

DEFAULT_SESSION_FACTORY = async_sessionmaker[AsyncSession](
    engine, expire_on_commit=False
)
