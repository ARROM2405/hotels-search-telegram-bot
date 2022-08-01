"""File keeps all the messages that bot uses"""
from . import requests_handler

languages = ['en', 'ru']
commands = ['low_price', 'high_price', 'best_deal', 'history']

language_message = 'Please choose the language\n' \
                   'Пожалуйста, выбери язык для общения'

following_messages = {'en': {
    'hi_message': 'Hi, my purpose of existence is helping you to find the hotel you would like. FYI: prices are given '
                  'in EUR, '
                  'distance in miles.',
    'help_message':
        '''Please pick one of the options:
/low_price - list of the hotels at the lowest price
/high_price - list of the hotels at the highest price
/best_deal - list of closest hotels to the location in the indicated price margins
/history - history of your searches
/done - end of the request''',
    'currency_message': 'What currency would you like the prices to be in?',
    'city_message': 'What city would you like to go to?',
    'hotels_quantity_message': 'How many hotels would you like me to suggest?',
    'max_price_message': 'What is the highest price is acceptable?',
    'lowest_price_message': 'What is the lowest price you would like to start with?',
    'distance_from_center_message': 'What is the farthest distance from center you want the hotel to be in, miles?',
    'history_message': 'Here is the history of your requests:',
    'no_history': 'No previous requests from you.',
    'done_message': 'Your inquiry is closed. If needed, please start a ney inquiry with a /start command.',
    'best_deal_prices': 'Please input tha acceptable price range in the format: min price - max price in €.',
    'best_deal_distance': 'Please provide the distance range to the center in which the hotel can be located',
    'wrong_prices': 'The information provided has incorrect format. Please provide the prices in the format:'
                    'min price - max price.',
    'city': 'In which city are we looking for the hotels?',
    'city_confirmation': f'Please confirm the  city - ',
    'search_result': 'How many search results there should be max?',
    'distance_error': 'Incorrect data is entered. Please input the max distance again.',
    'request_error': 'Something went wrong. Please start all over.'
},
    'ru': {
        'hi_message': 'Привет, моя цель помочь тебе в поиске отеля. Информативно: цены указываются в EUR, расстояние '
                      'в км.',
        'help_message':
            '''Пожалуйста, выбери одну их опций:
/low_price (низкая цена) - список самых дешевых отелей
/high_price (высокая цена) - список самых дорогих отелей
/best_deal (лучшее предложение) - список самых близких отелей в определенных ценовых рамках
/history - история ваших поисков
/done (закончить запрос) - закончить запрос''',
        'currency_message': 'В какой валюте мне показывать цены?',
        'city_message': 'В каком городе ищем отель?',
        'hotels_quantity_message': 'Какое максимальное количиство отелей мне предложить?',
        'max_price_message': 'Какая максимальная цена является приемлемой?',
        'lowest_price_message': 'С какой самой низкой цены мне начать поиск?',
        'distance_from_center_message': 'В каком диапазоне от центра города мне искать отели, в км?',
        'history_message': 'Вот твоя история запросов:',
        'no_history': 'Раннее не было от вас запросов.',
        'done_message': 'Ваш запрос закрыт. Если нужно, пожалуйста начните новый запрос с помощъю команды /start',
        'best_deal_prices': 'Пожалуйста, укажите ценовой диапазон в формате: минимальная цена - максимальная цена в €.',
        'best_deal_distance':
            'Пожалуйста, укажите возможное максимальное расстояние от центра города для расположения отеля',
        'wrong_prices': 'Вы что-то указали некорректно. Пожалуйста укажите ценовой диапазон в формате:'
                        ' минимальная цена - максимальная цена в €.',
        'city': 'В каком городе ищем отели?',
        'city_confirmation': f'Пожалуйста подтвердите город - ',
        'search_result': 'Какое максимальное количиство результатов поиска может быть?',
        'distance_error': 'Вы указали расстояние не правильно. Пожалуйста введите данные в км еще раз.',
        'request_error': 'Что-то пошло не так. Начните поиск заново.'
    }
}

buttons = {'en': {'low_price': 'low price',
                  'high_price': 'high price',
                  'best_deal': 'best deal',
                  'history': 'history',
                  'done': 'done',
                  'yes': 'yes',
                  'no': 'no'},
           'ru': {'low_price': 'низкая цена',
                  'high_price': 'высокая цена',
                  'best_deal': 'лучшее предложение',
                  'history': 'история запросов',
                  'done': 'закончить запрос',
                  'yes': 'да',
                  'no': 'нет'}}
