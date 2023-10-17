import streamlit as st
import os
import openai
from snowflake.snowpark import Session
from prompt import get_system_prompt
import re

a = st.secrets.OPENAI_API_KEY

print(a)