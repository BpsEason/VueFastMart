from pydantic import BaseModel, validator

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int

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