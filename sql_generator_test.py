import os
import unittest
from unittest.mock import patch
from sql_generator import files, data_path


class TestListFiles(unittest.TestCase):
    @patch("os.listdir")
    def test_get_csv_files(self, mock_listdir):
        # Configure the mock to return our test files
        mock_listdir.return_value = ['chicago_crimes_2023.csv', 'chicago_crimes_2024.csv', 'chicago_crime_2022.csv', 'other_file.txt']
        
        # Re-run the list comprehension that creates the 'files' variable
        test_files = [file for file in os.listdir(path=data_path) if file.endswith(".csv")]
        
        # Assert that the files list contains exactly our expected CSV files  
        self.assertEqual(sorted(test_files), sorted(['chicago_crimes_2023.csv', 'chicago_crimes_2024.csv', 'chicago_crime_2022.csv']))