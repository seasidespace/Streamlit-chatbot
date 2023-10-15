import streamlit as st
import os
import openai

# Everything is accessible via the st.secrets dict:
st.write("DB username:", st.secrets.OPENAI_API_KEY)
# And the root-level secrets are also accessible as environment variables:

conn = st.experimental_connection("snowpark")
df = conn.query("select current_warehouse()")
st.write(df)

#change from streamlit app 1

openai.api_key = st.secrets.OPENAI_API_KEY"

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "What is Streamlit?"}
  ]
)

st.write(completion.choices[0].message.content)
