from pydantic import BaseModel, validator
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("價格必須大於 0")
        return v

    @validator("stock")
    def stock_non_negative(cls, v):
        if v < 0:
            raise ValueError("庫存不能為負")
        return v

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True