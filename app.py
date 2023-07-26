import copy
import fastapi
import uvicorn
from fastapi import FastAPI, Query, Path, File, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
import database
import pydantic_modules
import config

app = fastapi.FastAPI()

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


@app.get('/users/')
def get_users(skip: int = 0, limit: int = 10):
    return fake_database['users'][skip: skip + limit]


@app.post('/user/create')
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


@app.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_modules.User = fastapi.Body()):  # Используя fastapi.Body мы явно
    # указыввем что отправляем информацию в теле запроса
    for index, u in enumerate(fake_database['users']):
        if u['id'] == user_id:
            fake_database['users'][index] = user
            return user


@app.get('/get_info_by_user_id/{id:int}')
def get_info_about_user(id):
    return fake_database['users'][id - 1]


@app.get('/get_user_balance_by_id/{id:int}')
def get_info_about_user(id):
    return fake_database['users'][id - 1]['balance']


@app.get('/get_total_balance')
def get_info_about_user():
    total_balance: float = 0.0
    for user in fake_database['users']:
        total_balance += pydantic_modules.User(**user).balance
    return total_balance


@app.delete('/user/{user_id}')
def delete_user(user_id: int = fastapi.Path()):
    for index, u in enumerate(fake_database['users']):
        if u['id'] == user_id:
            old_db = copy.deepcopy(fake_database)
            del fake_database['users'][index]
            return {'old_db': old_db,
                    'new_db': fake_database}


@app.get("/items")
def read_items(q: str | None = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/{item_id}")
def read_items(
        *,
        item_id: int = Path(title="The ID of the item to get", gt=0, le=1000),
        q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q":q})
    return results

@app.put('/users/{user_id}')
def update_user(user_id: int, user: pydantic_modules.User = fastapi.Body()):
    for index, u in enumerate(fake_database['users']):
        if u['id'] == user_id:
            fake_database['users'][index] = user
            return user

@app.get('/response_test')
def response_test():
    return fastapi.Response("Hello", status_code=200, media_type="application/json")

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)} # вернёт клиенту размер полученного файла

@app.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    return  {"filename": file.filename} # вернёт клиенту имя полученного файла


if __name__ == '__main__':
    uvicorn.run(app)
