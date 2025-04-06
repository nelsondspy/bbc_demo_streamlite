from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_from_input(user_input, df, top_n=5):
    # Combine all available text sources
    combined_text = (
        df['description'].fillna('') + " " +
        df['synopsis_small'].fillna('') + " " +
        df['synopsis_medium'].fillna('') + " " +
        df['synopsis_large'].fillna('')
    )

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(combined_text)

    user_vec = tfidf.transform([user_input])
    similarity_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    df['similarity_score'] = (similarity_scores * 100).round(2)  # convert to %
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

