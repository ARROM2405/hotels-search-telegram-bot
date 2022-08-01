""""The interaction with the bot always starts with a /start command.
Otherwise it will not react as there will be no information on a chat in the requests_dict"""

import datetime
import time

import dotenv
import os
import telebot
from loguru import logger
import telegram_bot.bot_messages as bot_messages
from hotels_API import api_requests
from telegram_bot.request_data import *
import psycopg2

dotenv.load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)


def sql_connect_and_insert_data(db_chat_id: str, db_command: str, db_city: str) -> None:
    sql_connect = psycopg2.connect(
        host='localhost',
        database=os.getenv('db_name'),
        user=os.getenv('db_username'),
        password=os.getenv('db_password')
    )
    cursor = sql_connect.cursor()
    sql_command = f'''
    INSERT INTO queries(chat_id, command, city, date_time)
    VALUES('{db_chat_id}', '{db_command}', '{db_city}', CURRENT_TIMESTAMP)
                  '''
    cursor.execute(sql_command)
    sql_connect.commit()
    sql_connect.close()


def sql_connect_and_read_data(db_chat_id) -> list:
    sql_connect = psycopg2.connect(
        host='localhost',
        database=os.getenv('db_name'),
        user=os.getenv('db_username'),
        password=os.getenv('db_password')
    )
    cursor = sql_connect.cursor()
    sql_command = f'''
        SELECT * FROM queries WHERE chat_id = '{db_chat_id}' ORDER BY date_time DESC LIMIT 5;
                      '''
    cursor.execute(sql_command)
    data = cursor.fetchall()
    sql_connect.commit()
    sql_connect.close()
    return data



city = None
logger.add(f'logging/{datetime.datetime.now().strftime("%Y/%m/%d/%H:%M:%S")}.log', rotation="00:00")


@logger.catch()
def request_data_update(message: telebot.types.Message, chat_id: int, command: str = None) -> None:
    """Updates request data in request_data.py."""
    chat_id = str(chat_id)
    user = requests_dict[chat_id]
    user.last_message_id = message.message_id
    user.chat_id = message.chat.id
    user.last_message_text = message.text
    user.last_message_keyboard = message.reply_markup
    logger.debug(f'Update request: {chat_id}.')
    if command:
        user.command = command


@logger.catch()
def results_quantity_setter(request: Request) -> None:
    """Sends the message to the user to pick the max quantity of the possible search results."""
    logger.debug(f'Request: {request.chat_id}.')
    results_quantity_keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    five_button = telebot.types.InlineKeyboardButton(text='5', callback_data=5)
    ten_button = telebot.types.InlineKeyboardButton(text='10', callback_data=10)
    fifteen_button = telebot.types.InlineKeyboardButton(text='15', callback_data=15)
    results_quantity_keyboard.add(five_button, ten_button, fifteen_button)
    bot_mes = bot.send_message(chat_id=request.chat_id,
                               text=bot_messages.following_messages[request.lang]['search_result'],
                               reply_markup=results_quantity_keyboard)
    request_data_update(message=bot_mes, chat_id=request.chat_id)


@logger.catch()
def options_message(request: Request) -> None:
    """Sends the bot.message with the bot information and the options (with the inline keyboard of options)in order
    for user to pick next command..
    The function is used as the reply for the /start(second part), /help and when the search is done
    shows the options to the user again."""
    logger.debug(f'Request: {request.chat_id}.')
    options_keyboard = telebot.types.InlineKeyboardMarkup()
    low_price_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['low_price'],
                                                          callback_data='/low_price')
    high_price_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['high_price'],
                                                           callback_data='/high_price')
    best_deal_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['best_deal'],
                                                          callback_data='/best_deal')
    done_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['done'],
                                                     callback_data='/done')
    options_keyboard.row(low_price_button, high_price_button)
    options_keyboard.row(best_deal_button)
    options_keyboard.row(done_button)
    bot_mes = bot.send_message(chat_id=request.chat_id,
                               text=bot_messages.following_messages[request.lang]['help_message'],
                               reply_markup=options_keyboard)
    request_data_update(message=bot_mes, chat_id=bot_mes.chat.id)


