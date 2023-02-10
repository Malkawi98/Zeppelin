import databases
from fastapi import FastAPI
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func

from services import check_token

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
from shop import notes

database = databases.Database(DATABASE_URL)

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@router.get("/product/{product_id}", response_class=HTMLResponse)
async def retrieve_item(request: Request, product_id: str):
    token_status = check_token.get_token(request)
    flag, user_id = False, None
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    results = notes.select().where(notes.c.id == product_id)
    result = await database.fetch_one(results)
    random_products = notes.select().order_by(func.random()).limit(3)
    random_products = await database.fetch_all(random_products)
    return templates.TemplateResponse("product-page.html",
                                      {"request": request, 'result': result,
                                       'random_products': random_products,
                                       'flag': flag, 'user_id': user_id})
