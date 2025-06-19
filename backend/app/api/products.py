from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate
from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.cache import cache

router = APIRouter()

@router.get("/", response_model=list[Product])
@cache(timeout=60)
def get_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    products = db.execute(select(ProductModel).offset(skip).limit(limit)).scalars().all()
    return products

@router.post("/", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可新增產品")
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可更新產品")
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可刪除產品")
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    db.delete(db_product)
    db.commit()
    return {"message": "產品已刪除"}