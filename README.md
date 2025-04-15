# Natural Language to SQL Query Generator

A Python application that converts natural language queries into SQL using OpenAI's GPT model. This project demonstrates the power of combining large language models with traditional database querying to create an intuitive interface for data analysis.

## Technologies Used

- **Python**: Core programming language
- **OpenAI API**: GPT-3.5-turbo model for natural language processing
- **DuckDB**: In-memory SQL database for efficient querying
- **Pandas**: Data manipulation and analysis
- **Docker**: Containerization for consistent development environment
- **unittest**: Python's built-in testing framework

## Project Overview

This project creates a bridge between natural language and SQL queries, allowing users to interact with databases using everyday language. While developed using the Chicago Crime dataset, the system is designed to work with any CSV dataset, making it a versatile tool for data analysis.

### Key Features

- Natural language to SQL conversion
- Interactive command-line interface
- Support for complex queries including filtering, grouping, and aggregation
- Comprehensive test coverage
- Docker containerization for easy setup

## Docker Integration

This project served as my introduction to Docker, teaching me several important concepts about containerization:

### What is Docker?

Docker is a platform that allows you to package applications and their dependencies into isolated containers. These containers are lightweight, portable, and ensure consistent behavior across different environments.

### Key Docker Learnings

1. **Container vs Image**
   - An image is a blueprint for a container
   - A container is a running instance of an image
   - Images are immutable, while containers are ephemeral

2. **Environment Isolation**
   - Packages installed in a Docker container are isolated from the host machine
   - All dependencies should be specified in `requirements.txt`
   - Changes to the container don't affect the host system

3. **Quickstart Guide**
   ```bash
   # Build the Docker image
   docker build -t nl-to-sql .

   # Run the container
   docker run -it nl-to-sql
   ```

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd nl-to-sql
   ```

2. Set up your environment:
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY='your-api-key-here'
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Examples

The system can handle various types of queries, from simple counts to complex aggregations. Here are some examples:

### Basic Counting Query
```python
query = "How many cases ended up with arrest?"
response = lang2sql(api_key=api_key, table_name="chicago_crime", query=query)
print(response.sql)
# Output: SELECT COUNT(*) FROM chicago_crime WHERE "Arrest" = true;
```

### Filtered Query
```python
query = "How many cases ended up with arrest during 2022"
response = lang2sql(api_key=api_key, table_name="chicago_crime", query=query)
print(response.sql)
# Output: SELECT COUNT(*) FROM chicago_crime WHERE "Arrest" = TRUE AND "Year" = 2022;
```

### Grouped Query
```python
query = "Summarize the cases by primary type"
response = lang2sql(api_key=api_key, table_name="chicago_crime", query=query)
print(response.sql)
# Output: SELECT "Primary Type", COUNT(*) as TotalCases FROM chicago_crime GROUP BY "Primary Type"
```

### Partial Name Recognition
```python
query = "How many cases is the type of robbery?"
response = lang2sql(api_key=api_key, table_name="chicago_crime", query=query)
print(response.sql)
# Output: SELECT COUNT(*) FROM chicago_crime WHERE "Primary Type" = 'ROBBERY';
```

## Dataset Flexibility

While the Chicago Crime dataset was used for development, the system is designed to work with any CSV dataset. The natural language processing component adapts to the schema of your data, making it a versatile tool for various data analysis tasks.

## Testing

The project includes comprehensive unit tests:
```bash
python -m unittest sql_generator_test.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments

- Chicago Crime Dataset
- OpenAI for their powerful language models
- DuckDB for efficient in-memory SQL processing 