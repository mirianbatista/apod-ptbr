from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator


import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
from io import StringIO 
from easygoogletranslate import EasyGoogleTranslate


with DAG(
    'apod_daily',
    default_args={'retries': 2},
    description='ETL DAG Astronomic Picture of the Day',
    schedule_interval=None,
    start_date=datetime(2022, 11, 3),
    catchup=False
) as dag:

    def last_update_redshift():   
        """
        Verifica e retorna a última data de atualização da tabela apod_dev.
        """
        pg_hook = PostgresHook(postgres_conn_id="redshift_default")
        df = pg_hook.get_pandas_df(sql="select * from apod_dev order by date desc")
        if len(df.date) > 0:
            last_update_red = df.sort_values(by='date', ascending=False).date[0]
            # é necessário adicionar um dia a mais no last_update 
            # porque se colocar ele no request, a api retorna ele também, e aí precisaria apagar o dado duplicado
            last_update_red = pd.to_datetime(last_update_red)
            last_update_sum_1_day = last_update_red + timedelta(days=1)
            last_update = last_update_sum_1_day.strftime('%Y-%m-%d')
            print('last_update: ', last_update)
        else:
            # a data do apod mais antigo disponível
            last_update='1995-06-16'
            print('full load: ', last_update)
        return last_update

    @task
    def request_api_nasa():
        """
        Pega dados da API Nasa e salva no s3.
        """        
        # end_date = datetime.now(tz=pytz.timezone("America/Sao_Paulo")).strftime('%Y-%m-%d')
        end_date = '1995-06-23'
        api_key = Variable.get('api_key')
        url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&start_date={last_update_redshift()}&end_date={end_date}'
        response = requests.get(url)
        j = response.json()
        # quando é só uma data, a api retorna um dict apenas 
        # quando é mais de uma data, o response é uma lista com um dict pra cada data 
        if type(j) == dict:
            df = pd.DataFrame.from_dict([j])
        elif type(j) == list:
            df = pd.DataFrame.from_dict(j)

        s3 = S3Hook()
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.load_string(
            string_data=csv_buffer.getvalue(),
            key=f'{end_date}/{end_date}.csv',
            bucket_name='apod-dag-teste',
            replace=True
        )

    @task
    def translate_info_apod():
        # end_date = datetime.now(tz=pytz.timezone("America/Sao_Paulo")).strftime('%Y-%m-%d')
        end_date = '1995-06-23'
        s3 = S3Hook()
        file = s3.download_file(
            key=f'{end_date}/{end_date}.csv',
            bucket_name='apod-dag-teste'
        )
        df = pd.read_csv(file)

        translator = EasyGoogleTranslate(
            source_language='en',
            target_language='pt',
            timeout=10
        )

        df['date'] = pd.to_datetime(df['date'])
        df['date_en'] = df['date'].dt.strftime('%d de %B de %Y')
        dates_ptbr = []
        for row in df.date_en:
            row_translated = translator.translate(row)
            dates_ptbr.append(row_translated)
        df['date_ptbr'] = dates_ptbr
        df.drop('date_en', axis=1, inplace=True)
        
        titles_ptbr = []
        for row in df.title:
            row_translated = translator.translate(row)
            titles_ptbr.append(row_translated)
        df['title_ptbr'] = titles_ptbr

        explanations_ptbr = []
        for row in df.explanation:
            row_translated = translator.translate(row)
            explanations_ptbr.append(row_translated)
        df['explanation_ptbr'] = explanations_ptbr

        if 'copyright' not in df.columns:
            df['copyright'] = None
        print('head: ', df.head)

        s3 = S3Hook()
        csv_buffer = StringIO()
        df_insert = df[['copyright','date','explanation_ptbr','hdurl','media_type','service_version','title_ptbr','url','date_ptbr']]
        df_insert.to_csv(csv_buffer, index=False, header=None)
        s3.load_string(
            string_data=csv_buffer.getvalue(),
            key=f'{end_date}/{end_date}.csv',
            bucket_name='apod-dag-teste-trusted',
            replace=True
        )

    end_date = '1995-06-23'
    insert_apod_translated_redshift = S3ToRedshiftOperator(
        task_id="transfer_s3_to_redshift",
        redshift_conn_id='redshift_default',
        s3_bucket='apod-dag-teste-trusted',
        s3_key=f'{end_date}/{end_date}.csv',
        schema="PUBLIC",
        table='apod_dev',
        copy_options=[
                "DELIMITER AS ','",
                "FORMAT AS CSV",
                "DATEFORMAT AS 'YYYY-MM-DD'"
            ],
        method='APPEND'
    )

    create_redshift_table_if_not_exists = PostgresOperator(
        task_id="create_table",
        sql="sql/create_table_apod.sql",
        postgres_conn_id="redshift_default"
    )

    get_data_nasa = request_api_nasa()

    translate_infos = translate_info_apod()

    create_redshift_table_if_not_exists >> get_data_nasa >> translate_infos >> insert_apod_translated_redshift