import pymysql
import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine(
    "mysql://",
    echo=False,
    pool_recycle=3600,
    pool_pre_ping=True,
)


def get_df_dtype(dfparam):
    dfparam.fillna("")
    dtypedict = {}
    for i, j in zip(dfparam.columns, dfparam.dtypes):
        try:
            if "object" in str(j):
                len_of_object = dfparam[i].map(len).max()
                if len_of_object > 255:
                    dtypedict.update({i: sqlalchemy.types.TEXT()})
                else:
                    dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=255)})
            elif "datetime" in str(j):
                dtypedict.update({i: sqlalchemy.types.DateTime()})

            elif "Timestamp" in str(j):
                dtypedict.update({i: sqlalchemy.types.DateTime()})

            elif "float" in str(j):
                dtypedict.update(
                    {i: sqlalchemy.types.Float(precision=3, asdecimal=True)}
                )

            elif "int" in str(j):
                dtypedict.update({i: sqlalchemy.types.INT()})

            elif "boolean" in str(j):
                dtypedict.update({i: sqlalchemy.types.Boolean()})

            else:
                len_of_object = dfparam[i].map(len).max()
                if len_of_object > 255:
                    dtypedict.update({i: sqlalchemy.types.LONGTEXT()})
                else:
                    dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=255)})
        except Exception as e:
            print(e)
            dtypedict.update({i: sqlalchemy.types.TEXT(length=255)})
    return dtypedict


def insert_table(df, table_name):
    with engine.connect() as conn:
        df.to_sql(
            name=table_name,
            con=conn,
            schema="chatbot2022",
            if_exists="replace",  # {'fail', 'replace', 'append'), default 'fail'
            index=False,
            dtype=get_df_dtype(df),
        )


path_dir = "./db_init"
dir_list = ["간부정보", "복지", "용어", "일반정보"]
for dir in dir_list:
    file_list = os.listdir(f"{path_dir}/{dir}")
    for file in file_list:
        if ".csv" in file:
            print(file)
            csv_data = pd.read_csv(f"{path_dir}/{dir}/{file}", encoding="cp949")
            table_name = file.replace(".csv", "")
            insert_table(csv_data, table_name)
