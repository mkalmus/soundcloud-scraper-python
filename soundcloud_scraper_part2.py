import requests
import json
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time

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

BASE_URL = 'https://soundcloud.com/charts'
CACHE_FILENAME = 'cache.json'

html = request_with_cache(BASE_URL)
soup = BeautifulSoup(html, "html.parser")

# Find all links
all_links = soup.find_all('a')
#print(all_links)

# Links to all genres (e.g. alternativerock, dancehall)
category_links = soup.find_all('a', href=re.compile("^(/charts/top)((?!all-).)*$"))
# print(category_links[0])

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
    return list(set(links))

def get_artist_stats(link):
    full_path = f"https://soundcloud.com{link['href']}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    r = requests.get(full_path, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        x = soup.find_all('script')[9].string.split('= ')[1].strip('][').split('{')[-4].split(',')
        stat_dict = {}
        for val in x[6:30]:
            kps = val.split(':')
            stat_dict[kps[0].strip('"')] = kps[1].strip('"')
        print(f"Success for {link['href']}")
        return stat_dict
    except:
        print(f"Issue with {link['href']}")

CHROMEDRIVER_PATH = "./chromedriver"
SCROLL_PAUSE_TIME = 2

scrollable_page_link = f"https://soundcloud.com{category_links[0]['href']}"
scrollable_page_html = get_source_scrollable(scrollable_page_link)
# print(type(scrollable_page_html))

top_tracks = get_top_track_links(scrollable_page_html)
# print(top_tracks[0])

artist_stats = get_artist_stats(top_tracks[0])
# print(artist_stats)