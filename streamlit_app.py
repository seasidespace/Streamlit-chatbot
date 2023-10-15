import streamlit as st
import os
import openai


st.title('❄️ Welcome to Snowflake Business Intelligent Chatbot')

# Establish Snowflake session
@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets.connections.snowpark).create()

session = create_session()
st.success("Connected to Snowflake!")
