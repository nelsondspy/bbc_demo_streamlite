# Necessary imports for the application functionality
import streamlit as st  # Streamlit library for creating web apps
from random import random  # For generating random numbers
import json  # Library for working with JSON data
import datetime  # For handling dates and times

# Function to save user activities to a JSON file
def save_activities():
    with open('activities.json', 'w') as outfile:
        # Dumping the session state activities into the file with pretty printing
        json.dump(st.session_state['activities'], outfile, indent=4)

# Function to handle an activity such as selecting an episode or a season
def activity(id, activity):
  
    # Creating a data dictionary with activity details
    accessibility_prefs = st.session_state.get("accessibility", {})

    data = {
        'content_id': id,
        'activity': activity,
        'user_id': st.session_state['username'],
        'datetime': str(datetime.datetime.now()), # Capturing the current datetime
        "accessibility_prefs": {
            "captions": accessibility_prefs.get("captions", False),
            "audio_descriptions": accessibility_prefs.get("audio_descriptions", False),    }
    }
    # Adding the activity to the session state
    if not st.session_state.get('activities'):
       st.session_state['activities'] = []

    st.session_state['activities'].append(data)
    # Saving the activities after adding the new activity
    save_activities()


# set episode session state
def select_item(isbn):
  st.session_state['id'] = isbn
  print('selected item:', isbn)

def tile_item(column, item, user_preferences):
    show_score = st.session_state.get("show_score", False)

    with column:
        st.markdown(u"[![Foo]({})](/videoplay?id={})".format(item['image'], str(item['id'])))
        st.markdown(f"**{item['title']}** : {item['description']}")

        if show_score and "similarity_score" in item:
            st.caption(f"Similarity Score: {item['similarity_score']}%")

        # Accessibility tags
        accessibility_tags = []
        if item.get("captions", False):
            accessibility_tags.append("🔠 Captions")
        if item.get("audio_description", False):
            accessibility_tags.append("🎧 Audio Description")
        if accessibility_tags:
            st.markdown(f"**Accessibility:** {', '.join(accessibility_tags)}")

        # User prefs match
        preferences_match = []
        if user_preferences["needs_captions"]:
            preferences_match.append("🔠 Requires Captions")
        if user_preferences["needs_audio_description"]:
            preferences_match.append("🎧 Requires Audio Description")
        st.markdown(f"**User's selected preferences:** {', '.join(preferences_match)}")

        mylist_curation_tools(item)


def tile_item_featured(column, item):
    show_score = st.session_state.get("show_score", False)

    with column:
        st.markdown(u"[![Foo]({})](/videoplay?id={})".format(item['image'], str(item['id'])))
        st.markdown(f"**{item['title']}** : {item['description']}")

        if show_score and "similarity_score" in item:
            st.caption(f"Similarity Score: {item['similarity_score']}%")

        mylist_curation_tools(item)
   
    

def mylist_curation_tools(item):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button('➕️ ', key=random(), type='primary' , help='Add to my list' , on_click=activity, args=(item['id'], 'added' ) )

    with col2:
        st.button('✔️', key=random(), type='secondary', help='Mark as watched' , on_click=activity, args=(item['id'], 'watched' ) )

    with col3:
        st.button('✖️', key=random(),type='tertiary', help='Not interested',  on_click=activity, args=(item['id'], 'black_listed' ))
   

def preview(df):
  # check the number of items
  nbr_items = df.shape[0]
  if nbr_items != 0:    
    columns = st.columns(6)
    items = df.to_dict(orient='records')
    any(tile_item(x[0], x[1]) for x in zip(columns, items)) 

def preview_featured(df):
  nbr_items = df.shape[0]
  if nbr_items != 0:    
    columns = st.columns(3)
    # convert df rows to dict lists
    items = df.to_dict(orient='records')
    for i in range(len(columns)):
        column = columns[i]
        item = items[i]
        tile_item_featured(column, item)
       
