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

movies = [
    {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Acción"
	},
    {
		"id": 2,
		"title": "2012",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "ficcion"
	}
]

@app.get("/", tags=["Home"])
def message():
    return HTMLResponse('<h1>Hello world</h1>')

@app.get("/movies", tags=["Movies"])
def get_movies():
    return movies

@app.get("/movies/{id}", tags=["Movies"])
def get_movie(id: int):
    for item in movies:
        if item["id"] == id:
            return item
    return []

@app.get("/movies/", tags=["Movies"])
def get_movies_by_category(category: str):
    return [ item for item in movies if item["category"] == category ]

@app.post("/movies", tags=["Movies"])
def create_movie(id: int = Body(), title: str = Body(), overview: str = Body(), year: int = Body(), rating: float = Body(), category: str = Body()):
    movies.append({
        "id": id,
        "title": title,
        "overview": overview,
        "year": year,
        "rating": rating,
        "category": category
    })
    return movies

@app.put('/movies/{id}', tags=["Movies"])
def update_movie(id: int, title: str = Body(), overview: str = Body(), year: int = Body(), rating: float = Body(), category: str = Body()):
    for item in movies:
        if item["id"] == id:
            item["title"] = title
            item["overview"] = overview
            item["year"] = year
            item["rating"] = rating
            item["category"] = category

    return movies

@app.delete('/movies/{id}', tags=["Movies"])
def delete_movie(id: int):
    for item in movies:
        if item["id"] == id:
            movies.remove(item)

    return movies

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






