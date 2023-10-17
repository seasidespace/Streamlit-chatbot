from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_experimental.sql.base import SQLDatabaseSequentialChain
#from langchain.chains import SQLDatabaseSequentialChain
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor
from sqlalchemy.dialects import registry
from snowflake.snowpark import Session
import pandas as pd
from ast import literal_eval
import streamlit as st
import openai
import re
import os


# secrets to login snowflake db
#user = st.secrets.connections.snowpark.user
#role_name = st.secrets.connections.snowpark.role
user = st.secrets.connections.snowpark.user_read
role_name = st.secrets.connections.snowpark.role_read
password = st.secrets.connections.snowpark.password
warehouse = st.secrets.connections.snowpark.warehouse
account = st.secrets.connections.snowpark.account
database = st.secrets.connections.snowpark.database
schema = st.secrets.connections.snowpark.schema

# register the snowflake dialects
registry.load("snowflake")
registry.register('snowflake', 'snowflake.sqlalchemy', 'dialect')

# Establish Snowflake session
@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets.connections.snowpark).create()

# Display title 
st.title('❄️Snowflake Database Chatbot')

# display the sidebar
with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()
st.sidebar.markdown(sidebar_content)

# Display the connection success message
session = create_session()
st.success("Connected to Snowflake!")

# create snowflake db instance
conn_string = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role_name}"
db = SQLDatabase.from_uri(conn_string)

# create the sql agent to communicate with the snowflake database
agent_executor = SQLDatabaseSequentialChain.from_llm(
    db = db,
    llm=OpenAI(temperature=0),
    verbose=True,
    return_intermediate_steps=True
    )

# Initialize the chat message history
if "messages" not in st.session_state.keys(): 
    welcome_message = 'Welcome to the ❄️Snowflake Chatbot! I will assist you in navigating and querying your data with ease. Feel free to ask any questions!'
    st.session_state.messages = [
        {"role": "assistant", "content": welcome_message}
    ]

# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display the prior chat messages
for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

# clean the string
def clean_string(input_string):
    lit = literal_eval(re.sub(' "([A-Za-z])" ', r'"\1"', input_string))    
    return lit

# convert it into pandas table
def make_into_markdown_table(lit):
    num_columns = len(lit[0])

    # Create a DataFrame from the output data
    df = pd.DataFrame(lit, columns=[f"Column{i}" for i in range(1, num_columns + 1)])

    # Convert the DataFrame to a Markdown table
    table_markdown = df.to_markdown(index=False)
    return table_markdown

def execute_prompt(prompt):
    try:
        response = agent_executor(prompt)
        
        question = response['query']
        sql_query = response['intermediate_steps'][1]
        sql_result = make_into_markdown_table(clean_string(response['intermediate_steps'][3]))
        answer = response['result']

        final_response = f"**Question:** {question}\n\n**SQL Query:**\n```sql\n{sql_query}\n```\n\n**Output:**\n{sql_result} \n\n\n\n **Answer:** {answer}"
        message = {"role": "assistant", "content": final_response}
        st.session_state.messages.append(message)
       
        st.write(final_response)

        return 
    except:
        message = {"role": "assistant", "content": "🥶I'm sorry, I couldn't perform this operation or answer this question."}
        st.write(message["content"])
        st.session_state.messages.append(message)
        pass
    

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("🤔Thinking..."):
            response = execute_prompt(prompt)

