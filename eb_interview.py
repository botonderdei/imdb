import pandas as pd
from bs4 import BeautifulSoup
import requests
import constants
import re


def scrap_name(movie):
    """
    Takes a parsed chunk of HTML and searches for the movie name in it.
    :param movie: bs4.element.Tag
    HTML code of a single movie.
    :return: str
    The name of the movie
    """
    name = movie.find('td', class_='titleColumn').a.text
    return name


def scrap_votes(movie):
    """
    Takes a parsed chunk of HTML and searches for the number of votes of the particular movie.
    :param movie: bs4.element.Tag
    HTML code of a single movie.
    :return: str
    The number of votes that the current movie has.
    """
    votes = movie.find('span', {"name": 'nv'})['data-value']
    return votes


def scrap_rating(movie):
    """
    Takes a parsed chunk of HTML and searches for the rating of the movie in it.
    :param movie: bs4.element.Tag
    HTML code of a single movie.
    :return: str
    The rating of the movie.
    """
    rating = movie.find('td', class_='ratingColumn imdbRating').strong.text
    return rating


def scrap_oscars(movie):
    """
    Takes a parsed chunk of HTML and searches for the link of the movie. Then parses the movie's own page and searches
    for it's oscar count.
    :param movie: bs4.element.Tag
    HTML code of a single movie.
    :return: int
    The number of oscars the movie has.
    """
    movie_link = movie.find('td', class_='titleColumn').a.attrs.get('href')
    movie_response = requests.get(constants.MAIN_URL + movie_link)
    movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
    won_oscar = str(movie_soup.find(string=re.compile('Won [0-9]')))
    oscar = 0 if won_oscar == 'None' else int(''.join(filter(str.isdigit, won_oscar)))
    return oscar


def scraper(movie_arr):
    """
    Scraps the data for each movie in the movie list with the previously created functions. Then stores the return
    values in lists and makes a dictionary out of them when the scrapping is finished.
    :param movie_arr: list
    A list which contains the parsed HTML code of each movie.
    :return: dict
    A dictionary which contains all the scrapped data.
    """
    movie_names = []
    oscar_count = []
    ratings = []
    vote_count = []

    for movie in movie_arr:
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
    """
    Calculates the penalty based on the number of votes and returns the adjusted ratings in a list rounded to one digit.
    :param votes_arr: list
    A list which contains the number of votes for each movie.
    :param ratings_arr: list
    A list which contains the rating of each movie.
    :return: list
    A list that contains the updated ratings.
    """
    max_vote = max(votes_arr)
    adjusted_numbers = []
    for i in range(0, len(votes_arr)):
        penalty = round((max_vote - votes_arr[i]) / 100000)
        num = round(float(ratings_arr[i]) - penalty * 0.1, 1)
        adjusted_numbers.append(num)

    return adjusted_numbers


def oscar_score_calculator(number_of_oscars):
    """
    Calculates the bonus score based on the number of oscars.
    :param number_of_oscars: int
    The number of oscars.
    :return: float
    The calculated score.
    """
    score = 0
    if number_of_oscars == 0:
        score = 0
    elif number_of_oscars <= 2:
        score = 0.3
    elif number_of_oscars <= 5:
        score = 0.5
    elif number_of_oscars <= 10:
        score = 1
    else:
        score = 1.5
    return float(score)


def oscar_calculator(oscar_arr, rating_arr):
    """
    Creates and returns a list which stores the adjusted ratings. It uses the score calculator function to achieve this.
    :param oscar_arr: list
    A list which contains the number of oscars for each movie.
    :param rating_arr: list
    A list which contains the rating of each movie.
    :return: list
    A list that contains the adjusted rating.
    """
    adjusted_numbers = []
    for i in range(0, len(oscar_arr)):
        adjusted_rating = round(rating_arr[i] + oscar_score_calculator(oscar_arr[i]), 1)
        adjusted_numbers.append(adjusted_rating)
    return adjusted_numbers


def adjusted_data(data_arr):
    """
    Takes the base dictonary and does the score adjustments.
    :param data_arr: dict
    The results of the first scraping.
    :return: dict
    The dict that contains the updated ratings.
    """
    after_oscar_calc = oscar_calculator(data_arr['Oscars'], data_arr['Rating'])
    data_arr['Rating'] = after_oscar_calc
    after_vote_calc = review_penalizer(data_arr['Votes'], data_arr['Rating'])
    data_arr['Rating'] = after_vote_calc
    return data_arr


if __name__ == '__main__':

    response = requests.get(constants.TOP_LIST)
    soup = BeautifulSoup(response.text, 'html.parser')
    movies = soup.find('tbody', class_='lister-list').find_all('tr')[:constants.TOP_NUMBER]

    # Creates the dict which contains the scrapped data
    data = scraper(movies)
    #Create the dataframe using the data
    df_before = pd.DataFrame(data, index=pd.RangeIndex(start=1, stop=constants.TOP_NUMBER + 1, name='Rank'))
    #Create the dict which containes the modified ratings
    after_adjustments = adjusted_data(data)
    #The dataframe which contains the data after modification
    dt_after = pd.DataFrame(after_adjustments, index=pd.RangeIndex(start=1, stop=constants.TOP_NUMBER + 1, name='Rank'))
    df_after = dt_after.sort_values('Rating', ascending=False, ignore_index=True)

    #Combine the two dataframes and print them in a csv
    df_combined = pd.concat([df_before, df_after])
    df_combined.to_csv('result.csv')
