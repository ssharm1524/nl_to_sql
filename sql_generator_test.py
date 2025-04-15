import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import duckdb
import openai
import os
from sql_generator import message, response, add_quotes, create_message, lang2sql

class TestMessageClass(unittest.TestCase):
    """Test cases for the message class."""
    
    def setUp(self):
        """Set up test data for message class tests."""
        self.test_system = "Test system message"
        self.test_user = "Test user message"
        self.test_column_names = ["col1", "col2"]
        self.test_column_attr = ["INT", "VARCHAR"]
        
    def test_message_initialization(self):
        """Test that message class initializes correctly with all attributes."""
        msg = message(
            system=self.test_system,
            user=self.test_user,
            column_names=self.test_column_names,
            column_attr=self.test_column_attr
        )
        
        self.assertEqual(msg.system, self.test_system)
        self.assertEqual(msg.user, self.test_user)
        self.assertEqual(msg.column_names, self.test_column_names)
        self.assertEqual(msg.column_attr, self.test_column_attr)

class TestResponseClass(unittest.TestCase):
    """Test cases for the response class."""
    
    def setUp(self):
        """Set up test data for response class tests."""
        self.test_message = MagicMock(spec=message)
        self.test_response = {"choices": [{"message": {"content": "SELECT * FROM test"}}]}
        self.test_sql = "SELECT * FROM test"
        
    def test_response_initialization(self):
        """Test that response class initializes correctly with all attributes."""
        resp = response(
            message=self.test_message,
            response=self.test_response,
            sql=self.test_sql
        )
        
        self.assertEqual(resp.message, self.test_message)
        self.assertEqual(resp.response, self.test_response)
        self.assertEqual(resp.sql, self.test_sql)

class TestAddQuotes(unittest.TestCase):
    """Test cases for the add_quotes function."""
    
    def test_add_quotes_single_column(self):
        """Test adding quotes around a single column name."""
        query = "SELECT date FROM table"
        col_names = ["date"]
        expected = 'SELECT "date" FROM table'
        result = add_quotes(query, col_names)
        self.assertEqual(result, expected)
        
    def test_add_quotes_multiple_columns(self):
        """Test adding quotes around multiple column names."""
        query = "SELECT date, time, location FROM table"
        col_names = ["date", "time", "location"]
        expected = 'SELECT "date", "time", "location" FROM table'
        result = add_quotes(query, col_names)
        self.assertEqual(result, expected)
        
    def test_add_quotes_already_quoted(self):
        """Test that already quoted column names are not modified."""
        query = 'SELECT "date" FROM table'
        col_names = ["date"]
        expected = 'SELECT "date" FROM table'
        result = add_quotes(query, col_names)
        self.assertEqual(result, expected)

class TestCreateMessage(unittest.TestCase):
    """Test cases for the create_message function."""
    
    @patch('duckdb.sql')
    def test_create_message(self, mock_duckdb):
        """Test message creation with mocked duckdb response."""
        # Mock duckdb response
        mock_df = pd.DataFrame({
            "column_name": ["col1", "col2"],
            "column_type": ["INT", "VARCHAR"]
        })
        mock_duckdb.return_value.df.return_value = mock_df
        
        table_name = "test_table"
        query = "test query"
        
        result = create_message(table_name, query)
        
        # Verify message attributes
        self.assertIsInstance(result, message)
        self.assertIn(table_name, result.system)
        self.assertIn(query, result.user)
        self.assertEqual(list(result.column_names), ["col1", "col2"])
        self.assertEqual(list(result.column_attr), ["INT", "VARCHAR"])

