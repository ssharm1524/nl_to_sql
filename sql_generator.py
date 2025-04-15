import pandas as pd
import duckdb
import openai
import time
import os

data_path = "./data"

files = [file for file in os.listdir(path = data_path) if file.endswith(".csv")]

chicago_crime = pd.concat(([pd.read_csv(os.path.join(data_path, file)) for file in files]), ignore_index=True)

# print(chicago_crime.head())

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
openai_api_models = pd.DataFrame(openai.Model.list()["data"])
# print(openai_api_models.head())

print("Hi, please enter your query below. Enter 'q' to quit the program.")

while True:
    query = input("> ")
    if query.lower() == 'q':
        print("Goodbye!")
        break
    print(f"Processing query: {query}")

    prompt = create_message("chicago_crime", query)
    message = [
        {
            "role": "system",
            "content": prompt.system
        },
        {
            "role": "user",
            "content": prompt.user
        }
    ]
    response = openai.ChatCompletion.create(
        model = "gpt-4o-mini",
        messages = message,
        temperature = 0,
        max_tokens = 256
    )

    generated_sql_query = print(response.choices[0]["message"]["content"])
    print("Generated SQL Query: ", generated_sql_query)
    print("Running SQL Query...")
    duckdb.sql(generated_sql_query).show()
    
    
