import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
load_dotenv() 

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f1c7f1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Database connection parameters 
db_user = "root"
db_password = "kabir19*"
db_host = "localhost"
db_name = "retail_sales_db"

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# Initialize SQLDatabase
db = SQLDatabase(engine, sample_rows_in_table_info=3)

# Initialize LLM
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# Create SQL query chain
chain = create_sql_query_chain(llm, db)

def clean_sql_query(response):
    """Clean the SQL query by stripping unnecessary formatting."""
    return response.strip('```sql\n').strip('```').strip()

def execute_query(question):
    try:
        # Generate SQL query from question
        response = chain.invoke({"question": question})
        
        # Clean the SQL query
        cleaned_query = clean_sql_query(response)
        
        # Execute the cleaned query
        result = db.run(cleaned_query)
                
        # Return the query and the result
        return cleaned_query, result
    except ProgrammingError as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Streamlit interface
st.title("Chat with our Database !")

# Input from user
question = st.text_input("What is your Question?")

if st.button("Execute"):
    if question:
        cleaned_query, query_result = execute_query(question)
        
        if cleaned_query and query_result is not None:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            st.write("Query Result:")
            st.write(query_result)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")
        