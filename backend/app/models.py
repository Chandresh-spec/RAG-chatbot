from .database import Base
from sqlalchemy import String,Integer,Enum as SQLENUM,func,DateTime,Boolean,UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import mapped_column,Mapped
from enum import Enum
import uuid


class StatusEnum(str,Enum):
    ACTIVE='Active'
    INACTIVE='Inactive'


class User(Base):
    __tablename__ ="users"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    email:Mapped[str]=mapped_column(String,nullable=False)
    name:Mapped[str]=mapped_column(String,unique=True,nullable=False)
    password:Mapped[str]=mapped_column(String,nullable=False)
    status:Mapped[StatusEnum]=mapped_column(SQLENUM(StatusEnum),default=StatusEnum.ACTIVE.value)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    deleted_at:Mapped[datetime | None]=mapped_column(DateTime(timezone=True),nullable=True)
    is_verified:Mapped[bool]=mapped_column(Boolean,default=False)


    __table_args__ =(UniqueConstraint(
        email,name="uq_user_email"
    ),)


