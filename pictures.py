from os import listdir
from random import choice
from requests import get

async def fetch(bot, message):
    urls = [
        "https://some-random-api.ml/img/bird",
        "https://some-random-api.ml/img/raccoon",
        "https://some-random-api.ml/img/cat",
        "https://some-random-api.ml/img/dog",
        "https://some-random-api.ml/img/fox",
        "https://some-random-api.ml/img/kangaroo",
        "https://some-random-api.ml/img/koala",
        "https://some-random-api.ml/img/panda",
        "https://some-random-api.ml/img/red_panda",
        "https://some-random-api.ml/img/whale",
    ]
    # делаем запрос по случайной ссылке
    resp = get(choice(urls))
    # проверка статуса запроса
    if 300 > resp.status_code >= 200:
        content = resp.json()
    else:
        content = f"Recieved a bad status code of {resp.status_code}."
    await answer_content(bot, content, message)

async def answer_content(bot, content, message):
    if type(content) != str:
        await bot.send_photo(message.chat.id, content['link'])
    else:
        # если запрос по апи не сработал то выводим сохраненные фото
        photos = listdir('pic')
        photo = 'pic/' + choice(photos)
        with open(photo, 'rb') as ph:
            await bot.send_photo(
                message.chat.id,
                ph
            )

