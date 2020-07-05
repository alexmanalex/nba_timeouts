import pandas as pd
import numpy as np

OUTPUT_COLS = ['game_id', 'date', 'period',
                'team_id', 'elapsed_seconds', 'elapsed_seconds_quarter', 'point_diff',
                'past_point_diff', 'future_point_diff', 'time_since_last_break']

#read in data
df = pd.read_csv('2018-2019_NBA_PBP/pbp-[10-16-2018]-[06-13-2019]-combined-stats.csv',
                  # nrows=100000,
                  encoding = "ISO-8859-1",   low_memory=False).drop(0, axis=0)
df['elapsed_seconds_quarter'] = df['elapsed'].str.split(':').apply(lambda x: int(x[1]) * 60 + int(x[2]))
df['elapsed_seconds'] = df['elapsed_seconds_quarter'] + (df['period']-1)*12*60
df['game_id'] = df.apply(lambda row: row.game_id[1:], axis=1).astype(int)

team_lookup = pd.read_csv('2018-2019_NBA_Historical_Schedule/TEAMS-Table 1.csv')
team_lookup['INITIALS'] = team_lookup['INITIALS'].str.lower().astype(str)

# Create nontimeouts
team_map = ['away', 'home']
lis = []
for _ in range(len(df)):
    lis.append(team_map[int(np.round(np.random.rand()))])
which_team = pd.Series(lis)
df['which_team'] = which_team

df['point_diff'] = df.apply(lambda row: row['away_score'] - row['home_score'] if row.which_team == 'away' else row['home_score'] - row['away_score'], axis=1)
df.sort_values(by='elapsed_seconds', ascending=True, inplace=True)

df_past = df.copy()
df_past['elapsed_seconds'] = df_past['elapsed_seconds'] + 3*60
df_past = df_past[['game_id', 'which_team', 'elapsed_seconds', 'point_diff']]
df_past = df_past.rename(columns={'point_diff': 'past_point_diff'})

df_future = df.copy()
df_future['elapsed_seconds'] = df_future['elapsed_seconds'] - 3*60
df_future = df_future[['game_id', 'which_team', 'elapsed_seconds', 'point_diff']]
df_future = df_future.rename(columns={'point_diff': 'future_point_diff'})

df = pd.merge_asof(df, df_past, on='elapsed_seconds', by=['game_id', 'which_team'], direction='backward')
df = pd.merge_asof(df, df_future, on='elapsed_seconds', by=['game_id', 'which_team'], direction='backward')

nontimeouts = df[df.event_type !='timeout']
nontimeouts = nontimeouts.sample(n=300000) #n = approximate number of timeouts in season


#Prepare nontimeouts
nontimeouts = nontimeouts[nontimeouts.team.notnull()]
nontimeouts['INITIALS'] = nontimeouts['team'].str.lower()
nontimeouts = nontimeouts.merge(team_lookup, on=['INITIALS'], how='left').rename(columns={'SHORT NAME': 'team_id'})


#Time since last break
game_break_event_names = ['start of period', 'timeout', 'end of period']
game_breaks = df[df.event_type.isin(game_break_event_names)]
game_breaks['elapsed_seconds'] = game_breaks['elapsed_seconds'] + 1 #avoid the current timeout
game_breaks['last_break_time'] = game_breaks['elapsed_seconds'] - 1
game_breaks = game_breaks[['elapsed_seconds', 'game_id', 'last_break_time']]
nontimeouts.sort_values(by='elapsed_seconds', ascending=True, inplace=True)
game_breaks.sort_values(by='elapsed_seconds', ascending=True, inplace=True)
nontimeouts = pd.merge_asof(nontimeouts, game_breaks, on='elapsed_seconds', by=['game_id'], direction='backward')
nontimeouts['time_since_last_break'] = nontimeouts['elapsed_seconds'] - nontimeouts['last_break_time']



nontimeouts = nontimeouts[OUTPUT_COLS].dropna(subset=['team_id'])
nontimeouts['treatment'] = 0
nontimeouts.to_csv('output/nontimeouts_raw.csv')