@logger.catch()
def inline_keyboard_remover(request: Request) -> None:
    """Function checks if the last message sent by bot has an inline keyboard, and if so,
     edits it (removes the keyboard) after the user clicks on one of the buttons"""
    logger.debug(f'Request: {request.chat_id}.')
    if request.last_message_keyboard:
        bot.edit_message_text(chat_id=request.chat_id, message_id=request.last_message_id,
                              text=request.last_message_text, reply_markup=None)


@logger.catch()
def search_commands_handler(request, command):
    """Sends the message to the customer with the request of the city for the search. Used after the user picks the
    command (message of callback received is in ['/low_price', '/high_price', '/best_deal'] """
    logger.debug(f'Request: {request.chat_id}.')
    bot_mes = bot.send_message(chat_id=request.chat_id,
                               text=bot_messages.following_messages[request.lang]['city'])
    request_data_update(message=bot_mes, chat_id=bot_mes.chat.id, command=command)


@logger.catch()
@bot.message_handler(commands=['history'])
def history_command(message: telebot.types.Message) -> None:
    """Handles /history command. Returns up to 5 last search commands for given chat id."""
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        logger.debug(f'Request: {request.chat_id}.')
        language = request.lang
        chat_id = request.chat_id
        data = sql_connect_and_read_data(chat_id)
        if data:
            message_text = bot_messages.following_messages[language]['history_message']
            message_text += '\n'
            for inquery in data:
                message_text += f'command: {inquery[1]}, city: {inquery[2]}, date and time: {inquery[3].date()}\n'
        else:
            message_text = bot_messages.following_messages[language]['no_history']
        bot.send_message(chat_id=chat_id, text=message_text)
        options_message(request)





@logger.catch()
@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> None:
    """Handles /start command. Asks user to chose a language. Communication has to always start with
    /start command, thus the chat_id saved."""
    chat_id = message.chat.id
    logger.debug(f'Request: {chat_id}.')
    requests_dict[f'{chat_id}'] = Request()
    language_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    eng_button = telebot.types.InlineKeyboardButton(text='Eng/Англ', callback_data='en')
    ru_button = telebot.types.InlineKeyboardButton(text='Rus/Рус', callback_data='ru')
    language_keyboard.add(eng_button, ru_button)
    bot_mes = bot.send_message(chat_id=chat_id, text=f"{bot_messages.language_message}",
                               reply_markup=language_keyboard)
    request_data_update(message=bot_mes, chat_id=chat_id)


@logger.catch()
@bot.callback_query_handler(lambda call: call.data in bot_messages.languages)
def lang_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Handles all the callbacks received from the user clicking in the offered inline keyboard."""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        inline_keyboard_remover(request)
        request.lang = call.data
        options_message(request)
        logger.debug(f'Request: {request.chat_id}.')


@logger.catch()
@bot.callback_query_handler(lambda call: call.data in ['/low_price', '/high_price', '/best_deal'])
def command_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Handles the commands ['/low_price', '/high_price', '/best_deal'] in the form of callback query. Follows with the
    message asking to provide the city"""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        inline_keyboard_remover(request)
        command = call.data
        search_commands_handler(request=request, command=command)
        logger.debug(f'Request: {request.chat_id}.')


@logger.catch()
@bot.message_handler(commands=['low_price', 'high_price', 'best_deal'])
def start_command(message: telebot.types.Message) -> None:
    """Handles the commands ['/low_price', '/high_price', '/best_deal'] in the form of message. Follows with the
    message asking to provide the city"""
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        inline_keyboard_remover(request)
        command = message.text
        search_commands_handler(request=request, command=command)
        logger.debug(f'Request: {request.chat_id}.')


