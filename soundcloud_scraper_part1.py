import requests
import json
from bs4 import BeautifulSoup
import re

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
print(category_links)