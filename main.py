import telebot;
from telebot import types
import json
import requests as req

import config

bot = telebot.TeleBot(config.token_tg_bot)
address = ['Ул. Проектируемая, 1', 'Ул. Светлая, 3 к. 2', 'Пр. Фрунзе, 73', 'Ул. Академика Колмогорова, 11']


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
        print(message.location)
        print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
        bot.send_message(message.chat.id, text=f'{message.location.latitude}, {message.location.longitude}')
        start(message)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Вручную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        [markup.add(types.KeyboardButton(x)) for x in address]
        bot.send_message(message.chat.id, text="Выберите ближайшее местоположение", reply_markup=markup)
    elif message.text in address:
        bot.send_message(message.chat.id, message.text)
        # 57.566729, 39.935673
        bot.send_message(message.chat.id, yandex_weather(57.566729, 39.935673, config.token_yandex_api))
        start(message)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


def yandex_weather(latitude, longitude, token_yandex: str):
    url_yandex = 'https://api.weather.yandex.ru/v2/informers?lat=55.75396&lon=37.620393'
    yandex_req = req.get(url=url_yandex, headers={'X-Yandex-API-Key': token_yandex})
    return yandex_req.text
    # conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
    #               'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
    #               'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
    #               'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
    #               'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
    #               'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
    #               'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
    #               }
    # wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
    #             'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}
    #
    # yandex_json = json.loads(yandex_req.text)
    # yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    # yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
    # for parts in yandex_json['forecast']['parts']:
    #     parts['condition'] = conditions[parts['condition']]
    #     parts['wind_dir'] = wind_dir[parts['wind_dir']]
    #
    # pogoda = dict()
    # params = ['condition', 'wind_dir', 'pressure_mm', 'humidity']
    # for parts in yandex_json['forecast']['parts']:
    #     pogoda[parts['part_name']] = dict()
    #     pogoda[parts['part_name']]['temp'] = parts['temp_avg']
    #     for param in params:
    #         pogoda[parts['part_name']][param] = parts[param]
    #
    # pogoda['fact'] = dict()
    # pogoda['fact']['temp'] = yandex_json['fact']['temp']
    # for param in params:
    #     pogoda['fact'][param] = yandex_json['fact'][param]
    #
    # pogoda['link'] = yandex_json['info']['url']
    # return pogoda


bot.polling(none_stop=True)
