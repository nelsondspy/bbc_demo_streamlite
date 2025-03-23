import pandas as pd
import numpy as np
import streamlit as st



# Load Dataset (Ensure the correct path to your dataset)
df_catalog = pd.read_pickle('../bbc_demo_streamlite/data/bbc_full_dataset.pkl')

if "captions" not in df_catalog.columns:
    df_catalog["captions"] = np.random.choice([True, False], len(df_catalog))

if "audio_description" not in df_catalog.columns:
    df_catalog["audio_description"] = np.random.choice([True, False], len(df_catalog))

# Set a seed for reproducibility
np.random.seed(42)

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

def filter_by_accessibility(content_list, user_prefs):
    return [
        c for c in content_list
        if (not user_prefs["captions"] or c.get("captions", False)) and
           (not user_prefs["audio_descriptions"] or c.get("audio_descriptions", False))
    ]

# This function gets accessible recommendations based on user preferences
def get_accessible_recommendations():
    user_prefs = st.session_state.get("accessibility", {})
    return filter_by_accessibility(df_catalog, user_prefs)


