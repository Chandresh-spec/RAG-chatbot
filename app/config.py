from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    sync_database_url:str
    async_database_url:str
    pool_size:int
    max_overflow:int
    pool_pre_ping:bool
    pool_timeout:int
    pool_recycle:int
    




    model_config=SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        ignore=True
    )



@lru_cache
def get_settings():
    return Settings()

settings=get_settings()