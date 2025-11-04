# Run get_data.py first to download all data from the website and save to local CSVs
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
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

# how many questions to teams get right in final chase, grouped by numbers of players in FC
counts = episodes.groupby(['players_in_final_chase', 'target'])['episode'].agg('count').reset_index()
counts.rename(columns={'episode': 'count'}, inplace=True)

# calculate the average for each team size
avg_target = episodes.groupby('players_in_final_chase')['target'].agg('mean').reset_index()
print(avg_target)

plt.figure()
plt.scatter(counts['players_in_final_chase'], counts['target'], alpha=0.5, s=counts['count'])
plt.grid(True, linestyle='--')
plt.title('Final Chase Target by # players in Final Chase')
plt.xlabel('Number of Players in Final Chase')
plt.xticks(range(5))
plt.ylabel('Final Chase Target (questions)')
plt.yticks(range(0, 31, 2))
plt.savefig('final_chase_correct_by_team_size.png')

# What are the win rates and average earnings for teams with:
# all players going down the middle
# 1 player going high
# one player going low
count_high_offers = players.loc[players['chosen_offer'] == 1].groupby('episode')['chosen_offer'].agg('count')
count_low_offers = players.loc[players['chosen_offer'] == -1].groupby('episode')['chosen_offer'].agg('count')

episodes = episodes.merge(count_high_offers.rename('num_high_offers'), left_on='episode', right_index=True, how='left')
episodes = episodes.merge(count_low_offers.rename('num_low_offers'), left_on='episode', right_index=True, how='left')
episodes['num_high_offers'] = episodes['num_high_offers'].fillna(0).astype(int)
episodes['num_low_offers'] = episodes['num_low_offers'].fillna(0).astype(int)
episodes['num_mid_offers'] = 4 - episodes['num_high_offers'] - episodes['num_low_offers']

# for every combination of team make up - what is the FC win rate and FC prize pot?
fc_summary = episodes.groupby(['num_low_offers', 'num_mid_offers', 'num_high_offers']).agg(
    episodes=('episode', 'count'),
    win_pc=('team_win', 'mean'),
    avg_prize_fund=('prize_fund', 'mean'),
).reset_index()
fc_summary['win_pc'] = fc_summary['win_pc'] * 100
fc_summary['avg_prize_fund'] = fc_summary['avg_prize_fund'] / 1000
fc_summary.sort_values(by='episodes', ascending=False, inplace=True)

plt.figure()
plt.title('Final Chase Win % by Team Offer Composition')
plt.xlabel('Win %')
plt.xticks(range(0, 101, 10))
plt.ylabel('Average Prize Fund (£k)')
plt.yticks(range(0, 41, 5))
plt.grid(True, linestyle='--')

# color based on the number of players going high
# bias from -4 (all low) to +4 (all high)
fc_summary['bias'] = fc_summary['num_high_offers'] - fc_summary['num_low_offers']

# create a 3-stop colormap: red @ -4, green @ 0, blue @ +4
cmap = LinearSegmentedColormap.from_list('red_green_blue', ['red', 'green', 'blue'])
norm = mpl.colors.Normalize(vmin=-4, vmax=4)

# map bias to RGBA colors
colors = cmap(norm(fc_summary['bias'].values))

# plot using bias values with the correct colormap and add a colorbar
plt.scatter(fc_summary['win_pc'], fc_summary['avg_prize_fund'], s=fc_summary['episodes'], c=fc_summary['bias'], cmap=cmap)
mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
mappable.set_array(fc_summary['bias'].values)
cb = plt.colorbar(mappable, ticks=[-4, -2, 0, 2, 4], cax=plt.gca().inset_axes([1.05, 0.1, 0.03, 0.8]))
cb.set_label('High offers - Low offers')

plt.savefig('final_chase_win_percentage_by_team_offer_composition.png')

breakpoint()
