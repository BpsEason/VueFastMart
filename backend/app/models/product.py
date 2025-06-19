from sqlalchemy import Column, Integer, String, Float, Text, Index, CheckConstraint
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)

    __table_args__ = (
        Index('idx_name', 'name'),
        CheckConstraint('price > 0', name='positive_price'),
        CheckConstraint('stock >= 0', name='non_negative_stock'),
    )