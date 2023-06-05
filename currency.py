from requests import get

async def currency_answer(message):
    # разбиваем сообщение на необходимые составляющие внутри
    # списка
    input_ = message.text.upper().split()
    if not validate_items(input_):
        await mistake_answer(message, 1)
    else:
        # делаем запрос для получения котировок
        url = f"https://open.er-api.com/v6/latest/{input_[0]}"
        data = get(url).json()
        if data["result"] != "success":
            await mistake_answer(message, 2)
        else:
            # получаем стоимость нужной валюты относительно нашей
            exchange_rates = data["rates"]
            try:
                exchange_rate = float(exchange_rates[input_[1]]) * \
                                float(input_[2])
                await message.reply(
                    f"{input_[2]} {input_[0]} = "
                    f"{round(exchange_rate, 2)}"
                    f" {input_[1]}"
                )
            except KeyError:
                await mistake_answer(message, 2)


# проверка введенных данных
def validate_items(text):
    if len(text) != 3:
        return False
    else:
        if text[0].isalpha() and text[1].isalpha() and text[2].isdigit():
            return True
        else:
            return False


# ответ в формате обработки ошибки
async def mistake_answer(message, i):
    if i == 1:
        await message.reply("Проверьте правильность написания с "
                            "шаблоном\n"
                            "Пример: USD RUB 100")
    elif i == 2:
        await message.reply("Проверьте правильность написания валют")




