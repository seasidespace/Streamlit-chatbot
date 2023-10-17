"""
import streamlit as st
import os
import openai
from snowflake.snowpark import Session
import re

st.title('❄️Snowflake Business Intelligent Chatbot')

# Establish Snowflake session
@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets.connections.snowpark).create()

session = create_session()
st.success("Connected to Snowflake!")

# Initialize the chat messages history
openai.api_key = st.secrets.OPENAI_API_KEY
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = ""
        resp_container = st.empty()
        for delta in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += delta.choices[0].delta.get("content", "")
            resp_container.markdown(response)

        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1)
            conn = st.experimental_connection("snowpark")
            message["results"] = conn.query(sql)
            st.dataframe(message["results"])
        st.session_state.messages.append(message)

"""

from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseSequentialChain
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor
from sqlalchemy.dialects import registry
from snowflake.snowpark import Session
import streamlit as st
import openai
import re
import os


# secrets to login snowflake db
user = st.secrets.connections.snowpark.user
password = st.secrets.connections.snowpark.password
warehouse = st.secrets.connections.snowpark.warehouse
role_name = st.secrets.connections.snowpark.role
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

INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": "Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍",
    },
]

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state["messages"] = INITIAL_MESSAGE

if "history" not in st.session_state:
    st.session_state["history"] = []

if "model" not in st.session_state:
    st.session_state["model"] = model

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    message_func(
        message["content"],
        True if message["role"] == "user" else False,
        True if message["role"] == "data" else False,
    )

def append_chat_history(question, answer):
    st.session_state["history"].append((question, answer))

def append_message(content, role="assistant", display=False):
    message = {"role": role, "content": content}
    st.session_state.messages.append(message)
    if role != "data":
        append_chat_history(st.session_state.messages[-2]["content"], content)

    if callback_handler.has_streaming_ended:
        callback_handler.has_streaming_ended = False
        return
response = agent_executor(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    content = st.session_state.messages[-1]["content"]
    if isinstance(content, str):
        result = chain(
            {"question": content, "chat_history": st.session_state["history"]}
        )["answer"]
        print(result)
        append_message(result)
        if get_sql(result):
            conn = SnowflakeConnection().get_session()
            df = execute_sql(get_sql(result), conn)
            if df is not None:
                callback_handler.display_dataframe(df)
                append_message(df, "data", True)


"""
print('sql query: ', response['intermediate_steps'][1])
print('orginal question: ', response['query'])
print('final answer: ', response['result'])
print('sql result: ',response['intermediate_steps'][3])
"""


if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        response = agent_executor.run(prompt)
        st.write( response['intermediate_steps'][1])
        st.write(response['query'])
        st.write(response['result'])
        st.write(response['intermediate_steps'][3])



