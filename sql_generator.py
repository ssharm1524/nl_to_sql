import pandas as pd
import duckdb
import openai
import time
import os

class message:
    def __init__(message, system, user, column_names, column_attr):
        message.system = system
        message.user = user
        message.column_names = column_names
        message.column_attr = column_attr

class response:
        def __init__(output, message, response, sql):
            output.message = message
            output.response = response
            output.sql = sql

def add_quotes(query, col_names):
  for i in col_names:
      if i in query:
          l = query.find(i)
          if query[l-1] != "'" and query[l-1] != '"': 
              query = str(query).replace(i, '"' + i + '"') 
  return(query)

def create_message(table_name, query):
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

def lang2sql(api_key, table_name, query, model = "gpt-3.5-turbo", temperature = 0, max_tokens = 256, frequency_penalty = 0,presence_penalty= 0):
    openai.api_key = api_key
    m = create_message(table_name = table_name, query = query)
    message = [
    {
      "role": "system",
      "content": m.system
    },
    {
      "role": "user",
      "content": m.user
    }
    ]
    
    openai_response = openai.ChatCompletion.create(
        model = model,
        messages = message,
        temperature = temperature,
        max_tokens = max_tokens,
        frequency_penalty = frequency_penalty,
        presence_penalty = presence_penalty)
    
    sql_query = add_quotes(query = openai_response["choices"][0]["message"]["content"], col_names = m.column_names)
    output = response(message = m, response = openai_response, sql = sql_query)
    return output

data_path = "./data"
files = [file for file in os.listdir(path = data_path) if file.endswith(".csv")]
chicago_crime = pd.concat(([pd.read_csv(os.path.join(data_path, file)) for file in files]), ignore_index=True)
api_key = os.getenv('OPENAI_KEY')
openai_api_models = pd.DataFrame(openai.Model.list()["data"])

print("Hi, please enter your query below. Enter 'q' to quit the program.")
while True:
    query = input("> ")
    if query.lower() == 'q':
        print("Goodbye!")
        break
    print(f"Processing query: {query}")

    response = lang2sql(api_key = api_key, table_name = "chicago_crime", query = query)

    print("Generated SQL Query: ", response.sql)
    print("Running SQL Query...")
    duckdb.sql(response.sql).show()