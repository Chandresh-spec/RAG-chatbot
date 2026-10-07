from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy import create_engine
from .config import settings
import logging
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker


logger=logging.getLogger(__name__)

sync_engine=create_engine(
    settings.sync_database_url,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_pre_ping=settings.pool_pre_ping,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle

)


sync_local_session=sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False
)



def get_db():
    session=sync_local_session()
    try:
        yield session
    except Exception:
        logger.exception("Db rolledbackk")
        raise

    finally:
        session.close()



class Base(DeclarativeBase):
    pass


#________________ASYNCDRIVER____________________________


async_engine=create_async_engine(
    settings.async_database_url,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_pre_ping=settings.pool_pre_ping,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle
)


async_local_session=async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
    
)



async def get_db_async():
    session=async_local_session()
    try:
        yield session
    except Exception:
        logger.exception("DB ROLLEDBACK")
    finally:
        await session.close()