from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.cart import CartItem
from app.models.product import Product as ProductModel
from app.schemas.cart import CartItemCreate, CartItem
from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=CartItem)
def add_to_cart(
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(ProductModel).filter(ProductModel.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="庫存不足")
    product.stock -= cart_item.quantity
    db_cart_item = CartItem(
        user_id=current_user.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

@router.get("/", response_model=list[CartItem])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return cart_items

@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="購物車項目不存在")
    db.delete(cart_item)
    db.commit()
    return {"message": "已移除購物車項目"}