from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import HTMLResponse
from config.database import Session, engine, Base
from models.product import Product

import cv2
from pyzbar.pyzbar import decode
import numpy as np

app = FastAPI()
app.title = "Mi aplicación con FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

@app.get("/products", tags=["Products"])
def get_products():
    session = Session()
    products = session.query(Product).all()
    session.close()
    return products

@app.post("/products", tags=["Products"])
async def create_product(name: str = Body(), description: str = Body(), price: float = Body(), stock: int = Body(), file: UploadFile = File(...)):
    code = await read_code_from_file(file)
    
    session = Session()
    product = Product(name=name, description=description, price=price, stock=stock, barcode=code)
    session.add(product)
    session.commit()
    session.close()
    return product

@app.post("/products/by_barcode", tags=["Products"])
async def get_product_by_barcode(file: UploadFile = File(...)):
    code = await read_code_from_file(file)
    
    session = Session()
    product = session.query(Product).filter(Product.barcode == code).first()
    session.close()
    return product

async def read_code_from_file(file: UploadFile) -> np.ndarray:
    # Leer la imagen recibida
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Decodificar el código de barras
    decoded_objects = decode(img)
    codes = [obj.data.decode('utf-8') for obj in decoded_objects]

    return codes[0]






