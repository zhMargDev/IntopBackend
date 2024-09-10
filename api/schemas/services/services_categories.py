from pydantic import BaseModel, EmailStr, Field

class ServiceCategoryResponse(BaseModel):
    id: int
    title: str
    description: str
    picture: str

    class Config:
        from_attributes = True