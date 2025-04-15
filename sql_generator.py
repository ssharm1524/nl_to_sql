import pandas as pd
import duckdb
import openai
import time
import os

class message:
    """A class to represent a message for SQL query generation.
    
    This class encapsulates the system and user messages along with column information
    needed for SQL query generation.
    
    Attributes:
        system (str): The system message containing table schema information
        user (str): The user's query request
        column_names (list): List of column names in the table
        column_attr (list): List of column types corresponding to the column names
    """
    def __init__(message, system, user, column_names, column_attr):
        message.system = system
        message.user = user
        message.column_names = column_names
        message.column_attr = column_attr

class response:
    """A class to represent the response from the language model.
    
    This class encapsulates the message, raw response, and generated SQL query.
    
    Attributes:
        message (message): The original message object used for the request
        response (dict): The raw response from the OpenAI API
        sql (str): The generated SQL query with proper column name quoting
    """
    def __init__(output, message, response, sql):
        output.message = message
        output.response = response
        output.sql = sql

def add_quotes(query, col_names):
    """Add quotes around column names in a SQL query.
    
    This function ensures that column names in the SQL query are properly quoted
    to prevent SQL syntax errors.
    
    Args:
        query (str): The SQL query string
        col_names (list): List of column names that need to be quoted
        
    Returns:
        str: The SQL query with column names properly quoted
        
    Example:
        >>> add_quotes("SELECT date FROM table", ["date"])
        'SELECT "date" FROM table'
    """
    for i in col_names:
        if i in query:
            l = query.find(i)
            if query[l-1] != "'" and query[l-1] != '"': 
                query = str(query).replace(i, '"' + i + '"') 
    return(query)

def create_message(table_name, query):
    """Create a message object for SQL query generation.
    
    This function generates a structured message containing the table schema
    and user query that will be sent to the language model.
    
    Args:
        table_name (str): The name of the table to query
        query (str): The natural language query from the user
        
    Returns:
        message: A message object containing system and user messages
                along with column information
    """
    system_template = """
    Given the following SQL table, your job is to write queries given a user's request. \n
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

def lang2sql(api_key, table_name, query, model = "gpt-3.5-turbo", temperature = 0, max_tokens = 256, frequency_penalty = 0, presence_penalty = 0):
    """Convert natural language to SQL using OpenAI's language model.
    
    This function takes a natural language query and converts it to SQL
    using OpenAI's language model. It handles the API communication and
    processes the response to generate a properly formatted SQL query.
    
    Args:
        api_key (str): OpenAI API key
        table_name (str): Name of the table to query
        query (str): Natural language query from the user
        model (str, optional): OpenAI model to use. Defaults to "gpt-3.5-turbo"
        temperature (float, optional): Controls randomness in response. Defaults to 0
        max_tokens (int, optional): Maximum tokens in response. Defaults to 256
        frequency_penalty (float, optional): Penalty for frequent tokens. Defaults to 0
        presence_penalty (float, optional): Penalty for new tokens. Defaults to 0
        
    Returns:
        response: A response object containing the message, raw API response,
                 and generated SQL query
    """
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

# Load data and initialize API key
data_path = "./data"
files = [file for file in os.listdir(path = data_path) if file.endswith(".csv")]
chicago_crime = pd.concat(([pd.read_csv(os.path.join(data_path, file)) for file in files]), ignore_index=True)
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running the program.")

openai.api_key = api_key

# Interactive query interface
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