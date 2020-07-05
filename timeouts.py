import pandas as pd

OUTPUT_COLS = ['game_id', 'date', 'period',
                'team_id', 'elapsed_seconds', 'elapsed_seconds_quarter', 'point_diff',
                'past_point_diff', 'future_point_diff', 'time_since_last_break']


team_lookup = pd.read_csv('2018-2019_NBA_Historical_Schedule/TEAMS-Table 1.csv')
team_lookup['NICKNAME'] = team_lookup['NICKNAME'].str.lower()#.astype(str)
team_lookup['INITIALS'] = team_lookup['INITIALS'].str.lower()#.astype(str)

#read in data
df = pd.read_csv('2018-2019_NBA_PBP/pbp-[10-16-2018]-[06-13-2019]-combined-stats.csv',
                  # nrows = 10000,
                  encoding = "ISO-8859-1", low_memory=False).drop(0, axis=0)

df['game_id'] = df.apply(lambda row: row.game_id[1:], axis=1).astype(int)
df['INITIALS'] = df['team'].str.lower()
df['elapsed_seconds_quarter'] = df['elapsed'].str.split(':').apply(lambda x: int(x[1]) * 60 + int(x[2]))
df['elapsed_seconds'] = df['elapsed_seconds_quarter'] + (df['period'] - 1)*12*60
df.sort_values(by='elapsed_seconds', ascending=True, inplace=True)

schedule = pd.read_csv('2018-2019_NBA_Historical_Schedule/NBA-2018-19-HISTORICAL-SCHEDULE-Table 1.csv')
schedule['game_id'] = schedule['GAME ID']

# Prepare timeouts
timeouts = df[(df.event_type=='timeout') & (df.type.isin([' timeout: regular', ' timeout: short']))]
timeouts['NICKNAME'] = timeouts.apply(lambda row: row.description.split()[0].lower(), axis=1).astype(str)
timeouts['minute'] = timeouts['elapsed'].str.split(':').apply(lambda x: int(x[1]))
timeouts = timeouts.merge(team_lookup, on=['NICKNAME'], how='left').rename(columns={'SHORT NAME': 'team_id'})
timeouts = timeouts.merge(schedule[['ROAD TEAM', 'HOME TEAM', 'game_id']], on=['game_id'], how='left')
timeouts['point_diff'] = timeouts.apply(lambda row: row['away_score'] - row['home_score'] if row['ROAD TEAM'] == row['team_id'] else row['home_score'] - row['away_score'], axis=1)
timeouts['is_home_team'] = timeouts['ROAD TEAM'] == timeouts['INITIALS_x']

# Add past and future point differential
df = df.merge(schedule[['ROAD TEAM', 'HOME TEAM', 'game_id']], on=['game_id'], how='left')
df['point_diff'] = df['away_score'] - df['home_score']
df = pd.melt(df, id_vars=['point_diff','elapsed', 'elapsed_seconds', 'game_id', 'event_type'],  value_vars=['ROAD TEAM', 'HOME TEAM'])
df['point_diff'] = df.apply(lambda row: row['point_diff'] * -1 if row['variable']=='HOME TEAM' else row['point_diff'], axis=1)
df['minute'] = df['elapsed'].str.split(':').apply(lambda x: int(x[1]))
df['team_id'] = df['value']

df_past = df.copy()
df_past['elapsed_seconds'] = df_past['elapsed_seconds'] + 3*60
df_past = df_past.rename(columns={'point_diff': 'past_point_diff'})
df_past.sort_values(by=['elapsed_seconds'], inplace=True)

df_future = df.copy()
df_future['elapsed_seconds'] = df_future['elapsed_seconds'] - 3*60
df_future = df_future.rename(columns={'point_diff': 'future_point_diff'})
df_future.sort_values(by=['elapsed_seconds'], inplace=True)

timeouts = pd.merge_asof(timeouts, df_past, on='elapsed_seconds', by=['game_id', 'team_id'], direction='backward')
timeouts = pd.merge_asof(timeouts, df_future, on='elapsed_seconds', by=['game_id', 'team_id'], direction='backward')


#Time since last break
game_break_event_names = ['start of period', 'timeout']
game_breaks = df[df.event_type.isin(game_break_event_names)]
game_breaks['last_break_time'] = game_breaks['elapsed_seconds']
game_breaks = game_breaks[['elapsed_seconds', 'game_id', 'last_break_time']]
game_breaks.sort_values(by=['elapsed_seconds'], inplace=True)
timeouts = pd.merge_asof(timeouts, game_breaks, on='elapsed_seconds', by=['game_id'], direction='backward', allow_exact_matches=False)
timeouts['time_since_last_break'] = timeouts['elapsed_seconds'] - timeouts['last_break_time']


#Prepare output
timeouts = timeouts[OUTPUT_COLS]
timeouts['treatment'] = 1

timeouts.to_csv('output/timeouts.csv')
