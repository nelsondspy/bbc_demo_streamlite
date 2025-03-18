import streamlit as st
import catalog_ds as catalog_ds


video_id = st.query_params.get("id")


if video_id is None:
    st.header("Select a video fisrt" )
    exit()


video_data =  catalog_ds.df_catalog.iloc[int(video_id)]

st.header(video_data['title'])
st.image(video_data['image'], use_container_width=True)
st.text(video_data['synopsis_large'])



