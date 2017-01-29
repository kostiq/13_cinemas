import requests
import argparse
import re
from bs4 import BeautifulSoup
from kinopoisk.movie import Movie


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).content


def get_title(movie_html):
    return movie_html.find('a', {'href': re.compile('afisha')}).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')
    for movie in soup.find_all('div', {'class': re.compile('s-votes')}):
        movie_id = movie.get('id')
        cinema_count = (
            len(movie.find_all('tr', {'id': re.compile(movie_id)})))
        yield (get_title(movie), cinema_count)


def fetch_movie_info(movie, arthouse):
    title, count = movie
    if arthouse or count > 30:
        movie_list = Movie.objects.search(title)
        if movie_list:
            movie = Movie(id=movie_list[0].id)
            movie.get_content('main_page')
            print (movie.title, movie.rating, count)
            return (movie.title, movie.rating, count)


def output_movies_to_console(movies):
    print (sorted(movies, key=lambda tup: tup[1])[:10])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--art', help="Show arthouse movies!", action='store_true')
    args = parser.parse_args()

    movies_info = []
    for movie in parse_afisha_list(fetch_afisha_page()):
        movies_info.append(fetch_movie_info(movie, args.art))
    output_movies_to_console(movies_info)
