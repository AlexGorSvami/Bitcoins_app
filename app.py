import fastapi
import uvicorn
import database
import pydantic_modules
import config

api = fastapi.FastAPI()

response = {"Answer": "From Server"}

fake_database = {'users':[
    {
        "id":1,             # тут тип данных - число
        "name":"Anna",      # тут строка
        "nick":"Anny42",    # и тут
        "balance": 15.01    # а тут float
     },

    {
        "id":2,             # у второго пользователя 
        "name":"Dima",      # такие же 
        "nick":"dimon2319", # типы 
        "balance": 8.01     # данных
     }
    ,{
        "id":3,             # у третьего
        "name":"Vladimir",  # юзера
        "nick":"Vova777",   # мы специально сделаем 
        "balance": "23"     # нестандартный тип данных в его балансе
     }
],}

@api.get('/')
def index():
    return response


@api.get('/user/{nick}')
def get_nick(nick):
    return {'user': nick}


@api.get('/usrid/{id:int}')
def get_id(id):
    return {'user': id}


@api.get('/get_info_by_user_id{id:int}')
def get_info_about_user(id):
    return fake_database['users'][id-1]

@api.get('/get_user_balance_by_id/{id:int}')
def get_user_balance(id):
    return fake_database['users'][id-1]['balance']

@api.get('/get_total_balance')
def get_total_balance():
    total_balance: float = 0.0
    for user in fake_database['users']:
        total_balance += pydantic_modules.User(**user).balance
    return total_balance

@api.get("/users/")
def get_users(skip: int = 0, limit: int = 10):
    return fake_database['users'][skip: skip + limit]




if __name__ == "__main__":
    uvicorn.run("app:api", host="0.0.0.0", port=9999, reload=True)
