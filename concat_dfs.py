import pandas as pd
from loguru import logger
from constants import TOPICS

dfs = []

for topic in TOPICS:
    dfs.append(pd.read_pickle(f'df_gazeta_{topic}.p', compression='gzip'))

df = pd.concat(dfs)

logger.info(df.shape)

df.to_pickle('df_gazeta.p', compression='gzip')