@logger.catch()
@bot.callback_query_handler(lambda call: call.data == '/done')
def done_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Handles the command /done in the form of callback query"""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        inline_keyboard_remover(request)
        message_text = bot_messages.following_messages[request.lang]['done_message']
        bot.send_message(chat_id=request.chat_id, text=message_text)
        requests_dict.pop(str(request.chat_id))
        logger.debug(f'Request: {request.chat_id}.')


@bot.message_handler(commands=['done'])
def done_command(message: telebot.types.Message) -> None:
    """Handles the command /done in the form of message removes the request.chat_id from """
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        inline_keyboard_remover(request)
        message_text = bot_messages.following_messages[request.lang]['done_message']
        bot.send_message(chat_id=request.chat_id, text=message_text)
        requests_dict.pop(str(request.chat_id))


@bot.callback_query_handler(lambda call: call.data == '/yes')
def yes_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Function handles '/yes' in a callback query form. That is the confirmation of the city."""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        inline_keyboard_remover(request)
        request.city = city
        if request.command == '/best_deal':
            """If the command is best_deal additional information is required.
            Here the bot asks for the prices range"""
            bot_mes = bot.send_message(chat_id=request.chat_id,
                                       text=bot_messages.following_messages[request.lang]['best_deal_prices'])
            request_data_update(message=bot_mes, chat_id=request.chat_id)
        elif request.command in ['/low_price', '/high_price']:
            """"If the command is in ['/low_price', '/high_price'], the amount of the search results is asked."""
            results_quantity_setter(request)


