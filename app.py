import copy

import fastapi
import uvicorn
from fastapi import Request
import database
import pydantic_modules
import config

api = fastapi.FastAPI()

response = {"Answer": "From Server"}

fake_database = {'users': [
    {
        "id": 1,  # тут тип данных - число
        "name": "Anna",  # тут строка
        "nick": "Anny42",  # и тут
        "balance": 15.01  # а тут float
    },

    {
        "id": 2,  # у второго пользователя
        "name": "Dima",  # такие же
        "nick": "dimon2319",  # типы
        "balance": 8.01  # данных
    }
    , {
        "id": 3,  # у третьего
        "name": "Vladimir",  # юзера
        "nick": "Vova777",  # мы специально сделаем
        "balance": "23"  # нестандартный тип данных в его балансе
    }
], }

@api.get('/users/')
def get_users(skip: int = 0, limit: int = 10):
    return fake_database['users'][skip: skip + limit]


@api.post('/user/create')
def index(user: pydantic_modules.User):
    """
    Когда в пути нет никаких параметров
    и не используются никакие переменные,
    то fastapi, понимая, что у нас есть аргумент, который
    надо заполнить, начинает искать его в теле запроса,
    в данном случае он берёт информацию, которую мы ему отправляем
    в теле запроса и сверяет её с моделью pydantic, если всё хорошо,
    то в аргумент user будет загружен наш объект, который мы отрправляем
    на север
    """
    fake_database['users'].append(user)
    return {'User Created': user}


@api.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_modules.User = fastapi.Body()):  # Используя fastapi.Body мы явно
    # указыввем что отправляем информацию в теле запроса
    for index, u in enumerate(fake_database['users']):
        if u['id'] == user_id:
            fake_database['users'][index] = user
            return user

@api.get('/get_info_by_user_id/{id:int}')
def get_info_about_user(id):
    return fake_database['users'][id-1]

@api.get('/get_user_balance_by_id/{id:int}')
def get_info_about_user(id):
    return fake_database['users'][id-1]['balance']

@api.get('/get_total_balance')
def get_info_about_user():
    total_balance: float = 0.0
    for user in fake_database['users']:
        total_balance += pydantic_modules.User(**user).balance
    return total_balance

@api.delete('/user/{user_id}')
def delete_user(user_id: int = fastapi.Path()):
    for index, u in enumerate(fake_database['users']):
        if u['id'] == user_id:
            old_db = copy.deepcopy(fake_database)
            del fake_database['users'][index]
            return {'old_db': old_db,
                    'new_db': fake_database}


if __name__ == '__main__':
    uvicorn.run(api)
