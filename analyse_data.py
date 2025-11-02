# Run get_data.py first to download all data from the website and save to local CSVs
import pandas as pd
import matplotlib.pyplot as plt


players = pd.read_csv('players.csv')
episodes = pd.read_csv('episodes.csv')

# work out some supplementary info - aggregate data for episodes (let's not scrape it, we should have everything we need in here no?)
players['won_hth'] = players['hth_winner'] == 'PLAYER'

# question 0: What is the average cashbuilder score?
cash_builder = players['cash_builder'].value_counts().sort_index()
max_count = cash_builder.values.max()
plt.figure()
plt.title('Cash Builder Score Distribution')
plt.xlabel('Cash Builder Score (£k)')
plt.xticks(range(0, 15, 1))
plt.ylabel('Number of Players')
plt.yticks(range(0, max_count + 1, 100))

bars = plt.bar(cash_builder.index / 1000, cash_builder.values, width=0.9)
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, h + max_count * 0.01, f'{int(h):,}', ha='center', va='bottom', fontsize=8)

plt.savefig('cashbuilder_distribution.png')


# Question 0.5: how does cashbuilder score correlate with high / low offers?
config = {
    'lower_offer': {
        'title': 'Lower Offer Value',
        'ymin': -20,
        'ymax': 11,
        'ygap': 2,
    },
    # 'cash_builder': {
    #     'title': 'Cash Builder Score',
    #     'ymax': 130_000,
    # },
    'higher_offer': {
        'title': 'Higher Offer Value',
        'ymin': 0,
        'ymax': 131,
        'ygap': 10,
    },
}
for column in config:
    plt.figure()
    for label, data in players.groupby('player_number'):
        # stagger the x-values based on player number. 1 = -0.5, 4 = +0.5
        x_offset = (label - 2.5) * 0.15
        x = data['cash_builder'] / 1000 + x_offset
        plt.scatter(x, data[column] / 1000, alpha=0.25, label=f'Player {label}', s=5)

    plt.title(f'Cash Builder vs {config[column]["title"]}')
    plt.xlabel('Cash Builder Score (£k)')
    plt.xticks(range(15))
    plt.ylabel(f'{config[column]["title"]} (£k)')
    plt.yticks(range(config[column]['ymin'], config[column]['ymax'], config[column]['ygap']))
    plt.grid(True, linestyle='--')
    plt.legend()
    plt.savefig(f'cashbuilder_vs_{column}.png')

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
episodes['team_win'] = episodes['winner'] == 'TEAM'
win_pcs = episodes.groupby('players_in_final_chase')['team_win'].agg(['count', 'mean'])

plt.figure()
plt.title('Win % by # players in Final Chase')
plt.xlabel('Number of Players')
plt.xticks(range(5))
plt.ylabel('Winning Percentage (%)')
plt.yticks(range(0, 51, 5))
plt.ylim([0, 50])
plt.grid(True, linestyle='--')

plt.bar(win_pcs.index, win_pcs['mean'] * 100, width=0.5)

plt.savefig('winning_percentages_by_final_chase.png')
