import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # or another Groq model
    temperature=0,
    api_key=GROQ_API_KEY
)