# Run get_data.py first to download all data from the website and save to local CSVs
import pandas as pd

players = pd.read_csv('players.csv')
episodes = pd.read_csv('episodes.csv')

# work out some supplementary info - aggregate data for episodes (let's not scrape it, we should have everything we need in here no?)

# Question 1: what are the get-home percentages for the lower / higher offers?
higher = players.loc[players['chosen_offer'] == 1]
higher_won_hth = higher.loc[higher['hth_winner'] == 'PLAYER']
higher_win_pc = len(higher_won_hth) / len(higher) * 100
# 48.4%

mid = players.loc[players['chosen_offer'] == 0]
mid_won_hth = mid.loc[mid['hth_winner'] == 'PLAYER']
mid_win_pc = len(mid_won_hth) / len(mid) * 100
# 61.7%

lower = players.loc[players['chosen_offer'] == -1]
lower_won_hth = lower.loc[lower['hth_winner'] == 'PLAYER']
lower_win_pc = len(lower_won_hth) / len(lower) * 100
# 72.8%

# Is win % proportional to what you scored in the cash-builder?


# Question 2: What are the odds of winning with an N-person team?
