import telebot
import requests
from bs4 import BeautifulSoup
import re

token = '863427020:AAEdpD31x7DNvvnrTMxBoiGTI88o7cAbbjc'
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


bot.polling()
