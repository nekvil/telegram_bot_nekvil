import logging
import os
import telebot
from tradingview_ta import TA_Handler, Interval
import rbc_crypto
import cryptonews
import investing
import datetime
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from telebot import types

dump_data = {
    "telebot_key": {
        "name": ""
    },
    "developer_telegram_url": {
        "name": ""
    },
    "coinmarketcap_url": {
        "name": ""
    },
    "CoinMarketCapAPI": {
        "name": ""
    }
}

if not os.path.exists('data.json'):
    with open('data.json', 'w+', encoding='utf-8') as f:
        json.dump(dump_data, f, ensure_ascii=False, indent=4)

with open("data.json", "r") as read_file:
    load_data = json.load(read_file)

bot = telebot.TeleBot(load_data["telebot_key"]["name"])


@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_one = types.KeyboardButton('/one')
    btn_news = types.KeyboardButton('/news')
    btn_top = types.KeyboardButton('/top')
    keyboard_markup.add(btn_help, btn_one, btn_news, btn_top)
    bot.send_message(message.chat.id,
                     'Добрый день! Я могу показать вам топ криптовалют, отдельные криптоактивы и последние новости.\n\n'
                     + 'Чтобы посмотреть текущий топ, используйте /top.\n'
                     + 'Чтобы посмотреть новости, используйте /news.\n'
                     + 'Чтобы узнать подробнее об одном криптоактиве, используйте /one.\n'
                     + 'Чтобы посмотреть все команды, используй /help.',
                     reply_markup=keyboard_markup)


@bot.message_handler(commands=['one'])
def one_command(message):
    send = bot.send_message(message.chat.id, 'Введите сокращенное название криптоактива (например, BTC)')
    bot.register_next_step_handler(send, email_create_request_data)


def email_create_request_data(message):
    bot.send_chat_action(message.chat.id, 'typing')
    cmc = CoinMarketCapAPI(load_data["CoinMarketCapAPI"]["name"])
    increase = "↗️"
    decrease = "↘️"
    cryptocurrency_name = message.text.upper()
    _str = ""
    try:
        r = cmc.cryptocurrency_quotes_latest(symbol=cryptocurrency_name)

        name = r.data[cryptocurrency_name]["name"]
        price_now = r.data[cryptocurrency_name]["quote"]["USD"]["price"]
        percent_change_1h = r.data[cryptocurrency_name]["quote"]["USD"]["percent_change_1h"]
        percent_change_24h = r.data[cryptocurrency_name]["quote"]["USD"]["percent_change_24h"]
        percent_change_7d = r.data[cryptocurrency_name]["quote"]["USD"]["percent_change_7d"]
        max_supply = r.data[cryptocurrency_name]["max_supply"]
        circulating_supply = r.data[cryptocurrency_name]["circulating_supply"]
        market_cap = r.data[cryptocurrency_name]["quote"]["USD"]["market_cap"]

        if "-" in str(percent_change_1h):
            status_1 = decrease
        else:
            status_1 = increase
        if "-" in str(percent_change_24h):
            status_2 = decrease
        else:
            status_2 = increase
        if "-" in str(percent_change_7d):
            status_3 = decrease
        else:
            status_3 = increase

        _str += "\n" + name + " (" + cryptocurrency_name + ") " + "\n\n" + datetime.datetime.today().strftime(
            "%Y-%m-%d %H:%M:%S") + "\n"

        _str += "\n" + "Цена: " + str('{0:,}'.format(round(price_now, 2)).replace(',', ' ')) + " $" + "\n"
        _str += "Капитализация: " + str('{0:,}'.format(round(market_cap)).replace(',', ' ')) + " $" + "\n"
        _str += "1h %: " + str(round(percent_change_1h, 2)) + " % " + status_1 + "\n"
        _str += "24h %: " + str(round(percent_change_24h, 2)) + " % " + status_2 + "\n"
        _str += "7d %: " + str(round(percent_change_7d, 2)) + " % " + status_3 + "\n"

        if max_supply is None:
            _str += "Максимальное предложение: неограничено" + "\n"
        else:
            _str += "Максимальное предложение: " + str('{0:,}'.format(round(max_supply)).replace(',', ' ')) + "\n"
        _str += "Циркулирующее предложение: " + str('{0:,}'.format(round(circulating_supply)).replace(',', ' ')) + "\n"

        fiat = "USDT"
        ico = {"STRONG_BUY": "💚", "BUY": "🟢", "SELL": "🔴", "STRONG_SELL": "🔴🔴🔴", "NEUTRAL": "⚪️"}
        day = Interval.INTERVAL_1_DAY
        week = Interval.INTERVAL_1_WEEK
        month = Interval.INTERVAL_1_MONTH
        # try:
        coin_day = TA_Handler(
            symbol=cryptocurrency_name + fiat,
            screener="CRYPTO",
            exchange="BINANCE",
            interval=day
        )

        coin_week = TA_Handler(
            symbol=cryptocurrency_name + fiat,
            screener="CRYPTO",
            exchange="BINANCE",
            interval=week
        )

        coin_month = TA_Handler(
            symbol=cryptocurrency_name + fiat,
            screener="CRYPTO",
            exchange="BINANCE",
            interval=month
        )

        _str += "\nАнализ представлен сайтом ru.TradingView.com\n"

        try:
            if coin_day.get_analysis().summary.items():
                _str += "\nДневной теханализ:\n"
                for key, value in coin_day.get_analysis().summary.items():
                    _str = rec_str(key, value, _str, ico)
        except Exception as e:
            logging.exception(e)
            _str += '\nНедельный теханализ ' + cryptocurrency_name + ' приболел!🤒\n'

        try:
            if coin_week.get_analysis().summary.items():
                _str += "\nНедельный теханализ:\n"
                for key, value in coin_week.get_analysis().summary.items():
                    _str = rec_str(key, value, _str, ico)
        except Exception as e:
            logging.exception(e)
            _str += '\nНедельный теханализ ' + cryptocurrency_name + ' приболел!🤒\n'

        try:
            if coin_month.get_analysis().summary.items():
                _str += "\nМесячный теханализ:\n"
                for key, value in coin_month.get_analysis().summary.items():
                    _str = rec_str(key, value, _str, ico)
        except Exception as e:
            logging.exception(e)
            _str += '\nМесячный теханализ ' + cryptocurrency_name + ' приболел!🤒\n'
            # bot.send_sticker(message.chat.id,"CAACAgIAAxkBAAECXspguDOMXJ0EN7MhCw98eNJRUcMIUgACFQYAApb6EgXzIfHp6frT9x8E")

        bot.send_message(message.chat.id, _str)
    except CoinMarketCapAPIError as e:
        logging.exception(e)
        bot.send_message(message.chat.id, 'Такого криптоактива не существует!👇')
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAECXspguDOMXJ0EN7MhCw98eNJRUcMIUgACFQYAApb6EgXzIfHp6frT9x8E")


