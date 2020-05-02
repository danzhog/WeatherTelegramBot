import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
from settings import token


bot = telebot.TeleBot(token)


def get_countries(country1):
    resp = requests.get("https://yandex.by/pogoda/region?via=brd")
    html = resp.text

    soup = BeautifulSoup(html, 'lxml')
    tags_countries = soup.find_all('a', 'link place-list__item-name i-bem')

    countries = {}
    for tag in tags_countries:

        url = re.findall(r'href=\"(/pogoda/region/\d+[?]via=reg)\"', str(tag))
        href = f'https://yandex.by{"".join(url)}'

        country = str.lower(tag.text)
        if country:
            countries[country] = href
    return countries.get(country1)


def get_cities(country_url, city1):
    resp = requests.get(country_url)
    html = resp.text

    soup = BeautifulSoup(html, 'lxml')
    tags_cities = soup('a', 'link place-list__item-name i-bem')

    cities = {}
    for tag in tags_cities:

        url = re.findall(r'href=\"(/pogoda/\D+\?via=reg)\"', str(tag))
        href = f'https://yandex.by{"".join(url)}'

        city = str.lower(tag.text)
        if city:
            cities[city] = href
    return cities.get(city1)


def get_weather(city_url):
    resp = requests.get(city_url)
    html = resp.text

    soup = BeautifulSoup(html, 'lxml')

    temp = soup.find_all('span', 'temp__value')
    current_temp = temp[1].text
    feels_like = temp[2].text
    clouds = soup.find('div', 'link__condition day-anchor i-bem').text
    rainfall = soup.find('p', 'maps-widget-fact__title').text

    return current_temp, feels_like, clouds, rainfall


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start')
    bot.register_next_step_handler(message, handle_country)
    bot.send_message(message.chat.id, "Введи название страны: ")


@bot.message_handler()
def handle_country(message):
    print(message)
    global country_url
    country_url = get_countries(str.lower(message.text))
    # bot.send_message(message.chat.id, text=f"ссылка {country_url}")

    if country_url:
        bot.send_message(message.chat.id, text="Введи название города: ")
        bot.register_next_step_handler(message, handle_city)
        # handle_city(country_url, message)
    else:
        bot.send_message(message.chat.id, text="Проверь правильность написания страны")
    return country_url


@bot.message_handler()
def handle_city(message):
    print(message)
    global city_url
    city_url = get_cities(country_url, str.lower(message.text))
    # bot.send_message(message.chat.id, text=f"ссылка города{city_url}")
    if city_url:
        handle_weather(message)
        # handle_weather(city_url)
    else:
        bot.send_message(message.chat.id, text="Проверь правильность написания города")


@bot.message_handler()
def handle_weather(message):
    global weather
    print(message)
    weather = get_weather(city_url)
    bot.send_message(message.chat.id, text=f"Текущая температура: {weather[0]} °C\n"
                                           f"Ощущается как: {weather[1]} °C\n"
                                           f"{weather[2]}\n"
                                           f"{weather[3]}")
    send_pic(message)


