import base64
import shutil
from typing import Optional
import json
from pydantic import BaseModel
from sqlalchemy import and_
from starlette.middleware.cors import CORSMiddleware

from shop import notes
import shop
from fastapi import Request, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile
import product
from login import users
from login.users import database
from services import check_token
import cart
from cart import cart as cart_db
from shop import notes

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    is_admin = 'select is_superuser from user where id=:user_id'
    exce_is_admin = await database.fetch_one(query=is_admin, values={'user_id': user_id})
    if exce_is_admin is not None and exce_is_admin[0]:
        admin = True
    glasses = 'select * from glasses limit 6'
    glasses = await database.fetch_all(query=glasses)

    return templates.TemplateResponse("index.html",
                                      {"request": request, 'glasses': glasses, 'flag': flag, 'admin': admin})


@app.get('/upload/')
async def upload(request: Request):
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    return templates.TemplateResponse("upload.html", {"request": request, 'flag': flag})


class Face(BaseModel):
    image: Optional[str]


@app.post("/upload/")
async def create_upload_file(request: Request, image: Optional[str] = Body(None, embed=True),
                             file: UploadFile = File(None)):
    token_status = check_token.get_token(request)
    flag = False
    if token_status['valid']:
        flag = True
    if file != None:
        with open("destination.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:

        form = await request.body()
        form1 = json.loads(form.decode('utf-8'))
        base = form1['image'].replace("data:image/png;base64,", "")
        base = base64.urlsafe_b64decode(base)

        f = open("temp.png", "wb")
        f.write(base)
        f.close()
    # if image is not None:

    # else:

    return 'success'


@app.get('/delete-from-cart/{item_id}')
async def delete_item(request: Request, item_id: str):
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    print(item_id)
    get_id = notes.select().where(notes.c.name == item_id)
    excec_get_id = await database.fetch_one(get_id)
    print(excec_get_id)
    remove_item = cart_db.delete().where(and_(cart_db.c.user_id == user_id, cart_db.c.glasses_id == excec_get_id[0]))
    excex_remove_item = await database.execute(remove_item)
    return 'success'


@app.get('/about-us/')
async def about_us(request: Request):
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    return templates.TemplateResponse('about-us.html', {"request": request, 'flag': flag})