@bot.callback_query_handler(lambda call: call.data == '/no')
def yes_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Function handles '/no' in a callback query form. That means that the user does not confirm the city,
    so the bot asks for the city again."""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        inline_keyboard_remover(request)
        bot_mes = bot.send_message(chat_id=request.chat_id,
                                   text=bot_messages.following_messages[request.lang]['city'])
        request_data_update(message=bot_mes, chat_id=request.chat_id)


@bot.callback_query_handler(lambda call: call.data in ['5', '10', '15'])
def max_searches_callback_handler(call: telebot.types.CallbackQuery) -> None:
    """Handles the max searches choice as the callback query. That is the last step before the API is involved."""
    if str(call.message.chat.id) in requests_dict:
        request = requests_dict[str(call.message.chat.id)]
        sql_connect_and_insert_data(request.chat_id, request.command, request.city)
        inline_keyboard_remover(request)
        request.search_results = call.data
        if request.lang == 'ru':
            if request.command == '/low_price':
                message_text = f'Ищу дешевые отели в {request.city}.\n' \
                               f'Максимальное количиство результатов - {request.search_results}'
                bot.send_message(chat_id=request.chat_id, text=message_text)
                try:
                    message_text = api_requests.low_price(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)
            elif request.command == '/high_price':
                message_text = f'Ищу дорогие отели в {request.city}.\n' \
                               f'Максимальное количиство результатов - {request.search_results}'
                bot.send_message(chat_id=request.chat_id, text=message_text)
                try:
                    message_text = api_requests.high_price(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)
            elif request.command == '/best_deal':
                message_text = f'Ищу отели в {request.city}.\n' \
                               f'Ценовой диапазон {request.min_price} - {request.max_price} €\n' \
                               f'Максимальное расстояние от центра - {request.distance} км\n' \
                               f'Максимальное количиство результатов - {request.search_results}'
                bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                request_data_update(message=bot_mes, chat_id=request.chat_id)
                try:
                    message_text = api_requests.best_deal(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)
        elif request.lang == 'en':
            if request.command == '/low_price':
                message_text = f'Searching for the cheapest hotels in {request.city}.\n' \
                               f'Max amount of search results - {request.search_results}'
                bot.send_message(chat_id=request.chat_id, text=message_text)
                try:
                    message_text = api_requests.low_price(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)
            elif request.command == '/high_price':
                message_text = f'Searching for the most expensive hotels in {request.city}.\n' \
                               f'Max amount of search results - {request.search_results}'
                bot.send_message(chat_id=request.chat_id, text=message_text)
                try:
                    message_text = api_requests.high_price(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)
            elif request.command == '/best_deal':
                message_text = f'Searching for the hotels in {request.city}.\n' \
                               f'Price range {request.min_price} - {request.max_price} €\n' \
                               f'Farthest distance from the center of the city - {request.distance} miles\n' \
                               f'Max amount of search results - {request.search_results}'
                bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                request_data_update(message=bot_mes, chat_id=request.chat_id)
                try:
                    message_text = api_requests.best_deal(request=request)
                    bot_mes = bot.send_message(chat_id=request.chat_id, text=message_text)
                    request_data_update(message=bot_mes, chat_id=request.chat_id)
                except ResponseError:
                    bot.send_message(chat_id=request.chat_id,
                                     text=bot_messages.following_messages[request.lang]['request_error'])
                    request.city = None
                options_message(request)


@bot.message_handler(commands=['help'])
def send_bot_info(message: telebot.types.Message) -> None:
    """Sends to the user the welcome message which contains all the information on the bot and the commands."""
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        inline_keyboard_remover(request)
        options_message(request=request)


@bot.message_handler(func=lambda msg: '-' in msg.text)
def best_deal_price_handler(message: telebot.types.Message) -> None:
    """Catches the message with the price range for the best deal in the format: min - max."""
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        inline_keyboard_remover(request)
        if not request.city:
            city_handler(message)
            return
        elif request.city and not request.max_price:
            try:
                prices = message.text.split('-')
                int(prices[0])
                int(prices[1])
                request.min_price, request.max_price = prices[0], prices[1]

                bot_mes = bot.send_message(chat_id=request.chat_id,
                                           text=bot_messages.following_messages[request.lang]
                                           ['distance_from_center_message'])
            except ValueError:
                bot_mes = bot.send_message(chat_id=request.chat_id,
                                           text=bot_messages.following_messages[request.lang]['wrong_prices'])
            request_data_update(bot_mes, message.chat.id)
        elif request.city and request.max_price and not request.distance:
            distance_handler(message)


@bot.message_handler(content_types=['text'])
def city_handler(message: telebot.types.Message) -> None:
    """Catches the city and provides as the request.city data."""
    global city
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        inline_keyboard_remover(request)
        if request.command:
            if not request.city:
                city = message.text
                yes_no_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                yes_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['yes'],
                                                                callback_data='/yes')
                no_button = telebot.types.InlineKeyboardButton(text=bot_messages.buttons[request.lang]['no'],
                                                               callback_data='/no')
                yes_no_keyboard.add(yes_button, no_button)
                bot_mes = bot.send_message(chat_id=request.chat_id,
                                           text=f'{bot_messages.following_messages[request.lang]["city_confirmation"]} '
                                                f'{city}',
                                           reply_markup=yes_no_keyboard)
                request_data_update(message=bot_mes, chat_id=request.chat_id)
            elif request.city and not request.max_price:
                best_deal_price_handler(message)
            elif request.max_price:
                distance_handler(message)


@bot.message_handler(content_types=['text'])
def distance_handler(message: telebot.types.Message) -> None:
    """Gets the distance for the best deal command and provides it as the request.distance"""
    if str(message.chat.id) in requests_dict:
        request = requests_dict[str(message.chat.id)]
        if request.city and request.max_price:
            try:
                int(message.text)
            except ValueError:
                bot_mes = bot.send_message(chat_id=request.chat_id,
                                           text=bot_messages.following_messages[request.lang]['distance_error'])
                request_data_update(message=bot_mes, chat_id=request.chat_id)
                return
            request.distance = message.text
            results_quantity_setter(request)


if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
