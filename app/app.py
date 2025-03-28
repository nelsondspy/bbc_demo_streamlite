# Import necessary libraries
import streamlit as st
import pandas as pd
import template as t 
import catalog_ds as catalog_ds  
import recommendation_ds as recommendation_ds
import evidence_ds as evidence_ds
from recommendation_ds import df_catalog
import streamlit_authenticator as stauth
from template import mylist_curation_tools  # Import activity function from the other file
import transparency_tools  # For content-based recommendations + explanation

import yaml  # YAML parser and emitter for Python
from yaml.loader import SafeLoader  # Loader class for safe YAML loading
import diversity_tools 
# Configure the layout of the Streamlit page to use a wide format for more space
st.set_page_config(layout="wide")

st.image("static/bbc_logo.jpg", width=150)  # Adjust width as needed

# Loading the configuration from a YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
# Initializing the authenticator with the configuration data
authenticator = stauth.Authenticate(
    config['credentials'],  # User credentials
    config['cookie']['name'],  # Cookie name for session management
    config['cookie']['key'],  # Key for cookie encryption
    config['cookie']['expiry_days']  # Cookie expiry in days
)

# Logging out any existing session
if st.session_state.get("authentication_status"):
    authenticator.logout()   

if st.session_state["authentication_status"]:
    # User is authenticated, display a welcome message
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

    # Display user preferences in a cleaner format
    st.sidebar.subheader("Your Preferences:")

    # Show selected accessibility settings nicely
    if captions_enabled:
        st.sidebar.markdown("✔ **Captions:** Enabled")
    else:
        st.sidebar.markdown("❌ **Captions:** Disabled")

    if audio_desc_enabled:
        st.sidebar.markdown("🎧 **Audio Descriptions:** Enabled")
    else:
        st.sidebar.markdown("❌ **Audio Descriptions:** Disabled")


    # Store preferences in session state
    st.session_state["user_preferences"] = {
        "needs_captions": captions_enabled,
        "needs_audio_description": audio_desc_enabled,

    }

    # Function to calculate accessibility score
    def calculate_accessibility_score(content, user_preferences):
        """ Assigns higher scores to accessible content based on user preferences """
        score = 1  # Base score

        if user_preferences["needs_captions"] and content.get("captions", False):
            score += 2  # Boost for captions
        if user_preferences["needs_audio_description"] and content.get("audio_description", False):
            score += 2  # Boost for audio descriptions

        return score

    # Function to generate recommendations based on accessibility preferences
    def recommend_content(df_catalog, user_preferences):
        items = df_catalog.to_dict(orient='records')
        scored_content = [(content, calculate_accessibility_score(content, user_preferences)) for content in items]

        # Sort content by accessibility score (higher scores first)
        sorted_recommendations = sorted(scored_content, key=lambda x: x[1], reverse=True)

        return [item[0] for item in sorted_recommendations]  # Return sorted content list

    # Function to display content with accessibility labels
    def tile_item(column, item, user_preferences):
        with column:
            st.markdown(u"[![Foo]({})](/videoplay?id={})".format(item['image'], str(item['id'])  ))
            st.markdown(f"**{item['title']}** : {item['description']}")

            # Display accessibility badges
            accessibility_tags = []
            if item.get("captions", False):
                accessibility_tags.append("🔠 Captions")
            if item.get("audio_description", False):
                accessibility_tags.append("🎧 Audio Description")

            if accessibility_tags:
                st.markdown(f"**Accessibility:** {', '.join(accessibility_tags)}")

            # Show user preferences and highlight matching content
            st.markdown("### Your Preferences:")
            preferences_match = []

            if user_preferences["needs_captions"]:
                preferences_match.append("🔠 Requires Captions")
            if user_preferences["needs_audio_description"]:
                preferences_match.append("🎧 Requires Audio Description")

            st.markdown(f"**User's selected preferences:** {', '.join(preferences_match)}")

            # Add interactive buttons
            mylist_curation_tools(item)



    def preview(df_catalog):
        user_preferences = st.session_state.get("user_preferences", {"needs_captions": False, "needs_audio_description": False})

        recommended_items = recommend_content(df_catalog, user_preferences)

        columns = st.columns(3)
        for column, item in zip(columns, recommended_items):
            tile_item(column, item, user_preferences)  # Pass the third argument here


    # 🔹 Display Recommended Content
    st.title("Accessibility-Aware Recommendations")
    preview(df_catalog)

    #transparency added

    st.subheader("Content Recommender based on your interests")

    user_input = st.text_input("Describe what you're interested in:")

    if user_input:
        results = transparency_tools.recommend_from_input(user_input, df_catalog)

        show_scores = st.checkbox("Show similarity scores", value=False)


        st.markdown("### Recommended for you:")
        columns = st.columns(5)
        items = results.to_dict(orient='records')
        for column, item in zip(columns, items):
            tile_item(column, item, st.session_state["user_preferences"])
            if show_scores:
               with column:
                st.caption(f"Similarity Score: {round(item['similarity_score'], 3)}")


    st.subheader('BBC Content ')

    # BBC  feature content  
    featured =  recommendation_ds.featured_BBC()
    print(featured)
    t.preview_featured(featured)


    st.subheader('Diversity')

    rh =  diversity_tools.recommend_higth(123)
    print(rh)
    t.preview_featured(rh)
    
    #t.preview(featured_station)

elif st.session_state["authentication_status"] is False:
    # Authentication failed, display error message
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    # No authentication attempt made yet, display warning and login form
    st.warning('Please enter your username and password')
    authenticator.login()  # Displaying the login form  





