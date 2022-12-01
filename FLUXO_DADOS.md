# Fluxo de dados do APODBR

O site original da Imagem Astronômica do Dia, em inglês Astronomy Picture of the Day ([APOD](https://apod.nasa.gov/apod/)) foi criado, é escrito, coordenado e editado desde 1995 por Robert Nemiroff e Jerry Bonnell. Todos os dias esses dois astrônomos atualizam o APOD com uma foto ou vídeo astronômico e uma explicação escrita por eles a respeito dessa foto/vídeo. Essas informações são disponibilizadas em inglês através da [apod-api](https://github.com/nasa/apod-api).

O objetivo deste projeto é democratizar o acesso às (incríveis) informações astronômicas do APOD, traduzindo-as para português de forma automática, utilizando a biblioteca [Easy Google Translate](https://github.com/ahmeterenodaci/easygoogletranslate). Na Imagem 1 podemos observar como isso acontece.
  
<figure>
  <img
  src="https://raw.githubusercontent.com/mirianbatista/apod-ptbr-airflow/main/fluxo_dados_apodbr.png"
  alt="Fluxo de dados APOBR">
  <center><figcaption>Imagem 1 - Fluxo de dados APOBR</figcaption>
</figure>

Em resumo, diariamente é feito um request para a apod-api, os dados retornados são colocados em um bucket e em seguida traduzidos, para após isso irem para outro bucket, e então serem inseridos no Redshift para serem utilizados em [uma versão brasileira do APOD](https://apodbr.streamlit.app/).

Agora que temos uma visão geral do fluxo de dados do APODBR, vamos ver detalhadamente o que acontece em cada momento.
