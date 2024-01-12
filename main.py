import telebot;
from telebot import types
import requests
import config

bot = telebot.TeleBot(config.token_tg_bot)
api_key = config.token_yandex_api
url = 'https://api.weather.yandex.ru/v2/forecast'
address = ['Ул. Проектируемая, 1', 'Ул. Светлая, 3 к. 2', 'Пр. Фрунзе, 73', 'Ул. Академика Колмогорова, 11']
wind_dir = {'nw': 'северо-западное',
            'n': 'северное',
            'ne': 'северо-восточное',
            'e': 'восточное',
            'se': 'юго-восточное',
            's': 'южное',
            'sw': 'юго-западное',
            'w': 'западное',
            'c': 'штиль'}
condition = {
    'clear': 'ясно',
    'partly-cloudy': 'малооблачно',
    'cloudy': 'облачно с прояснениями',
    'overcast': 'пасмурно',
    'light-rain': 'небольшой дождь',
    'rain': 'дождь',
    'heavy-rain': 'сильный дождь',
    'showers': 'ливень',
    'wet-snow': 'дождь со снегом',
    'light-snow': 'небольшой снег',
    'snow': 'снег',
    'snow-showers': 'снегопад',
    'hail': 'град',
    'thunderstorm': 'гроза',
    'thunderstorm-with-rain': 'дождь с грозой',
    'thunderstorm-with-hail': 'гроза с градом'}


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    button_geo = types.KeyboardButton(text="Автоматически", request_location=True)
    button_choise = types.KeyboardButton(text="Вручную")
    keyboard.add(button_geo)
    keyboard.add(button_choise)
    bot.send_message(message.chat.id, f"Для передачи погоды, выбери способ определения местоложения",
                     reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        bot.send_message(message.chat.id,
                         yandex_weather(message.location.latitude, message.location.longitude))
        start(message)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Вручную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        [markup.add(types.KeyboardButton(x)) for x in address]
        bot.send_message(message.chat.id, text="Выберите ближайшее местоположение", reply_markup=markup)
    elif message.text in address:
        bot.send_message(message.chat.id, yandex_weather(57.566729, 39.935673))
        start(message)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


def yandex_weather(latitude, longitude):
    params = {
        'lat': latitude,
        'lon': longitude,
        'lang': 'ru_RU',  # язык ответа
        'limit': 1,  # срок прогноза в днях
        'hours': False,  # наличие почасового прогноза
        'extra': False  # подробный прогноз осадков
    }
    yandex_req = requests.get(url, params=params, headers={'X-Yandex-API-Key': api_key})
    # Проверяем статус ответа
    if yandex_req.status_code == 200:
        # Преобразуем ответ в JSON формат
        data = yandex_req.json()
    else:
        # Выводим код ошибки
        print(f'Ошибка: {yandex_req.status_code}')
    return f'Температура воздуха: {data["fact"]["temp"]} °C' + '\n' + \
           f'Ощущается как: {data["fact"]["feels_like"]} °C' + '\n' + \
           f'Скорость ветра: {data["fact"]["wind_speed"]} м/с' + '\n' + \
           f'Направление ветра: {wind_dir[data["fact"]["wind_dir"]]}' + '\n' + \
           f'Давление: {data["fact"]["pressure_mm"]} мм рт. ст.' + '\n' + \
           f'Влажность: {data["fact"]["humidity"]} %' + '\n' + \
           f'Погодное описание: {condition[data["fact"]["condition"]]}'


bot.polling(none_stop=True)
