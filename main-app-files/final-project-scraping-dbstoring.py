from selenium import webdriver
import requests
import json
from bs4 import BeautifulSoup
import time
import sys
import pandas as pd
import numpy as np
import sqlite3

BASE_URL = 'https://soundcloud.com'
CACHE_FILENAME = 'sc_cache.json'
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
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
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict, indent=2)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def cache_page_with_genres(url):

    CACHE_DICT = open_cache()
    if url in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[url]

    else:
        print("Fetching")
        browser = webdriver.Chrome("/Users/michael/Downloads/chromedriver")
        browser.get(url)
        time.sleep(3)
        xpath = '/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div[2]/div/div[2]/div[4]/button'
        browser.find_element_by_xpath(xpath).click()
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        page_source = browser.page_source
        CACHE_DICT[url] = page_source
        save_cache(CACHE_DICT)
        browser.close()
        return CACHE_DICT[url]

def get_tracks_for_genre(bsObj):
    all_tracks = {}
    reggae_source = bsObj
    all_titles = reggae_source.find_all('li', class_="chartTracks__item")

    for i, track in enumerate(all_titles):
        details = track.find('div', class_='chartTrack__details')
        
        try:
            track_title = details.find('div', class_='chartTrack__title').text.strip()
        except:
            try: 
                track_title = details.find('div', class_='chartTrack__blockedTitle').text.strip()
            except:
                track_title = np.NaN

        try:
            end_url = details.find('div', class_='chartTrack__title').find('a')['href']
            track_url = BASE_URL + end_url
        except:
            track_url = np.NaN

        track_artist = details.find('div', class_='chartTrack__username').text.strip()
        artist_url_end = details.find('div', class_='chartTrack__username').find('a')['href']
        artist_url_full = 'https://soundcloud.com' + artist_url_end
        
        
        all_plays = track.find(
            'div', class_='chartTrack__score').find(
                'div', class_='sc-ministats')

        try:
            track_views_week = all_plays.find(
                'span', class_='chartTrack__scoreWeekPlays').find(
                    'span', class_='sc-visuallyhidden').text
        except:
            track_views_week = np.NaN

        try:
            track_views_all = all_plays.find(
                'span', class_='chartTrack__scoreAllPlays').find(
                    'span', class_='sc-visuallyhidden').text
        except:
            track_views_all = np.NaN

        all_tracks[i+1] = {
            'title': track_title,
            'url': track_url,
            'artist': track_artist,
            'weekly_views': track_views_week,
            'all_views': track_views_all,
            'artist_url': artist_url_full
        }

    return all_tracks

def build_genre_url_dict():
    genre_dict = {}
    url = 'https://soundcloud.com/charts/top?genre=reggae&country=US'
    reggae_source = BeautifulSoup(cache_page_with_genres(url), 'html.parser')

    all_genres = reggae_source.find_all('a', class_="linkMenu__link")
    for genre in all_genres:
        if (genre.text == 'All music genres') or (genre.text == 'All audio genres'):
            continue
        else:
            genre_dict[genre.text] = BASE_URL + genre['href']

    return genre_dict

genre_dict = build_genre_url_dict()

final_df = pd.DataFrame(
    columns=['genre', 'title', 'url', 
             'artist', 'weekly_views', 'all_views'])

for genre_name, genre_link in genre_dict.items():
    genre_source = BeautifulSoup(cache_page_with_genres(url=genre_link), 'html.parser')
    genre_tracks = get_tracks_for_genre(genre_source)
    
    genre_df = pd.DataFrame.from_dict(genre_tracks, orient='index')
    genre_df['genre'] = genre_name
    
    genre_top_10 = genre_df[0:10]
    final_df = pd.concat([final_df, genre_top_10], axis=0)

final_df = final_df.astype({
    'weekly_views': 'float',
    'all_views': 'float'
})
final_df = final_df.reset_index()
all_artist_urls = list(final_df['artist_url'])

def cache_artist_page(artist_url):

    url = artist_url + '/popular-tracks'
    CACHE_DICT = open_cache()
    if url in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[url]

    else:
        print("Fetching")
        browser = webdriver.Chrome("/Users/michael/Downloads/chromedriver")
        browser.get(url)
        time.sleep(3)

        page_source = browser.page_source
        CACHE_DICT[url] = page_source
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

