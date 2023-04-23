import requests
import random


# функция получения шуток про Чака Норриса
def chuk_norris_joke():
    API_CHUK_NORRIS_URL: str = 'https://api.chucknorris.io/jokes/random'
    joke = requests.get(API_CHUK_NORRIS_URL).json()['value']
    return joke


# функция получения шуток с оскорблениями
def insult_joke():
    API_EVILINSULT_URL: str = 'https://evilinsult.com/generate_insult.php?lang=en&amp;type=json'
    joke = requests.get(API_EVILINSULT_URL).text
    return joke


# функция получения шуток по жанрам
def genre_joke(genre):
    '''
    genre in ['Programming', 'Dark', 'Pun', 'Spooky']
    '''
    API_JOKES_URL: str = 'https://v2.jokeapi.dev/joke/'
    joke_json = requests.get(f'{API_JOKES_URL}{genre}').json()
    if joke_json['type'] == 'single':
        return joke_json['joke']
    if joke_json['type'] == 'twopart':
        return f'{joke_json["setup"]}\n{joke_json["delivery"]}'


# функция получения всяких других шуток
def random_joke():
    API_RANDOM_JOKES_URL = [
        'https://official-joke-api.appspot.com/random_joke',
        'https://v2.jokeapi.dev/joke/Misc']
    url_number = random.randint(0, 1)
    joke_json = requests.get(API_RANDOM_JOKES_URL[url_number]).json()
    if url_number == 1:
        if joke_json['type'] == 'single':
            return joke_json['joke']
        if joke_json['type'] == 'twopart':
            return f'{joke_json["setup"]}\n{joke_json["delivery"]}'
    if url_number == 0:
        return f'{joke_json["setup"]}\n{joke_json["punchline"]}'