def rec_str(key, value, _str, ico):
    if key == "RECOMMENDATION":
        _str += str(key) + ": " + str(value) + ico[value] + "\n"
    else:
        _str += str(key) + ": " + str(value) + "\n"
    return _str


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Сообщение разработчику', url=load_data["developer_telegram_url"]["name"])
    )
    bot.send_message(
        message.chat.id,
        'Добрый день! Я могу показать вам топ криптовалют, отдельные криптоактивы и последние новости.\n\n' +
        'Чтобы посмотреть текущий топ, используйте /top.\n' +
        'Чтобы посмотреть новости, используйте /news.\n' +
        'Чтобы посмотреть подробнее об одном криптоактиве, используйте /one.\n' +
        'Чтобы посмотреть все команды, используй /help.\n\n' +
        'Чтобы сообщить об ошибке или предложить идею, напишите личное сообщение разработчику. '
        '\nСпасибо, что пользуетесь нашим ботом!',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('get-'))
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_top_callback(query)


def get_top_callback(query):
    bot.answer_callback_query(query.id)
    send_exchange_result(query.message, query.data[4:])


def send_exchange_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    url = load_data["coinmarketcap_url"]["name"]
    parameters = {
        'start': '1',
        'limit': str(ex_code),
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': load_data["CoinMarketCapAPI"]["name"],
    }

    session = Session()
    session.headers.update(headers)
    ls_data = {}

    _str = f'Топ {str(ex_code)} криптовалют по капитализации на ' + \
           datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        for i in data["data"]:
            ls_data[i['symbol']] = [i['quote']['USD']]
        increase = "↗️"
        decrease = "↘️"

        for key, value in ls_data.items():
            _str += "\n" + "№" + str(list(ls_data.keys()).index(key) + 1) + " " + str(key) + "\n"
            for i in value:

                if "-" in str(i['percent_change_1h']):
                    status_1 = decrease
                else:
                    status_1 = increase
                if "-" in str(i['percent_change_24h']):
                    status_2 = decrease
                else:
                    status_2 = increase
                if "-" in str(i['percent_change_7d']):
                    status_3 = decrease
                else:
                    status_3 = increase

                _str += "\n" + "Цена: " + str('{0:,}'.format(round(i['price'], 2)).replace(',', ' ')) + " $" + "\n"
                _str += "Капитализация: " + str(
                    '{0:,}'.format(round(i['market_cap'], 2)).replace(',', ' ')) + " $" + "\n"
                _str += "1h %: " + str(round(i['percent_change_1h'], 2)) + " % " + status_1 + "\n"
                _str += "24h %: " + str(round(i['percent_change_24h'], 2)) + " % " + status_2 + "\n"
                _str += "7d %: " + str(round(i['percent_change_7d'], 2)) + " % " + status_3 + "\n"

        if len(_str) > 4096:
            for x in range(0, len(_str), 4096):
                bot.send_message(message.chat.id, '{}'.format(_str[x:x + 4096]))
                print(x)
        else:
            bot.send_message(message.chat.id, '{}'.format(_str))

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        bot.send_message(message.chat.id, e)
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAECU2dgqFj4fMuP60iFOpEZ-xPXyCrXhgAC-wUAApb6EgWXW-3leOFoFh8E")


