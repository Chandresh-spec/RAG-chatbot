from ..core.redis import get_redis_client
from fastapi  import HTTPException,status,APIRouter,Depends
from ..database import get_db_async
from ..models import User
from .email_service import OtpService,RateLimiting,VerifyResult
from sqlalchemy.exc import IntegrityError
from ..schemas import bodyIn,RegisterbodyIn,LoginBodyIn
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from ..core.redis import get_redis_client
from sqlalchemy import select
from ..auth import hash_password
import logging

logger=logging.getLogger(__name__)
auth_router=APIRouter(
    prefix="/api/auth",
    tags=['auth_router']
)


async def issue_and_send(email:str,svc:OtpService):
    
    try:
         otp=await svc.__issue(email)
    except RateLimiting as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"To many Request Try After {e.retry_after}",
            headers=f"retry fater {e.retry_after}"
        )

    return otp



@auth_router.post("/verify_otp")
async def verify_otp(
        body:bodyIn,
        db:AsyncSession=Depends(get_db_async),
        svc:OtpService=Depends(get_redis_client)
):
    email=body.email.strip()
    result=await svc.__verify(email,body.otp)

    if result == VerifyResult.LOCKED:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")
    if result == VerifyResult.EXPIRED:
        raise HTTPException(status_code=400, detail="Code expired or not requested")
    if result == VerifyResult.WRONG:
        raise HTTPException(status_code=400, detail="Invalid verification code")


    stmt=select(User).where(User.email==email)
    res=await db.execute(stmt)
    user_email=res.scalar_one_or_none()

    user_email.is_verified=True

    db.add(user_email)
    db.commit()
    db.refresh(user_email)

    return {
        "msg":"otp verification completed"
    }
    



@auth_router.post('/register')
async def register(
    body:RegisterbodyIn,
    db:AsyncSession=Depends(get_db_async),
):
    email=body.email.strip().lower()
    stmt=select(User).where(User.email==email)
    res=await db.execute(stmt)
    existing_user=res.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Should be unqiue"
        )

    user=User(
        email=email,
        name=body.name.strip().low(),
        password=hash_password(body.password.strip())
    )


    await db.add(user)
    try:
        await db.commit()
        logger.info("User commited sucesfully")
    except IntegrityError:
         await db.rollback()
         logger.exception("email must be unqiue")
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Email Must be Unique"
         )

    otp=await issue_and_send(email)
    return {
        "message":"User Registerred and Do the email verification",
        "otp":otp
    }

    
   





