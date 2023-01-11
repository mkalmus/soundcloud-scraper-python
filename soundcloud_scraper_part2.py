import requests
import json
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time

# PART 1 FUNCTIONS
def open_cache():
    '''
    - Opens the cache based on CACHE_FILENAME and returns cache as dictionary
    - If the cache file doesn't exist, returns an empty dict

    Parameters
    ----------
    None

    Returns
    -------
    cache_dict (dict): all cached data as a dict
        - keys are urls and values are the full HTML of the urls
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}

    return cache_dict

def save_cache(cache_dict):
    '''
    - Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict (dict): dictionary to write to disk
    '''
    dumped_json_cache = json.dumps(cache_dict, indent=2)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()
    return None

def request_with_cache(url):
    cache_dict = open_cache()
    if url in cache_dict.keys():
        print('Fetching from cache...')
        return cache_dict[url]
    else:
        print('Fetching new data...')
        r = requests.get(url)
        html = r.text
        cache_dict[url] = html
        save_cache(cache_dict)
        return html

def get_top_track_links(html):
    soup = BeautifulSoup(html, "html.parser")
    # Links to top artists in genres
    links = soup.find('div', {'class': 'chartTracks'}).find_all('a', href=re.compile('^/[^/]*$'))
    return list(set(links))

# PART 2 FUNCTIONS
def get_source_scrollable(url):
    """
    Gets the page source for a site that requires multiple scrolls but has a finite end
    """
    CACHE_DICT = open_cache()
    if url in CACHE_DICT.keys():
        print('Fetching from cache...')
        return CACHE_DICT[url]
    else:
        print('Making new headless browser')
        # Setup headless chromedriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # In Selenium 4, using ChromeService gets rid of deprecation warning when directly passing path
        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source
        CACHE_DICT[url] = html
        driver.close()
        save_cache(CACHE_DICT)
        return html

def get_top_track_links(html):
    """
    Inputs:
        html (str) : html for the top charts of a given genre on Soundcloud (i.e. html for https://soundcloud.com/charts/top?genre=reggaeton)
    Outputs:
        links (list) : unique track links
    """
    soup = BeautifulSoup(html, "html.parser")
    # Links to top tracks in genre
    links = soup.find('div', {'class': 'chartTracks'}).find_all('a', href=re.compile('^/[^/]*$'))
    return links

BASE_URL = 'https://soundcloud.com/charts'
CACHE_FILENAME = 'cache.json'

html = request_with_cache(BASE_URL)
soup = BeautifulSoup(html, "html.parser")
# Links to all genres (e.g. alternativerock, dancehall)
# Example: <a href="/charts/top?genre=alternativerock">Alternative Rock</a>
category_links = soup.find_all('a', href=re.compile("^(/charts/top)((?!all-).)*$"))
print(f"Category Link: {category_links[0]}")

# BEGIN PART 2

CHROMEDRIVER_PATH = "./chromedriver"
SCROLL_PAUSE_TIME = 2

# Get HTML source of category link like https://soundcloud.com/charts/top?genre=alternativerock
scrollable_page_html = get_source_scrollable(f"https://soundcloud.com{category_links[0]['href']}")

# Given HTML of a category page, get links to artists
artist_links = get_top_track_links(scrollable_page_html)
print(f"Artist Link: {artist_links[0]}")
