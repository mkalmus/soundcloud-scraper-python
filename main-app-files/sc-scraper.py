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

def make_genre_top_tracks_week(genre_selection):
    tracks_filtered = track_df[track_df['genre'] == genre_selection].sort_values(
        'weekly_views', ascending=False).head(3)

    graph_title = f'Top 3 Tracks for {genre_selection} (hover to see artist)'
    fig = px.bar(tracks_filtered, x="title", y="weekly_views", log_x=False,
                     hover_name="artist", hover_data=["title", "artist", "weekly_views"],
                     title=graph_title)

    fig.show()

    return tracks_filtered

def make_genre_top_tracks_all(genre_selection):
    tracks_filtered = track_df[track_df['genre'] == genre_selection].sort_values(
        'weekly_views', ascending=False).head(3)

    graph_title = f'Top 3 Tracks for {genre_selection} (hover to see artist)'
    fig = px.bar(tracks_filtered, x="title", y="all_views", log_x=False,
                     hover_name="artist", hover_data=["title", "artist", "weekly_views"],
                     title=graph_title)

    fig.show()

    return tracks_filtered

def make_top_3_radar(filtered_track_df, graph_title):
    categories = ['number of tracks','followers','top track views']
    artist_filtered = artist_df[artist_df['artist_name'].isin(tracks_filtered['artist'])]
    x = artist_filtered[['artist_numtracks', 'artist_followers', 'artist_toptrack_views']]
    y = artist_filtered[['artist_name']]

    basic_layout = go.Layout(title=graph_title)
    fig = go.Figure(layout=basic_layout)

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

def make_plotly_bar(xvals, yvals, graph_title):
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=graph_title)
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()

def intro():
    print("")
    print('-'*125)
    print("""Welcome to the Soundcloud scraper. This program allows the user to see information about popular genres, tracks, 
and artists on Soundcloud. All data is based off of the top 10 tracks for every genre. and, you can perform interactions where visualizations 
will be shown in your browser.""")
    print('-'*125)
    print("")

def step_one():
    global plot_names
    global plot_values
    print('-'*125)
    print('Step 1: Begin')
    print('-'*125)
    while True:
        print('If you would like to begin, enter 1; otherwise, type exit to exit the program (note: new graphs will open in new tabs)')
        choice_cont = input('Your choice: ')
        print("")

        if choice_cont == 'exit':
            sys.exit()

        if choice_cont == '1':
            step_two()

        else:
            print('Please enter a valid input (1 or exit) and try again.')
            print("")
            continue

def step_two():
    global plot_names
    global plot_values
    global weekly_or_all
    print('-'*125)
    print('Step 2: Choosing Views per Week or All Time Views')
    print('-'*125)
    while True:
        print(f"""For the next two graphs, would you like to sort by all time views or weekly views? If all time, type 1; if weekly, type 0.
Alternatively, type back to go back or exit to exit.""")
        weekly_or_all = input('Your choice: ')
        print("")

        if (weekly_or_all.lower() not in ['1', '0', 'exit', 'back']):
            print('Please enter a valid input (yes, no, exit, or back) and try again.')
            print("")

        if weekly_or_all.lower() == 'exit':
            sys.exit()

        if weekly_or_all.lower() == 'back':
            step_one()

        if weekly_or_all.lower() == '1':
            make_plotly_bar(genres_names_all, genres_values_all, 'Total Genre Streams for all Time')
            plot_names = genres_names_all
            plot_values = genres_values_all
            step_three()

        if weekly_or_all.lower() == '0':
            make_plotly_bar(genres_names_week, genres_values_week, 'Total Genre Streams per Week')
            plot_names = genres_names_week
            plot_values = genres_values_week
            step_three()

def step_three():
    global tracks_filtered
    global plot2_name
    print('-'*125)
    print('Step 3: Looking into a Specific Genre')
    print('-'*125)
    while True:
        print(f"""Now you can look into a specific genre. To see top tracks for your desigred genre, type a selection from 1-10 corresponding to the graph 
in your browser and the genre you want to see. Alternatively, type back to go back or exit to exit.""")
        genre_input = input('Your choice: ')
        print("")

        if genre_input == 'exit':
            sys.exit()

        if genre_input not in ['exit', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'back']:
            print('Please enter a valid input (integer between 1 and 10 or exit) and try again.')
            print("")

        if genre_input == 'back':
            step_two()

        else:
            plot2_name = plot_names[int(genre_input)-1]
            print(f"The genre you selected was {plot2_name}.")
            print("")
            if weekly_or_all.lower() == '1':
                tracks_filtered = make_genre_top_tracks_all(plot2_name)
            if weekly_or_all.lower() == '0':
                tracks_filtered = make_genre_top_tracks_week(plot2_name)
            step_four()

def step_four():
    print('-'*125)
    print('Step 4: Artist Info for Selected Genre')
    print('-'*125)
    while True:
        print("Now you can look into the artists of these songs (to see the artist, hover over any bar).") 
        print("")
        print(f"""Type 1 if you'd like to see artist information as a radar chart. Alternatively, type back 
to go back or exit to exit.""")
        graph_type = input('Your choice: ')
        print("")

        if graph_type == 'exit':
            sys.exit()
        if graph_type not in ['1', 'exit']:
            print('Please enter a valid input (1 or exit) and try again.')
            print("")
        if graph_type == 'back':
            step_three()
        if graph_type == '1':
            graph_title = f'Radar Plot for {plot2_name} Artists'
            make_top_3_radar(tracks_filtered, graph_title)
            print('Thanks for using the Soundcloud scraper. Please consider contributing to the code on GitHub!')
            print("")
            sys.exit()

def main():
    intro()
    step_one()
    step_two()
    step_three()
    step_four()

main()