@bot.message_handler(commands=['top'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('ТОП 10', callback_data='get-10')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('ТОП 50', callback_data='get-50'),
        telebot.types.InlineKeyboardButton('ТОП 100', callback_data='get-100')
    )

    bot.send_message(
        message.chat.id,
        'Выберите размер топа:',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('news-'))
def iq_callback(query):
    data = query.data
    if data.startswith('news-'):
        get_news_callback(query)


def get_news_callback(query):
    bot.answer_callback_query(query.id)
    send_news_result(query.message, query.data[5:])


def send_news_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    if ex_code == 'rbc':
        news_data = rbc_crypto.main()
        _str = "Новости с сайта rbc.ru" + "\n"
        for key, value in news_data.items():
            _str += "\n" + "№" + str(list(news_data.keys()).index(key) + 1) + "\n"
            _str += value['link'] + "\n" + value['title'] + "\n" + value['category'] + "\n" + "\n" + value[
                'date'] + "\n" + value['overview'] + "\n"
        bot.send_message(message.chat.id, _str, disable_web_page_preview=True)

    elif ex_code == 'investing':
        news_data = investing.main()
        _str = "Новости с сайта investing.com" + "\n"
        for key, value in news_data.items():
            _str += "\n" + "№" + str(list(news_data.keys()).index(key) + 1) + "\n"
            _str += value['link'] + "\n" + value['title'] + "\n" + "\n" + value['date'] + "\n"
        bot.send_message(message.chat.id, _str, disable_web_page_preview=True)

    elif ex_code == 'cryptonews':
        news_data = cryptonews.main()
        _str = "Новости с сайта cryptonews.net/ru" + "\n"
        for key, value in news_data.items():
            _str += "\n" + "№" + str(list(news_data.keys()).index(key) + 1) + "\n"
            _str += value['link'] + "\n" + value['title'] + "\n" + value['category'] + "\n" + "\n" + value[
                'date'] + "\n"
        bot.send_message(message.chat.id, _str, disable_web_page_preview=True)


@bot.message_handler(commands=['news'])
def news_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('rbc.ru', callback_data='news-rbc')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('cryptonews.net/ru', callback_data='news-cryptonews'),
        telebot.types.InlineKeyboardButton('investing.com', callback_data='news-investing')
    )
    bot.send_message(
        message.chat.id,
        'Выберите сайт:',
        reply_markup=keyboard
    )


@bot.message_handler(content_types=['text'])
def get_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, '[Пока](https://www.youtube.com/watch?v=dQw4w9WgXcQ)',
                         parse_mode='MarkdownV2',
                         disable_web_page_preview=True)
        bot.send_sticker(message.chat.id, open("doge.webp", "rb"))
    else:
        bot.send_message(message.chat.id, "WTFCK?🤬 /help", disable_web_page_preview=True)
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAECU2lgqFuz_pYlcFeLG3pweYv-CHB-NQACBQYAApb6EgW6M2c2KIW1YR8E")


bot.polling(none_stop=True, interval=0)
