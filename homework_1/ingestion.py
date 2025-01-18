import os
import argparse
from ast import literal_eval

from time import time
from typing import Iterator, List

import pandas as pd
from sqlalchemy import create_engine, engine

def get_params():
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write the results to')
    parser.add_argument('--url', help='url of the csv file')
    parser.add_argument("--date_cols", help="date columns in dataset", default="[]")
    return parser.parse_args()

def download_data(url: str, file_name: str) -> None:
    os.system(f"wget {url} -O {file_name}")

def create_postgres_engine(user: str, password: str, host: str, port: str, db: str) -> engine:
    return create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

def get_data_chunk(file_name: str, date_cols: List[str] = False, compression: str = "infer") -> Iterator:
    return pd.read_csv(
        file_name,
        iterator=True,
        chunksize=100000,
        parse_dates=date_cols,
        compression=compression
    )

def save_df(df: pd.DataFrame, table_name: str, engine: engine) -> None:
    df.to_sql(name=table_name, con=engine, if_exists='append')

def main(params):

    user = params.user
    password = params.password
    host = params.host 
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = params.url
    date_cols = literal_eval(params.date_cols)

    compression = "infer"
    csv_name = 'output.csv'

    if ".gz" in params.url:
        csv_name = csv_name+".gz"
        compression = "gzip"

    download_data(url= url, file_name= csv_name)

    engine = create_postgres_engine(
        user = user,
        password = password,
        host = host,
        port = port,
        db = db,
    )

    df_iter = get_data_chunk(
        file_name= csv_name,
        date_cols= date_cols,
        compression= compression
    )
    
    df = next(df_iter)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    save_df(df= df, table_name= table_name, engine= engine)

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            save_df(df= df, table_name= table_name, engine= engine)
            t_end = time()
            print('inserted another chunk, took %.3f second' % (t_end - t_start))
        except StopIteration:
            print('completed')
            break

if __name__ == '__main__':
    params = get_params()
    main(params)
