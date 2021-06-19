from fastapi import HTTPException
from shop import *

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class Cart(BaseModel):
    user_id: str
    glasses_id: str
    quantity: int = 1


@router.get("/cart/")
async def get_cart(request: Request):
    a = await activate_foreign_keys()
    token_status = check_token.get_token(request)
    flag, user_id = False, None
    if token_status['valid']:
        flag = True
        user_id = token_status['user_id']
    cart_items = cart.select().where(cart.c.user_id == user_id)
    excec_get_items = await database.fetch_all(cart_items)

    glasses_id = [i[-1] for i in excec_get_items]

    glasses_items = notes.select().where(notes.c.id.in_(glasses_id))
    excec_glasses_items = await database.fetch_all(glasses_items)
    prices = [i[8] for i in excec_glasses_items]
    total_in_cart = sum(prices)
    print(excec_get_items, total_in_cart)
    return templates.TemplateResponse('shopping-cart.html',
                                      {"request": request, 'items': excec_glasses_items, 'total': total_in_cart,
                                       'flag': flag})


@router.post('/cart/add/')
async def add_to_cart(request: Request, shop_cart: Cart):
    token = request.cookies.get('fastapiusersauth')
    token_validity = check_token.validate_token(token)
    flag, user_id = None, None
    if type(token_validity) == dict:
        flag = True
        user_id = token_validity.get('user_id')
    activate_foreign_keys()
    check_item_exists = cart.select().where(cart.c.user_id == user_id).where(cart.c.glasses_id == shop_cart.glasses_id)
    exec_item_exists = await database.fetch_one(check_item_exists)
    if exec_item_exists is not None:
        raise HTTPException(status_code=409, detail="Item already exists")
    add_item = cart.insert().values(glasses_id=shop_cart.glasses_id, user_id=shop_cart.user_id,
                                    quantity=shop_cart.quantity)
    excec_add_item = await database.execute(add_item)
    return True
