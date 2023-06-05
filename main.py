from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json
import weather
import currency
import other_func
import pictures
import os

storage = MemoryStorage()  # для обработки запросов

TOKEN = os.environ.get('TOKEN')  # API бота

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
bot_id = bot.id  # id бота для работы с опросами в группах

# Считываем информацию из файла
chats = other_func.load_chats_from_json()
# класс нужен для обработки запросов пользователей на получение
# прогноза погоды, конвертации валют и создания опросов
class Form(StatesGroup):
    weather = State()
    currency = State()
    poll_chat = State()
    poll_quest = State()
    poll_answers = State()
    poll_valid = State()


# функция старт для начала работы
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет. Нажми на /menu.")


# функция меню для вывода клавиатуры с запросами из тз
@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    # Клавиатура не исчезнет пока не удалят последнее сообщение
    # пользователя /menu
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    markup.add(types.KeyboardButton('Валюта'))
    markup.add(types.KeyboardButton('Погода'))
    markup.add(types.KeyboardButton('Случайная картинка милых '
                                    'животных'))
    if message.chat.id > 0:  # Опрос можно создать только в лс с ботом
        markup.add(types.KeyboardButton('Создать опрос'))
    await message.answer("Выберите пункт меню", reply_markup=markup)


# основной обработчик событий, который реагирует на клавиатуру
@dp.message_handler(content_types=['text'])
async def main(message: types.Message, state: FSMContext):
    global chats
    if message.text == "Валюта":
        await Form.currency.set()
        await message.answer("Введите валюту, из которой хотите "
                             "перевести, затем вылюту, в которую "
                             "хотите перевести и "
                             "исходное количетво средств.\n"
                             "Пример: USD RUB 100\n"
                             "Если передумал нажми /cancel")
    elif message.text == "Погода":
        await Form.weather.set()
        await message.answer("Введите город.\n"
                             "Если передумал нажми /cancel")
    elif message.text == "Случайная картинка милых животных":
        # отправляет случайную картинку из папки
        await pictures.fetch(bot, message)
    elif message.text == "Создать опрос":
        # данный алгоритм нужен, чтобы вывести в сообщении
        # пользователю названия всех чатов, в которых состоит бот
        send_chats = other_func.chat_titles(chats)
        if send_chats:
            await message.answer("Введите название чата:\n"
                                 f"{send_chats}\n"
                                 "Если передумал нажми /cancel")
            await state.set_state(Form.poll_chat.state)
        else:
            await message.answer("Бот не состоит ни в одном чате")

    else:
        await message.answer("Выберите пункт из меню")


# обработчик отмены действий если пользователь передумал
# запрашивать погоду, конвертировать валюту или создавать опрос
@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled.')


# функция конвертации валют получающая на вход соответствующее
# сообщение пользователя
@dp.message_handler(state=Form.currency)
async def currency_answer(message: types.Message, state: FSMContext):
    await state.finish()
    await currency.currency_answer(message)


# функция отправки прогноза погоды получающая на вход соответствующее
# сообщение пользователя
@dp.message_handler(state=Form.weather)
async def weather_answer(message: types.Message, state: FSMContext):
    await state.finish()
    await weather.weather_response(message)

# запрашиваем вопрос и сохраняем чат
@dp.message_handler(state=Form.poll_chat)
async def poll_chat(
        message: types.Message,
        state: FSMContext
):
    send_chats = other_func.chat_titles(chats)
    if message.text not in send_chats:
        await message.answer("Пожалуйста, выберите доступный чат.\n"
                             "Если передумал нажми /cancel")
        return
    # сохранение выбранного чата
    await state.update_data(choosen_chat=message.text)
    await message.answer("Введите ваш вопрос.\n"
                         "Пример: Выбери число \n"
                         "Если передумал нажми /cancel")
    await state.set_state(Form.poll_quest.state)


# запрашиваем ответы на вопрос и сохраняем вопрос
@dp.message_handler(state=Form.poll_quest)
async def poll_quest(
        message: types.Message,
        state: FSMContext
):
    # Сохранение текста вопроса
    await state.update_data(poll_quest=message.text)
    await message.answer("Введите варианты ответов. Их должно быть "
                         "минимум два. Каждый вариант ответа "
                         "вводится с новой строки\n"
                         "Пример для вопроса (Какого цвета "
                         "деревья?)\n"
                         "Зеленые\n"
                         "Синие\n"
                         "Черные\n"
                         "Если передумал нажми /cancel")
    await state.set_state(Form.poll_answers.state)

# запрашиваем валидацию опроса и сохраняем ответы
@dp.message_handler(state=Form.poll_answers)
async def poll_answers(
        message: types.Message,
        state: FSMContext
):
    # проверка введенных данных
    if len(message.text.split("\n")) < 2:
        await message.reply("Вариантов ответа должно быть минимум "
                            "два\nЕсли передумал нажми /cancel")
        return
    # Сохранение вариантов ответа
    await state.update_data(inputed_poll_answers=message.text)
    user_data = await state.get_data()
    await message.answer("Проверьте правильность данных\n"
                         f"{user_data['choosen_chat']}\n"
                         f"{user_data['poll_quest']}\n"
                         f"{message.text}")
    await message.answer("Если все верно введите да.\n"
                         "Если есть ошибки нажмите /cancel, чтобы "
                         "ввести все сначала")
    await state.set_state(Form.poll_valid.state)


# Отправляем опрос в чат
@dp.message_handler(state=Form.poll_valid)
async def create_poll(message: types.Message, state: FSMContext):
    if message.text.strip() != 'да':
        await message.answer("Если все верно введите да.\n"
                             "Если есть ошибки нажмите /cancel, "
                             "чтобы ввести все сначала")
        return
    else:
        final_state = await state.get_data()
        options = final_state['inputed_poll_answers'].split('\n')
        # получение id чата
        chat_id = 0
        for each in chats:
            if each['title'] == final_state['choosen_chat']:
                chat_id = each['id']
                break
        # Отправка опроса в выбранный чат
        await bot.send_poll(
                    chat_id=chat_id,
                    question=f"{final_state['poll_quest']}",
                    options=options,
                    correct_option_id=1,
        )
        await state.finish()


# обработчик добавления бота в чат
@dp.message_handler(
    content_types=[
        types.ContentType.NEW_CHAT_MEMBERS
    ]
)
async def save_chat(message: types.Message):
    global chats
    data = json.loads(message.as_json())
    if data['new_chat_participant']['id'] == bot_id:
        chats.append(data['chat'])


# обработчик удаления бота из чата
@dp.message_handler(
    content_types=[
        types.ContentType.LEFT_CHAT_MEMBER,
    ]
)
async def del_chat(message: types.Message):
    global chats
    data = json.loads(message.as_json())
    if data['left_chat_participant']['id'] == bot_id:
        chats.remove(data["chat"])

if __name__ == '__main__':
    # Создаем обработчик ошибок для беспрерывной работы бота
    try:
        executor.start_polling(dp)
    except KeyboardInterrupt:
        print("Выключено до полной подгрузки библиотек")
    except TimeoutError:
        print("Проверьте подключение к интернету")
    finally:  # после выключения бота записываем все чаты в файл
        with open("chats.json", 'w') as ch:
            json.dump(chats, ch)
