from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_from_input(user_input, df, top_n=5):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'])

    user_vec = tfidf.transform([user_input])
    similarity_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    df['similarity_score'] = similarity_scores
    recommended = df.sort_values(by='similarity_score', ascending=False).head(top_n)

    return recommended

def explain_recommendation():
    explanation = """
    ### How Recommendations Are Generated:
    - We use **TF-IDF (Term Frequency-Inverse Document Frequency)** to convert your input and content descriptions into numerical vectors.
    - Then we apply **Cosine Similarity** to compare your input with all content.
    - The top results with highest similarity scores are shown as recommendations.
    """
    return explanation

