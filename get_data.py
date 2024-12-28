from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from classes import Player

players = []
for series in range(1, 18):
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
df.to_csv('data.csv', index=False)
