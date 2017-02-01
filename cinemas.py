import requests
import argparse
import re
from operator import itemgetter
from bs4 import BeautifulSoup


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).content


def get_title(movie_html):
    return movie_html.find('a', {'href': re.compile('afisha')}).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')
    for movie in soup.find_all('div', {'class': re.compile('s-votes')}):
        movie_id = movie.get('id')
        cinemas_count = (
            len(movie.find_all('tr', {'id': re.compile(movie_id)})))
        yield {'title': get_title(movie), 'cinemas_count': cinemas_count}


def get_rating(movie_id):
    movie_info_url = 'http://kparser.pp.ua/json/film/'
    movie_json = requests.get(
        '{}{}'.format(movie_info_url, movie_id)).json()

    if movie_json.get('aggregateRating'):
        return movie_json['aggregateRating'][0]['properties']['ratingValue'][0]
    else:
        return '0'


def fetch_movie_info(movie):
    k_parser = 'http://kparser.pp.ua/json/search/'
    movie_list = requests.get(
        '{}{}'.format(k_parser, movie['title'])).json()['result']
    sorted(movie_list, key=lambda movie: movie['most_wanted'])
    if movie_list:
        if movie_list[0].get('id'):
            rating = get_rating(movie_list[0].get('id'))
            return (movie['title'], rating, movie['cinemas_count'])
        else:
            return (movie['title'], 0, movie['cinemas_count'])


def get_top_10_movies(movies, arthouse):
    if arthouse:
        return sorted(movies, key=itemgetter(1))[:10]
    else:
        return sorted(movies, key=itemgetter(1, 2))[:10]


def output_movies_to_console(movies, arthouse):
    for movie in movies_list:
        print ('{} {}'.format(movie[0], movie[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--art', help="Show arthouse movies!", action='store_true')
    args = parser.parse_args()

    movies_info = []
    for movie in parse_afisha_list(fetch_afisha_page()):
        movies_info.append(fetch_movie_info(movie))
    movies_info_list = [movie for movie in movies_info if movie is not None]
    output_movies_to_console(get_top_10_movies(movies_info_list, args.art))
