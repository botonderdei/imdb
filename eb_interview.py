import pandas as pd
from bs4 import BeautifulSoup
import requests
import constants
import re


def scrap_name(movie):
    name = movie.find('td', class_='titleColumn').a.text
    return name


def scrap_votes(movie):
    votes = movie.find('span', {"name": 'nv'})['data-value']
    return votes


def scrap_rating(movie):
    rating = movie.find('td', class_='ratingColumn imdbRating').strong.text
    return rating


def scrap_oscars(movie):
    movie_link = movie.find('td', class_='titleColumn').a.attrs.get('href')
    movie_response = requests.get(main_url + movie_link)
    movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
    won_oscar = str(movie_soup.find(string=re.compile('Won [0-9]')))
    oscar = 0 if won_oscar == 'None' else int(''.join(filter(str.isdigit, won_oscar)))
    return oscar


def scraper(movie_arr):
    movie_names = []
    oscar_count = []
    ratings = []
    vote_count = []

    for movie in movie_arr:
        # .span.attrs.get('data-value')

        name = scrap_name(movie)
        movie_names.append(name)

        votes = scrap_votes(movie)
        vote_count.append(int(votes))

        rating = scrap_rating(movie)
        ratings.append(float(rating))

        oscar = scrap_oscars(movie)
        oscar_count.append(oscar)

    movie_dict = {'Name': movie_names, 'Oscars': oscar_count, 'Rating': ratings, 'Votes': vote_count}
    return movie_dict


def review_penalizer(votes_arr, ratings_arr):
    max_vote = max(votes_arr)
    adjusted_numbers = []
    for i in range(0, len(votes_arr)):
        penalty = round((max_vote - votes_arr[i]) / 100000)
        num = round(float(ratings_arr[i]) - penalty * 0.1, 1)
        adjusted_numbers.append(num)

    return adjusted_numbers


def oscar_score_calculator(number_of_oscars):
    score = 0
    if number_of_oscars == 0:
        score = 0
    elif number_of_oscars < 2:
        score = 0.3
    elif number_of_oscars < 5:
        score = 0.5
    elif number_of_oscars < 10:
        score = 1
    else:
        score = 1.5
    return score


def oscar_calculator(oscar_arr, rating_arr):
    adjusted_numbers = []
    for i in range(0, len(oscar_arr)):
        num = round(rating_arr[i] + oscar_score_calculator(oscar_arr[i]), 1)
        adjusted_numbers.append(num)
    return adjusted_numbers


def adjusted_data(data_arr):
    after_oscar_calc = oscar_calculator(data_arr['Oscars'], data_arr['Rating'])
    data_arr['Rating'] = after_oscar_calc
    after_vote_calc = review_penalizer(data_arr['Votes'], data_arr['Rating'])
    data_arr['Rating'] = after_vote_calc
    return data_arr


if __name__ == '__main__':
    main_url = constants.MAIN_URL
    top_list = constants.TOP_LIST

    response = requests.get(top_list)
    soup = BeautifulSoup(response.text, 'html.parser')
    movies = soup.find('tbody', class_='lister-list').find_all('tr')[:constants.TOP_NUMBER]

    data = scraper(movies)
    df_before = pd.DataFrame(data, index=pd.RangeIndex(start=1, stop=constants.TOP_NUMBER+1, name='Rank'))

    after_adjustments = adjusted_data(data)
    dt_after = pd.DataFrame(after_adjustments, index=pd.RangeIndex(start=1, stop=constants.TOP_NUMBER+1, name='Rank'))
    df_after = dt_after.sort_values('Rating', ascending=False, ignore_index=True)

    df_combined = pd.concat([df_before, df_after])
    df_combined.to_csv('result.csv')
