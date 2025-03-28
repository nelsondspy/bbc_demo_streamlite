#@title Import Data - df
# Library
import pickle
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import functools
from os.path import join as pjoin 


from sklearn.preprocessing import MinMaxScaler

DATA_DIR = '../data'

# Topic: Arts
with open(pjoin(DATA_DIR,'arts.pkl') , 'rb') as file:
    arts = pickle.load(file)
    arts['Topic'] = 'Arts'

# Topic: Cbbc
with open(pjoin(DATA_DIR,'cbbc.pkl'), 'rb') as file:
    cbbc = pickle.load(file)
    cbbc['Topic'] = 'cbbc'

# Topic: Comedy
with open(pjoin(DATA_DIR,'comedy.pkl'), 'rb') as file:
    comedy = pickle.load(file)
    comedy['Topic'] = 'comedy'

# Topic: documentaries
with open(pjoin(DATA_DIR,'documentaries.pkl'), 'rb') as file:
    documentaries = pickle.load(file)
    documentaries['Topic'] = 'documentaries'

# Topic: entretainment
with open(pjoin(DATA_DIR,'entertainment.pkl') , 'rb') as file:
    entertainment = pickle.load(file)
    entertainment['Topic'] = 'entretainment'

# Topic: films
with open(pjoin(DATA_DIR,'films.pkl') , 'rb') as file:
    films = pickle.load(file)
    films['Topic'] = 'films'

# Topic: archives
with open( pjoin(DATA_DIR,'from-the-archives.pkl') , 'rb') as file:
    fta = pickle.load(file)
    fta['Topic'] = 'from the archives'

# Topic: history
with open(pjoin(DATA_DIR,'history.pkl'), 'rb') as file:
    history = pickle.load(file)
    history['Topic'] = 'history'

# Topic: lifestyle
with open(pjoin(DATA_DIR,'lifestyle.pkl') , 'rb') as file:
    lifestyle = pickle.load(file)
    lifestyle['Topic'] = 'lifestyle'

# Topic: music
with open(pjoin(DATA_DIR,'music.pkl'), 'rb') as file:
    music = pickle.load(file)
    music['Topic'] = 'music'

# Topic: Science - and nature
with open(pjoin(DATA_DIR,'science-and-nature.pkl'), 'rb') as file:
    san = pickle.load(file)
    san['Topic'] = 'science and nature'

# Topic: signed
with open(pjoin(DATA_DIR,'signed.pkl'), 'rb') as file:
    signed = pickle.load(file)
    signed['Topic'] = 'signed'

# Topic: sports
with open(pjoin(DATA_DIR,'sports.pkl') , 'rb') as file:
    sports = pickle.load(file)
    sports['Topic'] = 'sports'

# Creat data frame
df_1 = pd.concat([arts, cbbc, comedy, documentaries, entertainment,films,fta,history,lifestyle,music,san,signed,sports], ignore_index=True)

# Creat a variable with the year
def extrac_year(year):
    # Find 4 number in the varibale
    resultado = re.search(r'\d{4}', year)
    if resultado:
        return resultado.group(0)
    else:
        return None
df_1['year'] = df_1['first_broadcast'].apply(extrac_year)
df_catalog = df_1
df_catalog['id'] = df_catalog.index


# Create the Category variable, with all the topics
def catalog_recommended(df_catalog, num_recommendations=round(86)):
    categories = df_catalog['Topic'].unique()
    num_categories = len(categories)
# Number of recomendation per category
    recommendations_per_category = num_recommendations // num_categories
    remaining_recommendations = num_recommendations % num_categories

    diverse = []

    for category in categories:
        category_items = df_catalog[df_catalog['Topic'] == category]
        num_to_sample = min(recommendations_per_category, len(category_items))
        sampled_items = category_items.sample(n=num_to_sample, replace=True)
        diverse.append(sampled_items)

    if remaining_recommendations > 0:
        extra_categories = df_catalog.groupby('Topic').size().sort_values(ascending=False).index[:remaining_recommendations]
        for extra_category in extra_categories:
            extra_items = df_catalog[df_catalog['Topic'] == extra_category]
            random_item = extra_items.sample(n=1)
            diverse.append(random_item)