@bot.message_handler()
def send_pic(message):
    bot.send_message(message.chat.id, text="Вариант как одеться:")

    sun_5_5 = ['CAACAgIAAxkBAAJbkl6tWlqP3dBUBqeJebqATCuqGUswAAKOAwAC0_GkC_PTMhqVEIaVGQQ',
               'CAACAgIAAxkBAAJblF6tWmB9Dhc39wq76dGrsVps28f-AAKPAwAC0_GkC1ULNMp-XrubGQQ',
               'CAACAgIAAxkBAAJbll6tWmM80H_seXSQ5MjpVn14NKmmAAKQAwAC0_GkC0sL4zcDMU7wGQQ',
               'CAACAgIAAxkBAAJbmF6tWmaNnbt4IHSDa3QJH7jA6cpnAAKRAwAC0_GkC804rRUcZ67OGQQ',
               ]

    rain_5_5 = ['CAACAgIAAxkBAAJbml6tWqwVLeQtLRHLHdI_P5p86aORAAKSAwAC0_GkC_L1onaO5_m_GQQ',]

    sun_6_9 = ['CAACAgIAAxkBAAJbnF6tWtTx5EZ50wPI0NU54zudfv4bAAKTAwAC0_GkC9Ggypcc6CvbGQQ',
               'CAACAgIAAxkBAAJbnl6tWuD3DLoMMnWBYrBVQbca5rPIAAKUAwAC0_GkC3wYi_hQ-Lg_GQQ',
               'CAACAgIAAxkBAAJboF6tWuLcGq99xHfmESjZoYvobJpYAAKVAwAC0_GkC8ROEdFX2XLvGQQ',
               'CAACAgIAAxkBAAJbol6tWuVEg34vlAbr1m3vfl1DDhYrAAKWAwAC0_GkC9brW2U8UkQQGQQ',
               ]

    rain_6_9 = ['CAACAgIAAxkBAAJbpF6tWxQI6tPYAAGzSm1OC8Jbv_ykGQAClwMAAtPxpAsPqrB4FnGD0BkE',
                'CAACAgIAAxkBAAJbpl6tWxeqCm4qaWvj6CGC5iBxyiW8AAKYAwAC0_GkCwgHnUNfEFA_GQQ',
                ]

    sun_10_13 = ['CAACAgIAAxkBAAJbqF6tW4a6UepyavQDxO8aPsq8p47GAAKZAwAC0_GkC9bLB5oLvErxGQQ',
                 'CAACAgIAAxkBAAJbql6tW4kYO-R7oTzzvNRMapZkbmmNAAKaAwAC0_GkC7LFHxmGgufGGQQ',
                 'CAACAgIAAxkBAAJbrF6tW4wYMDW0aUuA1Ruhe_EQA0xVAAKbAwAC0_GkCwxBLGLWQ3UgGQQ',
                 'CAACAgIAAxkBAAJbrl6tW47yLq45iJkrg_T0aOyZoKsCAAKcAwAC0_GkC5fVnDanOq-gGQQ',
                 ]

    rain_10_13 = ['CAACAgIAAxkBAAJbsF6tW8CWaRTR2ZlGfKM-27hIVUL4AAKdAwAC0_GkC3KKIapZag_7GQQ',
                  'CAACAgIAAxkBAAJbsl6tW8J-NgkauyW8-pdeeKf5vvWjAAKeAwAC0_GkCzW09RYuCwXtGQQ',
                  ]

    sun_14_16 = ['CAACAgIAAxkBAAJbtF6tXBMjDjRdEZkxf60K2gp68oiLAAKfAwAC0_GkCyrCDPacKaRFGQQ',
                 'CAACAgIAAxkBAAJbtl6tXBa_EmPpPoKzd4TNpCBuTM9-AAKgAwAC0_GkC7pyNKmLJAjRGQQ',
                 'CAACAgIAAxkBAAJbuF6tXBmj-fHjQ3wrmQd9Q5FQP1muAAKhAwAC0_GkC7wfIwI05qokGQQ',
                 'CAACAgIAAxkBAAJbu16tXBu36PokxiNQfUdc42BBtzcHAAKiAwAC0_GkC9WDKf-90EvYGQQ',
                ]

    rain_14_16 = ['CAACAgIAAxkBAAJbwl6tXFTVwJrJHN_nKjflboyR_9M3AAKjAwAC0_GkC4EgQUChwgTdGQQ',
                  'CAACAgIAAxkBAAJbxF6tXFY-gT_wzthwILVgs4ULhbhyAAKkAwAC0_GkC_tFL5-Hq-z2GQQ',
                  ]

    sun_17_20 = ['CAACAgIAAxkBAAJbxl6tXISU5-U260U_OPZp26NA14cPAAKlAwAC0_GkC2H0Z-q5cUCfGQQ',
                 'CAACAgIAAxkBAAJbyF6tXIZOac-3yP8_7Wnj6KVTg2keAAKmAwAC0_GkCy2pbpyH2KTCGQQ',
                 'CAACAgIAAxkBAAJbyl6tXImAkMJCYVeBE9MJY_nC1I9eAAKnAwAC0_GkC5RmygGjtfZfGQQ',
                 ]

    rain_17_20 = ['CAACAgIAAxkBAAJbzF6tXM0w7VVXrNBmws96_3C_khTFAAKoAwAC0_GkC3nnU5FYKSb1GQQ',
                  'CAACAgIAAxkBAAJbzl6tXNDAVrxaLUU74DFyZGvNX_VNAAKpAwAC0_GkC0Xk0iR13OS_GQQ',
                  ]

    sun_21_35 = ['CAACAgIAAxkBAAJb0F6tXPfnPg9yU7ZkK179epK_p4muAAKqAwAC0_GkC8r7nL1jvsIUGQQ',
                 'CAACAgIAAxkBAAJb0l6tXPnTQh3Z4HrxdUC8EfHL_-84AAKrAwAC0_GkC62abpmnEeKIGQQ',
                 'CAACAgIAAxkBAAJb1F6tXPu7rz-P6uKdDVvHIHxTRquNAAKsAwAC0_GkC5BPkZ1Db7ePGQQ',
                 'CAACAgIAAxkBAAJb1l6tXP4i-ZK7XB5pqYzPTYOtHevMAAKtAwAC0_GkC1iZqlD7QMv3GQQ',
                 ]

    rain_21_35 = ['CAACAgIAAxkBAAJb2F6tXT20JJSzAk7pa8udVK-_P_ovAAKuAwAC0_GkC_V5w0B7jqoWGQQ',
                  'CAACAgIAAxkBAAJb2l6tXT-0nQtAQIn5JLZ-0lemXpDfAAKvAwAC0_GkC6oiWSowyXJ1GQQ',
                  ]

    if int(weather[1]) in range(-5, 6):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_5_5))
            bot.send_message(message.chat.id,
                             text="На улице холодно и мокро, советую надеть теплую куртку с капюшоном и кофту.\n"
                                  "Не забудь про шапку!")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_5_5))
            bot.send_message(message.chat.id, text="На улице прохладно, советую надеть теплую куртку и кофту.\n"
                                                   "Не забудь про шапку!")

    if int(weather[1]) in range(6, 10):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_6_9))
            bot.send_message(message.chat.id, text="На улице прохладно и идет дождь, советую надеть куртку и свитшот.\n"
                                                   "Не забудь ЗОНТИК!")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_6_9))
            bot.send_message(message.chat.id, text="На улице прохладно, советую надеть куртку и свитшот")

    if int(weather[1]) in range(10, 14):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_10_13))
            bot.send_message(message.chat.id, text="На улице свежо и идет дождь, советую надеть легку куртку и гольф.\n"
                                                   "Не забудь ЗОНТИК!")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_10_13))
            bot.send_message(message.chat.id, text="На улице свежо, советую надеть легку куртку и гольф")

    if int(weather[1]) in range(14, 17):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_14_16))
            bot.send_message(message.chat.id,
                             text="На улице тепло и идет дождь, надевай худи и прихвати что-нибудь от дождя.\n")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_14_16))
            bot.send_message(message.chat.id,
                             text="На улице тепло, поэтому снимай куртку(если ты не мерзляк) и надевай худи\n")

    if int(weather[1]) in range(17, 21):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_17_20))
            bot.send_message(message.chat.id,
                             text="На улице почти жара и идет дождь, майка и легкая джинсовка будет идеально.\n"
                                  "Не забудь ЗОНТИК!")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_17_20))
            bot.send_message(message.chat.id,
                             text="На улице почти жара, надевай футболку и прихвати легкую накдидку.\n")

    if int(weather[1]) in range(21, 36):
        if 'дождь' or 'Дождь' in weather[3]:
            bot.send_sticker(message.chat.id, random.choice(rain_21_35))
            bot.send_message(message.chat.id, text="На улице жара и идет дождь, надевай майку и шорты.\n"
                                                   "и не забудь ЗОНТИК и головной убор!")
        else:
            bot.send_sticker(message.chat.id, random.choice(sun_21_35))
            bot.send_message(message.chat.id, text="На улице жара, надевай футболку, шорты и прихвати головной убор")


bot.polling()
