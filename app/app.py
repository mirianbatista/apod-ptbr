import streamlit as st
from streamlit_option_menu import option_menu
import requests
import pandas as pd
from datetime import datetime
from easygoogletranslate import EasyGoogleTranslate


st.title('Imagem Astronômica do Dia')
st.markdown("""
Todo dia uma imagem ou vídeo diferente do nosso fascinante universo, junto com uma breve explicação escrita por um astrônomo profissional.
""")

selected = option_menu(None, ["Imagem de hoje", "Outras datas", "Sobre o APOD"], 
    icons=['calendar2-event', 'search', "info-circle"], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "nav-link-selected": {"background-color": "#0f4c81"},
    })

API_KEY = st.secrets["API_KEY"]
url = f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}'
response = requests.get(url)
j = response.json()
df = pd.DataFrame.from_dict([j])

translator = EasyGoogleTranslate(
    source_language='en',
    target_language='pt',
    timeout=10
)

if selected == 'Imagem de hoje':
    today_format = datetime.today().strftime('%d de %B de %Y')
    today_ptbr = translator.translate(today_format)
    title_apod_ptbr = translator.translate(df['title'][0])
    st.subheader(f'{today_ptbr} - {title_apod_ptbr}')
    if df['media_type'][0] == 'image':
        st.image(df['url'][0], caption=title_apod_ptbr)
    else:
        # a api retorna para media_type apenas imagem ou video
        st.video(df['url'][0])
    explanation_apod_ptbr = translator.translate(df['explanation'][0])
    st.markdown(explanation_apod_ptbr)
    st.markdown('APOD original: https://apod.nasa.gov/apod/')
    

if selected == 'Outras datas':
    dt_today = datetime.today().date()
    date_apod = st.date_input("De qual data você deseja ver a Imagem Astronômica do Dia?")
    first_apod = datetime(1995,6,16).date()
    if st.button('Buscar'):
        if (date_apod > dt_today):
            st.error('Ainda não podemos viajar para o futuro, tente outra data!', icon="🖖")
        elif (date_apod < first_apod):
            st.error('A Imagem Astronômica do Dia mais antiga é de 16 de junho de 1995!', icon="🚨")
            # o streamlit só permite buscas a partir de 20 de outubro de 2012 pelo calendário, mas dá pra digitar mais antigas
        else:
            url = f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={date_apod}' 
            response = requests.get(url)
            j = response.json()
            df_date_apod = pd.DataFrame.from_dict([j])

            date_apod_format = date_apod.strftime('%d de %B de %Y')
            date_apod_ptbr = translator.translate(date_apod_format)
            title_apod_ptbr = translator.translate(df_date_apod['title'][0])
            st.subheader(f'{date_apod_ptbr} - {title_apod_ptbr}')
            if df_date_apod['media_type'][0] == 'image':
                st.image(df_date_apod['url'][0], caption=title_apod_ptbr)
            else:
                # a api retorna para media_type apenas imagem ou video
                st.video(df_date_apod['url'][0])
            explanation_apod_ptbr = translator.translate(df_date_apod['explanation'][0])
            st.markdown(explanation_apod_ptbr)
            dt_original_apod = date_apod.strftime('%y%m%d')
            st.markdown(f'APOD original: https://apod.nasa.gov/apod/ap{dt_original_apod}.html')

if selected == 'Sobre o APOD':
    st.write("""
    O site original da Imagem Astronômica do Dia, em inglês Astronomy Picture of the Day (APOD) foi criado, é escrito, coordenado e editado desde 1995 por Robert Nemiroff e Jerry Bonnell. O APOD contém a maior coleção de imagens astronômicas da internet. Mais detalhes podem ser encontrados nas páginas [Sobre](https://apod.nasa.gov/apod/lib/about_apod.html) e [Perguntas Frequentes](https://apod.nasa.gov/apod/ap_faq.html) do site oficial do APOD.
    
    Esta versão brasileira desse projeto maravilhoso utiliza a biblioteca [Easy Google Translate](https://github.com/ahmeterenodaci/easygoogletranslate) para traduzir os textos originais para português. Você pode contribuir [aqui](https://github.com/mirianbatista/apod-ptbr).
    """)