# Data frame with the recomendation
    diverse = pd.concat(diverse, ignore_index=True)

#     return diverse[['Topic', 'title', 'description', 'duration_txt']]
    return diverse

#catalog_recommended(df_catalog,10)


###### 

# Feature engeniering and vectorization
df_catalog = df_catalog
df_catalog['descrip'] = df_catalog['category'] + " " + df_catalog['synopsis_small']
vectorizer = TfidfVectorizer(
    strip_accents='unicode',
    lowercase=True,
    stop_words='english',
    min_df=0.1
)

SIMILFILE= pjoin(DATA_DIR, 'similarities.pkl')

if not os.path.exists(SIMILFILE):
    print("BE PREPARE TO WAIT .. the simil file does not exists..yet,  fit_transform started...")
    movie_vectors = vectorizer.fit_transform(df_catalog['descrip'])

    # similarity Calculation

    # Calculate similarities between all movies
    # Depending on your preprocessing, this can take a while
    print("cosine_similarity started...")
    similarity_matrix = cosine_similarity(movie_vectors, movie_vectors)
    print("cosine_similarity end...")
# diversity Score
    similarities_df = pd.DataFrame(similarity_matrix, index=df_catalog.index, columns=df_catalog.index)
    print("similarity to file started...")
    similarities_df.to_pickle(SIMILFILE)
    print("similarity to file end...")
else:
    print("loading  similaries from file")
    similarities_df = pd.read_pickle(SIMILFILE)
    print("end load similatiries")

similarity_avg = similarities_df.mean(axis=1)
df_catalog['diversity'] = 1-similarity_avg

# Recomendation

def get_similarities(bbc_id):
    '''Gets similarity scores for all other movies'''
    similarities = similarities_df.loc[bbc_id]
    similarities.drop(bbc_id, inplace=True)
    return similarities.rename('similarity').to_frame()

def scale_features(bbc_df):
    '''Scales relevant features to domain [0, 1]'''
    scaler = MinMaxScaler((0,1))
    scaler.fit(bbc_df.similarity.to_frame())
    bbc_df['similarity_scaled'] = scaler.transform(bbc_df.similarity.to_frame())

    scaler.fit(bbc_df.diversity.to_frame())
    bbc_df['diversity_scaled'] = scaler.transform(bbc_df.diversity.to_frame())

    return bbc_df

def weighted_score(bbc, similarity_weight, diversity_weight):
    '''Calculates weighter average for relevant (scaled) features'''
    sw = bbc ['similarity_scaled'] * similarity_weight
    dw = bbc ['diversity_scaled'] * diversity_weight
    total_weights = similarity_weight + diversity_weight
    return (sw + dw) / total_weights

## Recomendation Higth Diversity

def recommend_higth(bbc_id, n_results=10, diversity_factor=0.75, similarity_factor=1):
    similarities = get_similarities(bbc_id)

    # dataframe with relevant features for a single movie
    bbc_df = df_catalog.drop(bbc_id, axis='rows').join(similarities)
    bbc_df = scale_features(bbc_df)

    # calculate the weighted score
    weight_func = functools.partial(weighted_score,
                                    similarity_weight=similarity_factor,
                                    diversity_weight=diversity_factor)
    bbc_df['recommender_score'] = bbc_df.apply(weight_func, axis='columns')

    return bbc_df.sort_values('recommender_score', ascending=False).head(n_results)

# Recomendation low Diversity

def recommend_low(bbc_id, n_results=10, diversity_factor=0.25, similarity_factor=1):
    similarities = get_similarities(bbc_id)

    # dataframe with relevant features for a single movie
    bbc_df = df_catalog.drop(bbc_id, axis='rows').join(similarities)
    bbc_df = scale_features(bbc_df)

    # calculate the weighted score
    weight_func = functools.partial(weighted_score,
                                    similarity_weight=similarity_factor,
                                    diversity_weight=diversity_factor)
    bbc_df['recommender_score'] = bbc_df.apply(weight_func, axis='columns')

    return bbc_df.sort_values('recommender_score', ascending=False).head(n_results)

print("low")

recommend_low(bbc_id=123)
print("end low")
recommend_higth(bbc_id=123)
print("end diversity tools ")
