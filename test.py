import unittest
import eb_interview
from bs4 import BeautifulSoup
import requests
import constants

class WidgetTestCase(unittest.TestCase):
    test_soup = None
    main_url = constants.MAIN_URL
    top_list = constants.TOP_LIST

    @classmethod
    def setUpClass(cls):
        response = requests.get(WidgetTestCase.top_list)
        soup = BeautifulSoup(response.text, 'html.parser')
        WidgetTestCase.test_soup = soup.find('tbody', class_='lister-list').find_all('tr')[:constants.TOP_NUMBER]


    def test_scrap_name(self):
        self.assertTrue(WidgetTestCase.test_soup)
        self.assertEqual(len(WidgetTestCase.test_soup), constants.TOP_NUMBER)
        self.assertTrue(type(eb_interview.scrap_name(WidgetTestCase.test_soup[0])), str)

    def test_scrap_votes(self):
        self.assertTrue(WidgetTestCase.test_soup)
        self.assertTrue(type(eb_interview.scrap_votes(WidgetTestCase.test_soup[0])), str)

    def test_scrap_rating(self):
        self.assertTrue(WidgetTestCase.test_soup)
        self.assertTrue(type(eb_interview.scrap_rating(WidgetTestCase.test_soup[0])), str)

    def test_scrap_oscars(self):
        self.assertTrue(WidgetTestCase.test_soup)
        self.assertTrue(type(eb_interview.scrap_oscars(WidgetTestCase.test_soup[0])), str)

    def test_scrapper(self):
        self.assertTrue(WidgetTestCase.test_soup)
        test_dict = eb_interview.scraper(WidgetTestCase.test_soup)
        self.assertTrue(type(test_dict), dict)
        self.assertTrue(test_dict)

    def test_review_penalizer(self):
        test_votes = [100000, 200000, 300000]
        test_ratings = [7.2, 8.1, 9]
        test_numbers = eb_interview.review_penalizer(test_votes, test_ratings)
        self.assertEqual(test_numbers, [7, 8, 9])

    def test_oscar_score_calculator(self):
        self.assertEqual(eb_interview.oscar_score_calculator(10), 1)

    def test_oscar_calculator(self):
        test_oscars = [0,1,3,6,10,11]
        test_ratings = [1,2,3,4,5,6]
        results = [1, 2.3, 3.5, 5, 6, 7.5]
        self.assertEqual(eb_interview.oscar_calculator(test_oscars, test_ratings), results)

    def test_adjusted_data(self):
        test_names = ['test1', 'test2']
        test_oscars = [8, 11]
        test_ratings = [6.1, 7]
        test_votes = [200000, 300000]

        result_ratings = [7, 8.5]

        test_dict= {'Name': test_names, 'Oscars': test_oscars, 'Rating': test_ratings, 'Votes': test_votes}
        result_dict = {'Name': test_names, 'Oscars': test_oscars, 'Rating': result_ratings, 'Votes': test_votes}

        test_data = eb_interview.adjusted_data(test_dict)

        self.assertEqual(test_data, result_dict)

if __name__ == '__main__':
    unittest.main()
