from os import getenv
from translatepy import Translator
from requests import get

API = getenv(WEATHERAPI)  # API для погоды
translator = Translator()  # для перевода описания погоды на

async def weather_response(message):
    url = 'https://api.openweathermap.org/data/2.5/weather?q=' \
          f'{message.text},' \
          f'&APPID={API}&units=metric'
    ans = get(url)
    data = ans.json()
    if ans.status_code == 200:  # проверка статуса запроса
        # получаем описание погоды в городе и переводим на русский
        await answer_weather_to_user(message, data)
    elif ans.status_code == 404:  # проверка статуса запроса
        await message.reply("Проверьте праильность написания "
                            "города")
    else:
        # в случае если код не соответсвует неправильному написанию
        # города
        print(data['cod'], data['message'])


# Высылаем ответ пользователю
async def answer_weather_to_user(message, data):
    descr = data['weather'][0]['description']
    descr_ru = translator.translate(descr, "Russian")
    await message.reply(f"Погода в городе {message.text}:\n"
                        f"Температура => "
                        f"{round(data['main']['temp'])}\n"
                        f"Ощущается как => "
                        f"{round(data['main']['feels_like'])}\n"
                        f"{descr_ru}")