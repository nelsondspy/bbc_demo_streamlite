import pandas as pd
import os

base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, '..', 'data', 'bbc_full_dataset.pkl')
df_catalog = pd.read_pickle(file_path)






