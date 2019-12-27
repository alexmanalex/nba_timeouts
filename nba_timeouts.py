import pandas as pd

OUTPUT_COLS = ['treatment', 'outcome', 'scoring_run', 'coach_exp', 'time_since_last_break', 'point_diff']

timeouts = pd.read_csv('output/timeouts.csv')
nontimeouts = pd.read_csv('output/nontimeouts.csv')
coaches = pd.read_csv('output/coaches.csv')


df = timeouts.append(nontimeouts, sort=False)
df = df.merge(coaches, on=['team_id'], how='left')
df['scoring_run'] = df['point_diff'] - df['past_point_diff']
df['outcome'] = df['future_point_diff'] - df['point_diff']

# some missing data for Portland?
# SEE HERE: df[df.team_id.isnull()].groupby('a1').count().sort_values('a2', ascending=False).head(20)
df.dropna(subset=['team_id'], inplace=True)

#single missing value, dropping, should review later
df.dropna(subset=['outcome', 'scoring_run'], inplace=True)

#single missing value, dropping
df.dropna(subset=['time_since_last_break'], inplace=True)

df = df[(df.elapsed_seconds_quarter >= 3*60) & (df.elapsed_seconds_quarter <= (12-3)*60)]

df[OUTPUT_COLS].to_csv('output/nba_timeouts_analysis.csv', index=False)
