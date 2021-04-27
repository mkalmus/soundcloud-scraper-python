import plotly
import plotly.graph_objs as gobjs
import plotly.express as px
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

conn = sqlite3.connect('soundcloud_data.db')
c = conn.cursor()
artist_df = pd.read_sql_query("SELECT * from soundcloud_artists", conn)
track_df = pd.read_sql_query("SELECT * from soundcloud_tracks", conn)
conn.close()

genre_group_weekly = (track_df.groupby(
    'genre'))[['weekly_views', 'all_views']].sum().sort_values(
    'weekly_views', ascending=False).head(10)

genre_group_all = (track_df.groupby(
    'genre'))[['weekly_views', 'all_views']].sum().sort_values(
    'all_views', ascending=False).head(10)

genres_names_week = genre_group_weekly.index.values
genres_values_week = genre_group_weekly['weekly_views']

genres_names_all = genre_group_all.index.values
genres_values_all = genre_group_all['all_views']

def make_genre_top_tracks(genre_selection):
    tracks_filtered = track_df[track_df['genre'] == genre_selection].sort_values(
        'weekly_views', ascending=False).head(3)

    fig = px.bar(tracks_filtered, x="title", y="weekly_views", log_x=False,
                     hover_name="artist", hover_data=["title", "artist", "weekly_views"])

    fig.show()

    return tracks_filtered

def make_top_3_radar(filtered_track_df):
    categories = ['number of tracks','followers','top track views']
    artist_filtered = artist_df[artist_df['artist_name'].isin(tracks_filtered['artist'])]
    x = artist_filtered[['artist_numtracks', 'artist_followers', 'artist_toptrack_views']]
    y = artist_filtered[['artist_name']]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
          r=list(x.iloc[0].values),
          theta=categories,
          fill='toself',
          name=str(y.iloc[0].values),
    ))
    fig.add_trace(go.Scatterpolar(
          r=list(x.iloc[1].values),
          theta=categories,
          fill='toself',
          name=str(y.iloc[1].values)
    ))


    fig.add_trace(go.Scatterpolar(
          r=list(x.iloc[2].values),
          theta=categories,
          fill='toself',
          name=str(y.iloc[2].values)
    ))

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
        )),
      showlegend=True
    )

    fig.show()

def make_plotly_bar(xvals, yvals):
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Bar Graph")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()

print("")
print('-'*150)
print("""Welcome to the Soundcloud scraper. This program allows the user to see information about popular genres, tracks, and artists on Soundcloud.
All data is based off of the top 10 tracks for every genre. First, you will be presented with the top genres this week by track plays. 
Then, you can perform interactions where visualizations will be shown in your browser.""")
print('-'*150)
print("")

while True:
    print('If you would like to begin, enter 1; otherwise, type exit to exit the program (note: new graphs will open in new tabs)')
    choice_cont = input('Your choice: ')
    print("")

    if choice_cont == 'exit':
        sys.exit()

    if choice_cont == '1':
        make_plotly_bar(genres_names_week, genres_values_week)
        plot_names = genres_names_week
        plot_values = genres_values_week

        while True:
            print(f"This graph is sorted by weekly views. Would you like to sort by all time views instead? If yes, type yes; if no, type no. Or, type exit to exit.")
            weekly_or_all = input('Your choice: ')
            print("")

            if (weekly_or_all.lower() not in ['yes', 'no', 'exit']):
                print('Please enter a valid input (yes, no, or exit) and try again.')
                print("")

            else:
                break

        if weekly_or_all.lower() == 'exit':
            sys.exit()

        if weekly_or_all.lower() == 'yes':
            make_plotly_bar(genres_names_all, genres_values_all)
            plot_names = genres_names_all
            plot_values = genres_values_all

        while True:
            print(f"Now you can look into a specific genre. To see top tracks for your desigred genre, type a selection from 1-10 corresponding to the graph in your browser and the genre you want to see. Or, type exit to exit.")
            genre_input = input('Your choice: ')
            print("")

            if genre_input == 'exit':
                sys.exit()

            if genre_input not in ['exit', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                print('Please enter a valid input (integer between 1 and 10 or exit) and try again.')
                print("")

            else:
                break

        plot2_name = plot_names[int(genre_input)-1]
        print(f"The genre you selected was {plot2_name}.")
        print("")
        tracks_filtered = make_genre_top_tracks(plot2_name)


        while True:
            print("Now you can look into the artists of these songs (to see the artist, hover over any bar).") 
            print("Type 1 if you'd like to see artist information as a radar chart, or type exit to exit.")
            graph_type = input('Your choice: ')
            print("")

            if graph_type == 'exit':
                sys.exit()

            if graph_type not in ['1', 'exit']:
                print('Please enter a valid input (1 or exit) and try again.')
                print("")
            else:
                break

        if graph_type == '1':
            make_top_3_radar(tracks_filtered)

        print('Thanks for using the Soundcloud scraper. Please consider contributing to the code on GitHub!')
        sys.exit()

    else:
        print('Please enter a valid input and try again.')
        print("")



