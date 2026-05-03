from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List
import os
import shutil
import uuid

os.makedirs("static/images", exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Product Table
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    wood_type = Column(String)
    price = Column(Float)
    stock_quantity = Column(Integer)
    description = Column(String)
    image_urls = Column(String, nullable=True)

# 2. Store Settings Table
class StoreSettings(Base):
    __tablename__ = "store_settings"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, default="+977-0000000000")
    email = Column(String, default="info@swarnalakshmi.com")
    address = Column(String, default="Lahan, Madhesh Province, Nepal")
    facebook = Column(String, default="")
    instagram = Column(String, default="")

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# === THE CORS FIX IS SAFELY APPLIED HERE ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "https://swarna-laxmi-furniture.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PRODUCT ROUTES ---
@app.get("/products/")
def read_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/products/")
async def create_product(
    name: str = Form(...), wood_type: str = Form(...), price: float = Form(...),
    stock_quantity: int = Form(...), description: str = Form(""),
    images: List[UploadFile] = File(None), db: Session = Depends(get_db)
):
    saved_urls = []
    if images:
        for image in images:
            if image.filename:
                unique_filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = f"static/images/{unique_filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                saved_urls.append(f"https://swarna-laxmi-furniture-udyog.onrender.com/{file_path}")

    image_urls_string = ",".join(saved_urls) if saved_urls else None
    new_product = Product(name=name, wood_type=wood_type, price=price, stock_quantity=stock_quantity, description=description, image_urls=image_urls_string)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{product_id}")
async def update_product(
    product_id: int, name: str = Form(...), wood_type: str = Form(...), price: float = Form(...),
    stock_quantity: int = Form(...), description: str = Form(""),
    images: List[UploadFile] = File(None), db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")

    product.name, product.wood_type, product.price = name, wood_type, price
    product.stock_quantity, product.description = stock_quantity, description

    if images and images[0].filename != '':
        if product.image_urls:
            for url in product.image_urls.split(","):
                file_path = url.replace("https://swarna-laxmi-furniture-udyog.onrender.com/", "")
                if os.path.exists(file_path): os.remove(file_path)
        saved_urls = []
        for image in images:
            unique_filename = f"{uuid.uuid4()}_{image.filename}"
            file_path = f"static/images/{unique_filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            saved_urls.append(f"https://swarna-laxmi-furniture-udyog.onrender.com/{file_path}")
        product.image_urls = ",".join(saved_urls)
    
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    if product.image_urls:
        for url in product.image_urls.split(","):
            file_path = url.replace("https://swarna-laxmi-furniture-udyog.onrender.com/", "")
            if os.path.exists(file_path): os.remove(file_path)
    db.delete(product)
    db.commit()
    return {"message": "Deleted"}

# --- SETTINGS ROUTES ---
@app.post("/settings/hero/")
async def upload_hero_image(image: UploadFile = File(...)):
    file_path = "static/images/hero.jpg"
    with open(file_path, "wb") as buffer: shutil.copyfileobj(image.file, buffer)
    return {"message": "Hero image updated"}

@app.get("/settings/contact/")
def get_contact(db: Session = Depends(get_db)):
    settings = db.query(StoreSettings).first()
    if not settings:
        settings = StoreSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.put("/settings/contact/")
def update_contact(
    phone: str = Form(""), email: str = Form(""), address: str = Form(""),
    facebook: str = Form(""), instagram: str = Form(""), db: Session = Depends(get_db)
):
    settings = db.query(StoreSettings).first()
    if not settings:
        settings = StoreSettings(id=1)
        db.add(settings)
    settings.phone, settings.email, settings.address = phone, email, address
    settings.facebook, settings.instagram = facebook, instagram
    db.commit()
    db.refresh(settings)
    return settings