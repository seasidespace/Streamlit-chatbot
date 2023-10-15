import streamlit as st
import os

# Everything is accessible via the st.secrets dict:
st.write("DB username:", st.secrets.OPENAI_API_KEY)
# And the root-level secrets are also accessible as environment variables:

conn = st.experimental_connection("snowpark")
df = conn.query("select current_warehouse()")
st.write(df)
