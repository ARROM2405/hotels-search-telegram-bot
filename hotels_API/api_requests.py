import datetime
import dotenv
import os
from math import ceil

import requests

from telegram_bot.request_data import *
from loguru import logger

logger.add(f'logging/{datetime.datetime.now().strftime("%Y/%m/%d/%H:%M:%S")}.log', rotation="00:00")

dotenv.load_dotenv()
api_key = os.getenv('API_KEY')

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': api_key
}


@logger.catch()
def destination_id_search(city: str, locale: str) -> int:
    logger.debug(f'city: {city}.')
    """Searches the location (city) and returns destination ID needed for the hotels search"""
    querystring = {"query": city, "locale": locale}
    location_url = "https://hotels4.p.rapidapi.com/locations/search"
    r = requests.request("GET", url=location_url, headers=headers, params=querystring)
    try:
        destination_id = r.json()['suggestions'][0]['entities'][0]['destinationId']
        return destination_id
    except Exception:
        raise ResponseError


@logger.catch()
def dates_range() -> tuple:
    start_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    logger.debug(f'Dates range set {start_date} - {end_date}')
    return start_date, end_date


@logger.catch()
def get_hotels(request: Request, sort_order: str, price_min: int = None, price_max: int = None) -> str:
    hotels_search_url = "https://hotels4.p.rapidapi.com/properties/list"
    if request.lang == 'en':
        language = 'en_IE'
    elif request.lang == 'ru':
        language = 'ru_RU'
    destination_id = destination_id_search(city=request.city, locale=language)
    dates = dates_range()
    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": request.search_results,
                   "checkIn": dates[0], "checkOut": dates[1], "adults1": "1", "sortOrder": sort_order,
                   "locale": language, "currency": "EUR"}
    if price_max and price_min:
        querystring['priceMin'] = f'{price_min}'
        querystring['priceMax'] = f'{price_max}'
    response = requests.request("GET", hotels_search_url, headers=headers, params=querystring).json()
    if len(response['data']['body']['searchResults']['results']) == 0:
        raise ResponseError
    num = 1
    result = ''
    for hotel in response['data']['body']['searchResults']['results']:
        name = hotel['name']
        stars = '⭐' * int(ceil(hotel['starRating']))
        address = f"{hotel['address']['locality']}"
        distance = f"Distance from the center - {hotel['landmarks'][0]['distance']}"
        # price = f"{hotel['ratePlan']['price']['current']} {hotel['ratePlan']['price']['info']}"
        price = f"{hotel.get('ratePlan', {}).get('price', {}).get('current')} " \
                f"{hotel.get('ratePlan', {}).get('price', {}).get('info')}"
        if sort_order == "DISTANCE_FROM_LANDMARK":
            if hotel['landmarks'][0]['distance'] > request.distance:
                continue
        result += f"{num}. {name}\n{stars}\n{address}\n{distance}\n{price}\n\n"
        num += 1
    logger.debug(f'Done hotels search. Request: {request.chat_id}.')
    request.command = None
    request.city = None
    request.min_price = None
    request.max_price = None
    request.distance = None
    request.search_results = None
    request.destinationID = None
    return result


hotels_search_url = "https://hotels4.p.rapidapi.com/properties/list"


@logger.catch()
def low_price(request: Request) -> str:
    logger.debug(f'Returning the search result. Request: {request.chat_id}.')
    result = get_hotels(request=request, sort_order="PRICE")
    return result


@logger.catch()
def high_price(request: Request) -> str:
    logger.debug(f'Returning the search result. Request: {request.chat_id}.')
    result = get_hotels(request=request, sort_order="PRICE_HIGHEST_FIRST")
    return result


@logger.catch()
def best_deal(request: Request) -> str:
    logger.debug(f'Returning the search result. Request: {request.chat_id}.')
    result = get_hotels(request=request, sort_order="DISTANCE_FROM_LANDMARK", price_min=request.min_price,
                        price_max=request.max_price)
    return result
