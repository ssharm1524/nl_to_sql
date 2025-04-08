import pandas as pd
import duckdb
import openai
import time
import os

data_path = "./data"

files = [file for file in os.listdir(path = data_path) if file.endswith(".csv")]

chicago_crime = pd.concat(([pd.read_csv(os.path.join(data_path, file)) for file in files]), ignore_index=True)

print(chicago_crime.head())

def create_message(table_name, query):

    class message:
        def __init__(message, system, user, column_names, column_attr):
            message.system = system
            message.user = user
            message.column_names = column_names
            message.column_attr = column_attr

    
    system_template = """

    Given the following SQL table, your job is to write queries given a user’s request. \n

    CREATE TABLE {} ({}) \n
    """

    user_template = "Write a SQL query that returns - {}"
    
    tbl_describe = duckdb.sql("DESCRIBE SELECT * FROM " + table_name +  ";")
    col_attr = tbl_describe.df()[["column_name", "column_type"]]
    col_attr["column_joint"] = col_attr["column_name"] + " " +  col_attr["column_type"]
    col_names = str(list(col_attr["column_joint"].values)).replace('[', '').replace(']', '').replace('\'', '')

    system = system_template.format(table_name, col_names)
    user = user_template.format(query)

    m = message(system = system, user = user, column_names = col_attr["column_name"], column_attr = col_attr["column_type"])
    return m


openai.api_key = os.getenv('OPENAI_KEY')
openai.Model.list()
print(openai.Model.list())

