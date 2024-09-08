from pydantic import BaseModel, EmailStr, Field

class ServiceResponse(BaseModel):
    id: int
    title: str
    description: str
    picture: str

    class Config:
        from_attributes = True