# Snowflake Database Chatbot

SnowChat simplifies data interaction with Snowflake through natural language queries. It automates SQL query generation, making data retrieval hassle-free. It's a user-friendly interface for querying data using conversational language.

## What it can do 

It generates SQL queries and data output from natural language input (though sometimes it couldn't understand the question😶‍🌫️).

Here are some example queries you can try with SnowChat:
- How many rows are there in the order table?
- Who has the most purchased order?
- How many actual order delivery is not as scheduled?

## What it cannot do 
- DML manipulation is restricted for security purpose.
    - For example, "drop the order table" is not allowed
- Can't answer unrelated database questions.
    - For example, it cannot answer "how's the weather?"