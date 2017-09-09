# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from time import sleep
from scrapy.conf import settings
import lxml.html
from datetime import datetime
from dateutil import tz


SPORT_URL_XPATH = '//*[@id="app"]/div/div/div[2]/div/nav/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]/a/@href'
COMPETITIONS_NAMES_XPATH = '//*[@id="app"]/div/div/div[4]/div/div/div[1]/div/div/div[2]/div[1]/button/span/text()'
COMPETITIONS_BUTTONS_XPATH = '//*[@id="app"]/div/div/div[4]/div/div/div[1]/div/div/div[2]/div[1]/button[{}]'
GAME_XPATH = '//*[@id="app"]/div/div/div[4]/div/div/div[1]/div/div/div/div[2]/div[{}]/div'


def to_utc(datetime_aest):
    """
    ["25 Sep, 13:30", " AEST"]
    :param starts:
    :return: utc version of the input datetime
    """

    from_zone = tz.gettz('Australia/Melbourne')
    to_zone = tz.gettz('UTC')

    aest = datetime.strptime(datetime_aest[0], '%d %b, %H:%M')

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    aest = aest.replace(tzinfo=from_zone)

    # Convert time zone
    datetime_utc = aest.astimezone(to_zone)

    return str(datetime.now().year) + str(datetime_utc)[4:] + " UTC"


def parse_games(dom, sport_category, index):
    games = []

    for game_match in dom.xpath(GAME_XPATH.format(index)):
        try:
            start = to_utc(game_match.xpath('div[1]/div[1]/a/text()'))
        except:
            start = ""

        try:
            game = game_match.xpath('div[1]/div[2]/a/text()')
        except:
            game = ""

        try:
            home = game_match.xpath('div[2]/div[1]/div[1]/span[2]/text()')
        except:
            home = ""

        try:
            away = game_match.xpath('div[2]/div[1]/div[2]/span[2]/text()')
        except:
            away = ""

        try:
            bet_straight_home = game_match.xpath('div[2]/div[2]/div[1]/div[2]/button[1]/span[2]/text()')
        except:
            bet_straight_home = ""

        try:
            bet_straight_away = game_match.xpath('div[2]/div[2]/div[1]/div[2]/button[2]/span[2]/text()')
        except:
            bet_straight_away = ""

        try:
            bet_line_handicap = game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[1]/span[2]/text()')
        except:
            bet_line_handicap = ""

        try:
            bet_line_home = game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[1]/span[3]/text()')
        except:
            bet_line_home = ""

        try:
            bet_line_away = game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[2]/span[3]/text()')
        except:
            bet_line_away = ""

        try:
            bet_score_over = game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[1]/span[2]/text()')
        except:
            bet_score_over = ""

        try:
            bet_score_home = game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[1]/span[3]/text()')
        except:
            bet_score_home = ""

        try:
            bet_score_away = game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[2]/span[3]/text()')
        except:
            bet_score_away = ""

        tmp_obj = {
            "starts": start,
            "game": game,
            "home": home,
            "away": away,
            "bet": {
                "straight": {
                    "home": bet_straight_home,
                    "away": bet_straight_away
                },
                "line": {
                    "handicap": bet_line_handicap,
                    "home": bet_line_home,
                    "away": bet_line_away
                },
                "total game score": {
                    "over": bet_score_over,
                    "home": bet_score_home,
                    "away": bet_score_away
                }
            }
        }
        # tmp_obj = {}
        # if sport_category == "australian-rules":
        #     if index == 1:
        #         tmp_obj = {
        #           "starts": game_match.xpath('div[1]/div[1]/a/text()'),
        #           "game": game_match.xpath('div[1]/div[2]/a/text()'),
        #           "home": game_match.xpath('div[2]/div[1]/div[1]/span[2]/text()'),
        #           "away": game_match.xpath('div[2]/div[1]/div[2]/span[2]/text()'),
        #           "bet": {
        #             "straight": {
        #               "home": game_match.xpath('div[2]/div[2]/div[1]/div[2]/button[1]/span[2]/text()'),
        #               "away": game_match.xpath('div[2]/div[2]/div[1]/div[2]/button[2]/span[2]/text()')
        #             },
        #             "line": {
        #               "handicap": game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[1]/span[2]/text()'),
        #               "home": game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[1]/span[3]/text()'),
        #               "away": game_match.xpath('div[2]/div[2]/div[2]/div[2]/button[2]/span[3]/text()')
        #             },
        #             "total game score": {
        #               "over": game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[1]/span[2]/text()'),
        #               "home": game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[1]/span[3]/text()'),
        #               "away": game_match.xpath('div[2]/div[2]/div[3]/div[2]/button[2]/span[3]/text()')
        #             }
        #           }
        #         }
        #
        #     else:
        #         tmp_obj = {
        #           "starts": game_match.xpath('div/div[1]/a/text()'),
        #           "game": game_match.xpath('div/div[2]/a/text()')
        #         }
        games.append(tmp_obj)

    return games


def selenium_webdriver(url, sport_category):
    """
    :param url: a url of a home page in william hill website
    :param sport_category: the name of the sport page will be scrapped
    :return: a list of Competitions
    """
    competitions = []

    driver = webdriver.Chrome(settings.get("SELENIUM_CHROME_DRIVER_PATH"))
    driver.get(url)
    # sleep some seconds to make sure js is done executing and webpage content is loaded
    sleep(1)
    current_page_dom = lxml.html.fromstring(driver.page_source)
    driver.close()
    # parsing current_page_dom
    index = 1
    for item in current_page_dom.xpath(COMPETITIONS_NAMES_XPATH):
        tmp_obj = {
            "name": item,
            "games": []
        }

        # GET GAMES
        competitions.append(tmp_obj)
        tmp_obj["games"] = parse_games(current_page_dom, sport_category, index)

        print("-------------------------------------------------------")
        print(tmp_obj)
        print("-------------------------------------------------------")
        index += 1

    return competitions


class WilliamhillSpiderSpider(scrapy.Spider):
    name = "williamhill_spider"
    allowed_domains = ["williamhill.com"]
    start_urls = ['https://www.williamhill.com.au']

    def parse(self, response):
        sports_urls = [x for x in response.xpath(SPORT_URL_XPATH).extract() if "/sports/" in x]
        result_json = {
            "sports": []
        }

        for url in sports_urls:
            sport_category = url.split("/")[-1]
            result_json["sports"].append(
                {
                    "name": sport_category,
                    "Competitions": selenium_webdriver(response.urljoin(url), sport_category)
                }
            )

        return result_json
