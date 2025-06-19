from pydantic import BaseModel, validator
from .product import Product

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    @validator("quantity")
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("數量必須大於 0")
        return v

class CartItem(CartItemCreate):
    id: int
    product: Product

    class Config:
        orm_mode = True