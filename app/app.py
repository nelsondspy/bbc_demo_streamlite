# Import necessary libraries
import streamlit as st
import pandas as pd
import template as t 
import catalog_ds as catalog_ds  
import recommendation_ds as recommendation_ds
import evidence_ds as evidence_ds
from recommendation_ds import df_catalog
import streamlit_authenticator as stauth
from template import mylist_curation_tools
import transparency_tools
import yaml
from yaml.loader import SafeLoader
import diversity_tools 

# Configure the layout of the Streamlit page to use a wide format for more space
st.set_page_config(layout="wide")
st.image("static/bbc_logo.jpg", width=150)  # Adjust width as needed

# Global Search Bar
global_search = st.text_input("🔍 What are you interested in?", key="global_search")

# Loading the configuration from a YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initializing the authenticator with the configuration data
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Logging out any existing session
if st.session_state.get("authentication_status"):
    authenticator.logout()   

if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')

    # Sidebar: User Accessibility Preferences
    st.sidebar.header("Accessibility Settings")
    captions_enabled = st.sidebar.checkbox("Enable Captions", value=True)
    audio_desc_enabled = st.sidebar.checkbox("Enable Audio Descriptions", value=False)

    # Store preferences in session state
    st.session_state["accessibility"] = {
        "captions": captions_enabled,
        "audio_descriptions": audio_desc_enabled,
    }

    st.sidebar.subheader("Your Preferences:")

    if captions_enabled:
        st.sidebar.markdown("✔ **Captions:** Enabled")
    else:
        st.sidebar.markdown("❌ **Captions:** Disabled")

    if audio_desc_enabled:
        st.sidebar.markdown("🎧 **Audio Descriptions:** Enabled")
    else:
        st.sidebar.markdown("❌ **Audio Descriptions:** Disabled")

    st.session_state["user_preferences"] = {
        "needs_captions": captions_enabled,
        "needs_audio_description": audio_desc_enabled,
    }

    # Function to calculate accessibility score
    def calculate_accessibility_score(content, user_preferences):
        score = 1
        if user_preferences["needs_captions"] and content.get("captions", False):
            score += 2
        if user_preferences["needs_audio_description"] and content.get("audio_description", False):
            score += 2
        return score

    # Accessibility Recommendation
    def recommend_content(df_catalog, user_preferences):
        items = df_catalog.to_dict(orient='records')
        scored_content = [(content, calculate_accessibility_score(content, user_preferences)) for content in items]
        sorted_recommendations = sorted(scored_content, key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_recommendations]

    def tile_item(column, item, user_preferences):
        with column:
            st.markdown(u"[![Foo]({})](/videoplay?id={})".format(item['image'], str(item['id'])))
            st.markdown(f"**{item['title']}** : {item['description']}")

            accessibility_tags = []
            if item.get("captions", False):
                accessibility_tags.append("🔠 Captions")
            if item.get("audio_description", False):
                accessibility_tags.append("🎧 Audio Description")

            if accessibility_tags:
                st.markdown(f"**Accessibility:** {', '.join(accessibility_tags)}")

            st.markdown("### Your Preferences:")
            preferences_match = []
            if user_preferences["needs_captions"]:
                preferences_match.append("🔠 Requires Captions")
            if user_preferences["needs_audio_description"]:
                preferences_match.append("🎧 Requires Audio Description")

            st.markdown(f"**User's selected preferences:** {', '.join(preferences_match)}")
            mylist_curation_tools(item)

    def preview(df_catalog):
        user_preferences = st.session_state.get("user_preferences", {
            "needs_captions": False,
            "needs_audio_description": False
        })
        recommended_items = recommend_content(df_catalog, user_preferences)
        columns = st.columns(3)
        for column, item in zip(columns, recommended_items):
            tile_item(column, item, user_preferences)

    # Accessibility Recommendations
    st.title("Accessibility-Aware Recommendations")
    preview(df_catalog)

    # Transparency Recommendations based on Global Search
    st.subheader("Content Recommender based on your interests")

    if global_search:
        results = transparency_tools.recommend_from_input(global_search, df_catalog)
        show_scores = st.checkbox("Show similarity scores", value=False)

        st.markdown("### Recommended for you:")
        columns = st.columns(5)
        items = results.to_dict(orient='records')
        for column, item in zip(columns, items):
            tile_item(column, item, st.session_state["user_preferences"])
            if show_scores:
                with column:
                    st.caption(f"Similarity Score: {round(item['similarity_score'], 2)}%")

    # Featured BBC Content
    st.subheader('BBC Content')
    featured = recommendation_ds.featured_BBC()
    t.preview_featured(featured)

    # Diversity Section
    st.subheader('Diversity')
    rh = diversity_tools.recommend_higth(123)
    t.preview_featured(rh)

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    authenticator.login()


