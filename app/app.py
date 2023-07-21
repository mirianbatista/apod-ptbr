import streamlit as st
import pandas as pd
import pandas_gbq
from google.oauth2 import service_account
import json
import time

hide_streamlit_style = """
                <style>
                # div[data-testid="stToolbar"] {
                # visibility: hidden;
                # height: 0%;
                # position: fixed;
                # }
                # div[data-testid="stDecoration"] {
                # visibility: hidden;
                # height: 0%;
                # position: fixed;
                # }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                # #MainMenu {
                # visibility: hidden;
                # height: 0%;
                # }
                header {
                visibility: hidden;
                height: 0%;
                }
                # footer {
                # visibility: hidden;
                # height: 0%;
                # }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title('O que Mírian está ouvindo agora?')

sa_info = json.loads(st.secrets["gcp"]["service_account"])
credentials = service_account.Credentials.from_service_account_info(sa_info)
project_id = st.secrets["gcp"]["project_id"]

placeholder = st.empty()
placeholder_image = st.empty()

while True:
    try:
        query = f"""
        SELECT *
        FROM `{project_id}.lastfm.lastfm_st`
        ORDER BY publish_time DESC
        LIMIT 1
        """
        results = pandas_gbq.read_gbq(query, project_id=project_id, credentials=credentials)
        df_json = pd.DataFrame(results.data)
        extracted_data = df_json['data'].apply(lambda x: json.loads(x))
        df = pd.DataFrame(extracted_data.to_list())
        
        data_to_display = df.loc[0].to_dict()
        markdown_text = f"**Música:** {data_to_display['lastplayed_trackname']}<br>**Artista:** {data_to_display['lastplayed_artist']}<br>**Álbum:** {data_to_display['lastplayed_album']}"
        placeholder.markdown(markdown_text, unsafe_allow_html=True)
        placeholder_image.image(data_to_display['lastplayed_image_url'], width=300)
        time.sleep(2)
    except:
        placeholder_image.empty()
        placeholder.markdown('nesse momento, apenas as vozes da própria cabeça', unsafe_allow_html=True)