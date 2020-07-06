import pandas as pd
import numpy as np


non_timeouts = pd.read_csv('output/nontimeouts_raw.csv',
                  # nrows=100000,
                  encoding = "ISO-8859-1",   low_memory=False).drop(0, axis=0)

timeouts = pd.read_csv('output/timeouts.csv',
                  # nrows=100000,
                  encoding = "ISO-8859-1",   low_memory=False).drop(0, axis=0)


timeouts['timeout_time'] = timeouts['elapsed_seconds']
timeouts = timeouts[['game_id', 'elapsed_seconds', 'timeout_time']]
timeouts.sort_values(by=['elapsed_seconds'], inplace=True)

# Add time since last timeout
non_timeouts = pd.merge_asof(non_timeouts, timeouts, on='elapsed_seconds', by=['game_id'], direction='backward', allow_exact_matches=False)
non_timeouts['time_since_last_timeout'] = non_timeouts['elapsed_seconds'] - non_timeouts['timeout_time']
non_timeouts.drop('timeout_time', axis=1, inplace=True)

#Add time until next timeout
non_timeouts = pd.merge_asof(non_timeouts, timeouts, on='elapsed_seconds', by=['game_id'], direction='forward', allow_exact_matches=False)
non_timeouts['time_to_next_timeout'] = non_timeouts['timeout_time'] - non_timeouts['elapsed_seconds']
non_timeouts.drop('timeout_time', axis=1, inplace=True)

#Remove non timeouts within 60 seconds of timeout
non_timeouts = non_timeouts[(non_timeouts.time_to_next_timeout > 60) & (non_timeouts.time_since_last_timeout > 60)]

non_timeouts.drop(['time_since_last_timeout', 'time_to_next_timeout'], axis=1, inplace=True)
non_timeouts.to_csv('output/nontimeouts.csv')
