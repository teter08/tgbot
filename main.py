import telebot
from telebot import types
import requests
import config
from geopy.geocoders import Nominatim
import gspread
from datetime import datetime

bot = telebot.TeleBot(config.token_tg_bot)
api_key = config.token_yandex_api
url = 'https://api.weather.yandex.ru/v2/forecast'
address = {'Ул. Проектируемая, 1, Большая Техническая 13, 15': [57.566729, 39.935673],
           'Ул. Светлая 1, 3': [57.568663, 39.931061],
           'Дядьковский проезд, 3': [57.587483, 39.899913],
           'Ул. Академика Колмогорова, 11, 14': [57.585587, 39.912253]}
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
smelltype = ['Нефтепродуктами', 'Химией', 'Канализацией']
currentweather = []
currentuser = 'currentuser'
mylocation = 'mylocation'


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Автоматически", request_location=True)
    button_choise = types.KeyboardButton(text="Вручную")
    keyboard.add(button_geo, button_choise)
    bot.send_message(message.chat.id, f"Для передачи погоды, выберите способ определения местоложения",
                     reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    global mylocation
    if message.location is not None:
        mylocation = (message.location.latitude, message.location.longitude)
    smell(message)


@bot.message_handler(content_types=['text'])
def func(message):
    global mylocation, currentweather
    if message.text == "Вручную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        [markup.add(types.KeyboardButton(x)) for x in address.keys()]
        bot.send_message(message.chat.id, text="Выберите ближайшее местоположение", reply_markup=markup)
    elif message.text in address:
        mylocation = ([address[message.text][0], address[message.text][1]])
        smell(message)
    elif message.text in smelltype:
        yandex_weather(*mylocation)
        google_write(message.text)
        bot.send_message(message.chat.id, f'Переданы следующие данные:' + '\n' + \
                         f'Запах: {message.text}' + '\n' + \
                         f'Температура воздуха: {currentweather[0]} °C' + '\n' + \
                         f'Скорость ветра: {currentweather[1]} м/с' + '\n' + \
                         f'Направление ветра: {currentweather[2]}' + '\n' + \
                         f'Давление: {currentweather[3]} мм рт. ст.' + '\n' + \
                         f'Влажность: {currentweather[4]} %' + '\n' + \
                         f'Описание погоды: {currentweather[5]}')
        start(message)
    else:
        bot.send_message(message.chat.id, text="Используйте кнопки")


def smell(message):
    global currentuser
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    [markup.add(types.KeyboardButton(x)) for x in smelltype]
    bot.send_message(message.chat.id, text="Чем пахнет?", reply_markup=markup)
    currentuser = f'{message.from_user.first_name}, {message.from_user.username}'


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
    global mylocation, currentweather
    geolocator = Nominatim(user_agent="my_geocoder")
    mylocation = geolocator.reverse((latitude, longitude), language="ru")
    currentweather = [data["fact"]["temp"], data["fact"]["wind_speed"], wind_dir[data["fact"]["wind_dir"]],
                      data["fact"]["pressure_mm"], data["fact"]["humidity"], condition[data["fact"]["condition"]]]
    return f'Температура воздуха: {data["fact"]["temp"]} °C' + '\n' + \
        f'Ощущается как: {data["fact"]["feels_like"]} °C' + '\n' + \
        f'Скорость ветра: {data["fact"]["wind_speed"]} м/с' + '\n' + \
        f'Направление ветра: {wind_dir[data["fact"]["wind_dir"]]}' + '\n' + \
        f'Давление: {data["fact"]["pressure_mm"]} мм рт. ст.' + '\n' + \
        f'Влажность: {data["fact"]["humidity"]} %' + '\n' + \
        f'Описание погоды: {condition[data["fact"]["condition"]]}'


def google_write(mysmell) -> None:
    global currentuser, currentweather
    # Указываем путь к JSON
    gc = gspread.service_account(filename='credentials.json')
    # Открываем таблицу для записи
    sh = gc.open("air_quality_measurement")
    nextcol = len(sh.sheet1.col_values(2)) + 1
    sh.sheet1.update(values=[[int(sh.sheet1.cell(nextcol - 1, 1).value) + 1,
                              datetime.now().strftime('%H:%M:%S'),
                              datetime.now().strftime('%d.%m.%Y'),
                              mylocation.address.split(',')[1] + ' ' + mylocation.address.split(',')[0],
                              currentweather[0], currentweather[1], currentweather[2], currentweather[3],
                              currentweather[4], currentweather[5],
                              currentuser,
                              mysmell]], range_name=f'A{nextcol}:L{nextcol}')


bot.polling(none_stop=True)
