from sqlalchemy import Column, Integer, String, Float
from database import Base

# We are creating a class called Product that inherits from our database Base
class Product(Base):
    # This is the actual name of the table inside our database file
    __tablename__ = "products"

    # These are the columns in our table
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)            # e.g., "Carved Dining Table"
    description = Column(String)                 # e.g., "Handcrafted 6-seater table..."
    wood_type = Column(String)                   # e.g., "Sal Wood", "Teak", "Rosewood"
    price = Column(Float)                        # e.g., 15000.50
    stock_quantity = Column(Integer, default=0)  # How many are currently in the shop
    