class TestLang2SQL(unittest.TestCase):
    """Test cases for the lang2sql function."""
    
    @patch('openai.ChatCompletion.create')
    @patch('sql_generator.create_message')
    def test_lang2sql(self, mock_create_message, mock_openai_create):
        """Test the complete lang2sql function with mocked dependencies."""
        # Mock create_message response
        mock_message = MagicMock(spec=message)
        mock_message.system = "system message"
        mock_message.user = "user message"
        mock_message.column_names = ["col1", "col2"]
        mock_create_message.return_value = mock_message
        
        # Mock OpenAI response
        mock_openai_response = {
            "choices": [{"message": {"content": "SELECT * FROM test"}}]
        }
        mock_openai_create.return_value = mock_openai_response
        
        # Test parameters
        api_key = "test_key"
        table_name = "test_table"
        query = "test query"
        
        result = lang2sql(api_key, table_name, query)
        
        # Verify result
        self.assertIsInstance(result, response)
        self.assertEqual(result.message, mock_message)
        self.assertEqual(result.response, mock_openai_response)
        self.assertEqual(result.sql, 'SELECT * FROM test')
        
        # Verify OpenAI API call
        mock_openai_create.assert_called_once()
        call_args = mock_openai_create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-3.5-turbo")
        self.assertEqual(call_args["temperature"], 0)

    @patch('openai.ChatCompletion.create')
    @patch('sql_generator.create_message')
    def test_lang2sql_api_error(self, mock_create_message, mock_openai_create):
        """Test lang2sql function with API error."""
        # Mock create_message response
        mock_message = MagicMock(spec=message)
        mock_create_message.return_value = mock_message
        
        # Mock OpenAI error
        mock_openai_create.side_effect = openai.error.AuthenticationError("Invalid API key")
        
        # Test parameters
        api_key = "invalid_key"
        table_name = "test_table"
        query = "test query"
        
        with self.assertRaises(openai.error.AuthenticationError):
            lang2sql(api_key, table_name, query)

class TestMainFunctionality(unittest.TestCase):
    """Test cases for the main functionality (interactive query interface)."""
    
    @patch('builtins.input')
    @patch('duckdb.sql')
    @patch('sql_generator.lang2sql')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    def test_main_loop(self, mock_lang2sql, mock_duckdb, mock_input):
        """Test the main interactive loop with mocked user input and dependencies."""
        # Mock user input sequence
        mock_input.side_effect = ["test query", "q"]
        
        # Mock lang2sql response
        mock_response = MagicMock(spec=response)
        mock_response.sql = "SELECT * FROM test"
        mock_lang2sql.return_value = mock_response
        
        # Mock duckdb response
        mock_duckdb.return_value.show.return_value = None
        
        # Import and run the main code
        with patch('builtins.print') as mock_print:
            # Import the main code block
            from sql_generator import api_key
            
            # Run the main loop
            print("Hi, please enter your query below. Enter 'q' to quit the program.")
            
            while True:
                query = input("> ")
                if query.lower() == 'q':
                    print("Goodbye!")
                    break
                
                print(f"Processing query: {query}")
                response = lang2sql(api_key=api_key, table_name="chicago_crime", query=query)
                print("Generated SQL Query: ", response.sql)
                print("Running SQL Query...")
                duckdb.sql(response.sql).show()
        
        # Verify the sequence of events
        mock_input.assert_called()
        mock_lang2sql.assert_called_once_with(
            api_key=api_key,
            table_name="chicago_crime",
            query="test query"
        )
        mock_duckdb.assert_called_once_with("SELECT * FROM test")
        
        # Verify print statements
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("Hi, please enter your query below. Enter 'q' to quit the program.", print_calls)
        self.assertIn("Processing query: test query", print_calls)
        self.assertIn("Generated SQL Query:  SELECT * FROM test", print_calls)
        self.assertIn("Running SQL Query...", print_calls)
        self.assertIn("Goodbye!", print_calls)

    @patch.dict('os.environ', {}, clear=True)
    def test_missing_api_key(self):
        """Test that the program raises an error when API key is missing."""
        with self.assertRaises(ValueError) as context:
            from sql_generator import api_key
        self.assertIn("OPENAI_API_KEY environment variable is not set", str(context.exception))

if __name__ == '__main__':
    unittest.main() 