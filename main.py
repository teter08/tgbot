import telebot;
from telebot import types
import json
import requests as req

import config

bot = telebot.TeleBot(config.token_tg_bot)
address = ['Ул. Проектируемая, 1', 'Ул. Светлая, 3 к. 2', 'Пр. Фрунзе, 73', 'Ул. Академика Колмогорова, 11']

import requests

# Задаем координаты населенного пункта
lat = 55.75396  # широта Москвы
lon = 37.620393  # долгота Москвы

# Задаем параметры запроса
params = {
    'lat': lat,
    'lon': lon,
    'lang': 'ru_RU',  # язык ответа
    'limit': 7,  # срок прогноза в днях
    'hours': True,  # наличие почасового прогноза
    'extra': False  # подробный прогноз осадков
}

# Задаем значение ключа API
api_key = config.token_yandex_api

# Задаем URL API
url = 'https://api.weather.yandex.ru/v2/forecast'

# Делаем запрос к API
response = requests.get(url, params=params, headers={'X-Yandex-API-Key': api_key})

# Проверяем статус ответа
if response.status_code == 200:
    # Преобразуем ответ в JSON формат
    data = response.json()
    # Выводим данные о текущей погоде
    print(f'Температура воздуха: {data["fact"]["temp"]} °C')
    print(f'Ощущается как: {data["fact"]["feels_like"]} °C')
    print(f'Скорость ветра: {data["fact"]["wind_speed"]} м/с')
    print(f'Давление: {data["fact"]["pressure_mm"]} мм рт. ст.')
    print(f'Влажность: {data["fact"]["humidity"]} %')
    print(f'Погодное описание: {data["fact"]["condition"]}')
else:
    # Выводим код ошибки
    print(f'Ошибка: {response.status_code}')

# @bot.message_handler(commands=["start"])
# def start(message):
#     keyboard = types.ReplyKeyboardMarkup()
#     button_geo = types.KeyboardButton(text="Автоматически", request_location=True)
#     button_choise = types.KeyboardButton(text="Вручную")
#     keyboard.add(button_geo)
#     keyboard.add(button_choise)
#     bot.send_message(message.chat.id, f"Для передачи погоды, выбери способ определения местоложения",
#                      reply_markup=keyboard)
#
#
# @bot.message_handler(content_types=["location"])
# def location(message):
#     if message.location is not None:
#         print(message.location)
#         print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
#         bot.send_message(message.chat.id, text=f'{message.location.latitude}, {message.location.longitude}')
#         start(message)
#
#
# @bot.message_handler(content_types=['text'])
# def func(message):
#     if message.text == "Вручную":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         [markup.add(types.KeyboardButton(x)) for x in address]
#         bot.send_message(message.chat.id, text="Выберите ближайшее местоположение", reply_markup=markup)
#     elif message.text in address:
#         bot.send_message(message.chat.id, message.text)
#         # 57.566729, 39.935673
#         bot.send_message(message.chat.id, yandex_weather(57.566729, 39.935673, config.token_yandex_api))
#         start(message)
#     else:
#         bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")
#
#
# def yandex_weather(latitude, longitude, token_yandex: str):
#     url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
#     yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
#
#     return yandex_req
#
#
# bot.polling(none_stop=True)
