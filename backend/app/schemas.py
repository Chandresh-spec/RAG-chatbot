from pydantic import BaseModel,Field,EmailStr




class bodyIn(BaseModel):
    email:str
    otp:str





class RegisterbodyIn(BaseModel):
    email:EmailStr
    name:str=Field(min_length=5,max_length=20)
    password:str=Field(min_length=8,max_length=20)


class LoginBodyIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=20)
