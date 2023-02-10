import shutil
from typing import Optional, List
import json
import uvicorn
import base64
import login.users
import shop
import databases
import sqlalchemy
from fastapi import FastAPI, Request, Form
from product import router
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI, File, UploadFile
from shop import router
import product
from login import users
from login.users import database
from views import check_token
import cart

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(shop.router)
app.include_router(users.router)
app.include_router(product.router)
app.include_router(cart.router)

templates = Jinja2Templates(directory="templates")


@app.get("/analyze", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/")
async def index(request: Request):
    glasses = 'select * from glasses limit 3'
    glasses = await database.fetch_all(query=glasses)
    return templates.TemplateResponse("index.html", {"request": request, 'glasses': glasses})


@app.get('/upload/')
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload/")
async def create_upload_file(request: Request, file: UploadFile = File(None), image: Optional[str] = None):
    # form = await request.body()
    # form1 = json.loads(form.decode('utf-8'))
    # base = form1['image'].replace("data:image/png;base64,", "")
    # base = base64.urlsafe_b64decode(base)
    #
    # f = open("temp.png", "wb")
    # f.write(base)
    # f.close()

    # with open("imageToSave.png", "wb") as fh:
    #     fh.write(base64.b64decode(form1['image']))

    # if image is None:
    with open("destination.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # else:
    #     with open("imageToSave.png", "wb") as fh:
    #         fh.write(base64.decodebytes(image))

    return 'success'


@app.post('/check/')
async def test(request: Request):
    validate_token = check_token.validate_token(request.headers)
    print(validate_token)
    return validate_token


@app.get('/a/')
async def test(request: Request):
    # valid_token = check_token.validate_token(request.headers)
    # print(valid_token)
    return templates.TemplateResponse("a.html", {"request": request})




