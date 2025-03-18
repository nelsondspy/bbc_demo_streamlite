# Import necessary libraries
import streamlit as st
import pandas as pd
import template as t 
import catalog_ds as catalog_ds  
import recommendation_ds as recommendation_ds
import evidence_ds as evidence_ds

# Configure the layout of the Streamlit page to use a wide format for more space
st.set_page_config(layout="wide")





st.image("./static/bbc_logo.jpg", width=150)  # Adjust width as needed

logged_user =st.query_params.get("u")

if (logged_user):  
  st.session_state['username'] = logged_user
else:
  if not st.session_state.get('username'):
    st.session_state['username'] = 'undefined'

st.header('BBC featured content ')

# BBC  feature content  
featured =  recommendation_ds.featured_BBC()
print(featured)
t.preview_featured(featured)


# regional station content 
st.subheader('A specific type of content??')
featured_station = recommendation_ds.filter_by_tags('fake')
t.preview(featured_station)


# Display recommendations based on content similarity to user curated list 
st.subheader('Tailored just for you')
rec_content_based  = recommendation_ds.user_content_based_recommendation(user_id=st.session_state['username'] )
t.preview(rec_content_based)


# Display the user curated list
st.subheader('Your list')
my_list = evidence_ds.my_list(userid=st.session_state['username'])
t.preview(my_list)
