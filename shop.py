from typing import List, Optional
from fastapi import FastAPI, Request, Query, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import databases
from sqlalchemy.orm import relationship
from starlette.responses import RedirectResponse
import sqlalchemy
from sqlalchemy import and_, ColumnDefault
from fastapi import FastAPI
from pydantic import BaseModel
from views import check_token
from sqlalchemy import event

# SQLAlchemy specific code, as with any other app
from starlette.status import HTTP_302_FOUND

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

user = sqlalchemy.Table('user', metadata, autoload=True, autoload_with=engine)

notes = sqlalchemy.Table(

    "glasses",

    metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),

    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("brand", sqlalchemy.String),
    sqlalchemy.Column('gender', sqlalchemy.String),
    sqlalchemy.Column("colors", sqlalchemy.String),
    sqlalchemy.Column('image', sqlalchemy.String),
    sqlalchemy.Column('shape', sqlalchemy.String),
    sqlalchemy.Column('glasses_type', sqlalchemy.String),
    sqlalchemy.Column('price', sqlalchemy.Integer)

)

cart = sqlalchemy.Table(
    "cart",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("quantity", sqlalchemy.Integer, default=1, nullable=False),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('user.id')),
    sqlalchemy.Column('glasses_id', sqlalchemy.ForeignKey(notes.c.id)),
)

metadata.create_all(engine)


class Glass(BaseModel):
    name: str
    brand: str
    gender: str
    color: str
    shape: str
    price: int


app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.on_event("startup")
# async def startup():
#     await database.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


def split_filter(filters):
    filtered = {}

    for word, colour in filters:
        filtered.setdefault(colour, []).append((word))
    return filtered


async def prepare_filter(brand, color, gender, glass_type):
    conditions = []
    if brand is not None:
        conditions.append(notes.c.brand.in_(brand))
    if gender is not None:
        conditions.append(notes.c.gender.in_(gender))
    if color is not None:
        conditions.append(notes.c.colors.in_(color))
    if glass_type is not None:
        conditions.append(notes.c.glasses_type.in_(glass_type))
    return conditions


class Filter(BaseModel):
    categories: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None
    glass_type: Optional[str] = None


async def activate_foreign_keys():
    statement = await database.execute('PRAGMA foreign_keys = ON;')
    return statement


@router.get("/shop/")
async def shop(request: Request, brand: Optional[List[str]] = Query(None),
               color: Optional[List[str]] = Query(None),
               gender: Optional[List[str]] = Query(None), glass_type: Optional[List[str]] = Query(None)):
    a = await activate_foreign_keys()
    brands = 'select distinct brand from glasses'
    brands = await database.fetch_all(query=brands)
    colors = 'select distinct colors from glasses'
    colors = await database.fetch_all(query=colors)
    result = None
    filter_query = await prepare_filter(brand, color, gender, glass_type)
    if filter_query:
        filter_query = notes.select().where(and_(*filter_query))
        result = await database.fetch_all(query=filter_query)
    else:
        results = notes.select()
        result = await database.fetch_all(results)
    token = request.cookies.get('fastapiusersauth')
    token_validity = check_token.validate_token(token)
    flag, user_id = None, None
    if type(token_validity) == dict:
        flag = True
        user_id = token_validity.get('user_id')
    if flag != True:
        flag = False
    print(flag, user_id)
    return templates.TemplateResponse('catalog-page.html',
                                      {'request': request, 'query': result, 'brands': brands, 'colors': colors,
                                       'flag': flag})


@router.post('/add-glass')
async def add_glasses(request: Request, glass: Glass):
    add_item = notes.insert().values(name=glass.name, brand=glass.brand, gender=glass.gender, colors=glass.color,
                                     shape=glass.shape, glasses_type=glass.shape, price=glass.price)


@router.get('/add-glass')
async def add_glasses(request: Request):
    return templates.TemplateResponse('add-glasses.html', {'request': request})
