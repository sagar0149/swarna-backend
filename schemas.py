from pydantic import BaseModel
from typing import Optional

# This dictates exactly what information someone MUST provide 
# when they want to add new furniture to the database.
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None  # Optional means they can leave it blank
    wood_type: str
    price: float
    stock_quantity: int = 0

# This dictates what information our server sends BACK after it's successfully saved.
# It includes everything above, plus the unique ID the database assigns it.
class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True
        