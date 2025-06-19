from sqlalchemy import Column, Integer, String, Float, Text, Index
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    __table_args__ = (Index('idx_name', 'name'),)