def get_artist_info(artist_url_list):
    '''
    Parameters
    -----------
    artist_url: The URL to an artist page. The function uses 
    cache_artist_page to retrieve the HTML then creates BS 
    object from HTML text of artist page.

    '''

    all_artists = {}

    for i, artist_url in enumerate(artist_url_list):

        artist_source = BeautifulSoup(
        cache_artist_page(artist_url), 'html.parser')

        try:
            artist_name = artist_source.find(
            'span', class_='soundTitle__usernameText').text.strip()

            top_track_name = artist_source.find(
            'a', class_='soundTitle__title').text.strip()

            top_track_views = artist_source.find(
            'span', class_='sc-ministats-plays').find(
            'span', class_='sc-visuallyhidden').text.strip().split(' ')[0]

            all_tables = artist_source.find_all('td')

            artist_followers = all_tables[0].find(
                'a')['title'].strip().split(' ')[0]

            artist_tracks = all_tables[2].find(
                'a')['title'].strip().split(' ')[0]


            all_artists[i+1] = {
                'artist_name': artist_name,
                'artist_url': artist_url,
                'artist_toptrack': top_track_name,
                'artist_toptrack_views': top_track_views,
                'artist_followers': artist_followers,
                'artist_numtracks': artist_tracks
            }
        except:
            artist_url = artist_url
            artist_name = np.NaN
            top_track_name = np.NaN
            top_track_views = np.NaN
            artist_followers = np.NaN
            artist_tracks = np.NaN

            all_artists[i+1] = {
            'artist_name': artist_name,
            'artist_url': artist_url,
            'artist_toptrack': top_track_name,
            'artist_toptrack_views': top_track_views,
            'artist_followers': artist_followers,
            'artist_numtracks': artist_tracks}

    return all_artists

all_artist_info = get_artist_info(all_artist_urls)
artist_df = pd.DataFrame.from_dict(all_artist_info, orient='index')
artist_df = artist_df.reset_index()

artist_df = artist_df.rename(columns={'index': 'id'})
final_df = final_df.drop('index', axis=1).reset_index()
final_df = final_df.rename(columns={'index': 'id'})


conn = sqlite3.connect('soundcloud_data.db')
c = conn.cursor()

query_artists = '''
CREATE TABLE IF NOT EXISTS soundcloud_artists(
    id integer,
    artist_name text,
    artist_url text PRIMARY KEY,
    artist_toptrack text,
    artist_toptrack_views REAL,
    artist_followers REAL,
    artist_numtracks REAL)
'''
c.execute(query_artists)

query_tracks = '''
CREATE TABLE IF NOT EXISTS soundcloud_tracks (
    id integer PRIMARY KEY,
    track_genre text,
    track_title text,
    track_url text,
    track_artist text,
    track_views_week REAL,
    track_views_all REAL,
    track_artist_url text, 
    FOREIGN KEY (track_artist_url) REFERENCES soundcloud_artists (artist_url)
);
'''
c.execute(query_tracks)

artist_df.to_sql('soundcloud_artists', conn, if_exists='replace', index=False)
final_df.to_sql('soundcloud_tracks', conn, if_exists='replace', index=False)

conn.close()


# def save_cache_with_name(cache_dict, cache_filename):
#     dumped_json_cache = json.dumps(cache_dict, indent=2)
#     fw = open(cache_filename,"w")
#     fw.write(dumped_json_cache)
#     fw.close()

# def open_cache_with_name(cache_filename):
#     try:
#         cache_file = open(cache_filename, 'r')
#         cache_contents = cache_file.read()
#         cache_dict = json.loads(cache_contents)
#         cache_file.close()
#     except:
#         cache_dict = {}

#     return cache_dict

# cache_full = open_cache()
# cache_half1 = dict(list(cache_full.items())[len(cache_full)//2:])
# cache_half2 = dict(list(cache_full.items())[:len(cache_full)//2])

# save_cache_with_name(cache_half1, 'cache_half1.json')
# save_cache_with_name(cache_half2, 'cache_half2.json')

# cache_half1 = open_cache_with_name('cache_half1.json')
# cache_half2 = open_cache_with_name('cache_half2.json')

# cache_half1.update(cache_half2)
# save_cache_with_name(cache_half1, 'sc_cache.json')






