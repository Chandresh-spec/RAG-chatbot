
from redis.asyncio import Redis
from config import settings
import hashlib
import secrets
import hmac
import enum as Enum
from fastapi import Depends
from ..core.redis import get_redis_client


LUA_SCRIPT = """
local stored = redis.call('GET', KEYS[1])
if not stored then return -1 end

local attempts = redis.call('INCR', KEYS[2])
if attempts == 1 then redis.call('EXPIRE', KEYS[2], tonumber(ARGV[3])) end

if attempts > tonumber(ARGV[2]) then
   redis.call('DEL', KEYS[1], KEYS[2])
   return -2
end

if stored == ARGV[1] then
   redis.call('DEL', KEYS[1], KEYS[2])
   return 1
end
return 0
"""


class VerifyResult(Enum):
    OK = 1
    WRONG = 0
    EXPIRED = -1
    LOCKED = -2



def _k(kind:str,email:str):
    return f"code:{kind}:{email}"

class RateLimiting(Exception):
    def __init__(self,retry_after):
        self.retry_after=max(retry_after,1)


def generate_otp():
    return f"{secrets.randbelow(10*6):06d}"

def hash_otp(email:str,otp:str):
    return hmac.new(f"{settings.otp_secret_key}".encode,f"{email}:{otp}".encode(),hashlib.sha256).hexdigest()

class OtpService:
    def __init__(self,redis:Redis):
        self.redis=redis
        self.verify_script=redis.register_script(LUA_SCRIPT)


    async def __issue(self,email):
        ok=await self.redis.set(_k("cooldown",email),1,nx=True,ex=settings.otp_cooldown)
        if not ok:
            ttl=await self.redis.ttl(_k("cooldown",email))
            raise RateLimiting(ttl)

        sends_key=_k("attempts",email)
        sends=await self.redis.incr(sends_key)

        if sends == 1:
            await self.redis.expire(sends_key,3600)

        if sends >settings.otp_max_attempt_per_hours:
            raise RateLimiting(await self.redis.ttl(sends_key))

        otp=generate_otp()
        pipe=await self.redis.pipeline(transaction=True)

        pipe.set(_k("code",email),hash_otp(email,otp),ex=settings.otp_cooldown)
        pipe.delete(_k("attempts",email))
        pipe.execute()

        return otp

    async def __verify(self,email:str,otp:str):
      res=await self.verify_script(
          keys=[
              _k("code",email),
              _k("attempts",email)
          ],
          args=[
              hash_otp(email,otp),
              settings.otp_max_attempts,
              settings.otp_ttl_expiry
          ]



      )
      return VerifyResult(int(res))
        
           

async def get_otp_service(redis:Redis=Depends(get_redis_client)):
    return  OtpService(redis)
        
        


