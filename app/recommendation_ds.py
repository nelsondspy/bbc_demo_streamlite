import pandas as pd


df_catalog = pd.read_pickle('../data/bbc_full_dataset.pkl')

def featured_BBC():
    # what the bbc decided to promote for x reason 
    return df_catalog.iloc[[120,3040,23]]


def filter_by_tags(tag="fake"):
    # we can put any content you want here guys , i just put random stuff
    df_news = df_catalog[df_catalog['tags'].str.contains(tag, case=False)]
    return df_news.sample(10)


def user_content_based_recommendation(user_id):
    # we can put any content you want here guys , i just put random stuff
    return df_catalog.sample(10)

def get_by_id_list(list):
    # we can put any content you want here guys , i just put random stuff
    return df_catalog.iloc[list]
