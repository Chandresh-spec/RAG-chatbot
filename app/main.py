from fastapi import FastAPI

from .database import Base,sync_engine
from .models import User


print(Base.metadata.__dict__)
Base.metadata.create_all(bind=sync_engine)


app=FastAPI()