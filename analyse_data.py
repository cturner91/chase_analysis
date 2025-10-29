# Run get_data.py first to download all data from the website and save to local CSVs
import pandas as pd
import matplotlib.pyplot as plt


players = pd.read_csv('players.csv')
episodes = pd.read_csv('episodes.csv')

# work out some supplementary info - aggregate data for episodes (let's not scrape it, we should have everything we need in here no?)
players['won_hth'] = players['hth_winner'] == 'PLAYER'

# Question 1: what are the get-home percentages for the lower / higher offers?
higher = players.loc[players['chosen_offer'] == 1]
higher_win_pc = higher['won_hth'].mean() * 100
# 48.4%

mid = players.loc[players['chosen_offer'] == 0]
mid_win_pc = mid['won_hth'].mean() * 100
# 61.7%

lower = players.loc[players['chosen_offer'] == -1]
lower_win_pc = lower['won_hth'].mean() * 100
# 72.8%

# Is win % proportional to what you scored in the cash-builder?
all_players_ratios = players.groupby('cash_builder')['won_hth'].agg(['count', 'mean'])
higher_ratios = higher.groupby('cash_builder')['won_hth'].agg(['count', 'mean'])
mid_ratios = mid.groupby('cash_builder')['won_hth'].agg(['count', 'mean'])
lower_ratios = lower.groupby('cash_builder')['won_hth'].agg(['count', 'mean'])

# filter by min 5 players
min_players = 5
all_players_ratios = all_players_ratios[all_players_ratios['count'] >= min_players]
higher_ratios = higher_ratios[higher_ratios['count'] >= min_players]
mid_ratios = mid_ratios[mid_ratios['count'] >= min_players]
lower_ratios = lower_ratios[lower_ratios['count'] >= min_players]

plt.figure()
plt.title('Head-to-head win % by Cash Builder')
plt.xlabel('Cash Builder (£k)')
plt.xticks(range(13))
plt.ylabel('Winning Percentage (%)')
plt.yticks(range(0, 101, 10))
plt.grid(True, linestyle='--')

plt.plot(all_players_ratios.index/1000, all_players_ratios['mean'] * 100, label=f'All Players ({len(players):,} players)')
plt.plot(higher_ratios.index/1000, higher_ratios['mean'] * 100, label=f'Higher Offer ({len(higher):,} players)')
plt.plot(mid_ratios.index/1000, mid_ratios['mean'] * 100, label=f'Mid Offer ({len(mid):,} players)')
plt.plot(lower_ratios.index/1000, lower_ratios['mean'] * 100, label=f'Lower Offer ({len(lower):,} players)')

plt.legend()
plt.savefig('winning_percentages_by_cash_builder.png')


# Question 2: What are the odds of winning with an N-person team?
