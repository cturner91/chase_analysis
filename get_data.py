from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from classes import Player, Episode


SERIES = range(1, 18)


def extract_players():
    players = []
    for series in SERIES:
        response = requests.get(f'https://onequestionshootout.xyz/players/series_{series}.htm')
        if response.status_code != 200:
            raise ValueError(f'Could not get data for series: {series}')

        soup = BeautifulSoup(response.content, features='html.parser')
        rows = soup.find_all('tr')[4:]

        prev_dt, episode = None, 1
        for row in rows:
            player_data = Player.from_html(str(row))

            if prev_dt is not None and player_data.date != prev_dt:
                episode += 1

            player_data.series = series
            player_data.episode = episode
            prev_dt = player_data.date

            players.append(player_data)

    df = pd.DataFrame(players)
    df.to_csv('players.csv', index=False)


def extract_episodes():
    episodes = []
    for series in SERIES:
        response = requests.get(f'https://onequestionshootout.xyz/episodes/series_{series}.htm')
        if response.status_code != 200:
            raise ValueError(f'Could not get data for series: {series}')

        soup = BeautifulSoup(response.content, features='html.parser')
        rows = soup.find_all('tr')[4:]

        for i, row in enumerate(rows):
            episode = i + 1
            episode_data = Episode.from_html(str(row))
 
            episode_data.series = series
            episode_data.episode = episode

            episodes.append(episode_data)

    df = pd.DataFrame(episodes)
    df.to_csv('episodes.csv', index=False)


if __name__ == '__main__':
    extract_players()
    extract_episodes()
