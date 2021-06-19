from typing import List, Optional
from fastapi import Request, Query, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import databases
import sqlalchemy
from sqlalchemy import and_
from fastapi import FastAPI
from pydantic import BaseModel
from services import check_token

# SQLAlchemy specific code, as with any other app

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
    image: str
    shape: str
    glasses_type: str
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


async def prepare_filter(brand, color, gender, glass_type, shape):
    conditions = []
    if brand is not None:
        conditions.append(notes.c.brand.in_(brand))
    if gender is not None:
        conditions.append(notes.c.gender.in_(gender))
    if color is not None:
        conditions.append(notes.c.colors.in_(color))
    if glass_type is not None:
        conditions.append(notes.c.glasses_type.in_(glass_type))
    if shape is not None:
        a = conditions.append(notes.c.shape.in_(shape))
    return conditions


class Filter(BaseModel):
    categories: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None
    glass_type: Optional[str] = None
    shape: Optional[str] = None


async def activate_foreign_keys():
    statement = await database.execute('PRAGMA foreign_keys = ON;')
    return statement


@router.get("/shop/")
async def shop(request: Request, page_num: Optional[int] = 1, brand: Optional[List[str]] = Query(None),
               color: Optional[List[str]] = Query(None),
               gender: Optional[List[str]] = Query(None), glass_type: Optional[List[str]] = Query(None),
               shape: Optional[List[str]] = Query(None)):
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    a = await activate_foreign_keys()
    brands = 'select distinct brand from glasses'
    brands = await database.fetch_all(query=brands)
    colors = 'select distinct colors from glasses'
    colors = await database.fetch_all(query=colors)
    shapes = 'select distinct shape from glasses'
    shapes = await database.fetch_all(query=shapes)
    result = None
    filter_query = await prepare_filter(brand, color, gender, glass_type, shape)
    if filter_query:
        filter_query = notes.select().where(and_(*filter_query))

        result = await database.fetch_all(query=filter_query)

    else:
        range_1 = 10 * page_num - 9
        range_2 = page_num * 10 - 1
        results = notes.select().offset(range_1).limit(range_2)
        result = await database.fetch_all(results)
    return templates.TemplateResponse('catalog-page.html',
                                      {'request': request, 'query': result, 'brands': brands, 'colors': colors,
                                       'shapes': shapes, 'flag': flag})


@router.post('/add-glass')
async def add_glasses(request: Request, glass: Glass):
    foreign_keys = await activate_foreign_keys()
    print(glass)
    add_item = notes.insert().values(name=glass.name, brand=glass.brand, gender=glass.gender, colors=glass.color,
                                     shape=glass.shape, glasses_type=glass.shape, price=glass.price, image=glass.image)
    excec_add_item = await database.execute(add_item)


@router.post('/modify')
async def add_glasses(request: Request, glass: Glass):

    pass


@router.get('/add-glass')
async def add_glasses(request: Request):
    token_status = check_token.get_token(request)
    flag, user_id, admin = False, None, False
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    is_admin = 'select is_superuser from user where id=:user_id'
    exce_is_admin = await database.fetch_one(query=is_admin, values={'user_id': user_id})
    if exce_is_admin is not None and exce_is_admin[0]:
        admin = True
        return templates.TemplateResponse('add-glasses.html', {'request': request, 'flag': flag})
    else:
        return templates.TemplateResponse('unauth.html', {'request': request})