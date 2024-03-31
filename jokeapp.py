import streamlit as st
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()  # API key stored in .env file for security purpose

google_api_key = os.getenv("GOOGLE_API_KEY")

st.title("Joke App")  # App title

st.header("Generate a joke using AI")  # Header text

jokeType = st.selectbox("Select Joke types", ["General", "Office", "Programming", "Dark", "Pun", "Spooky", ])

noOfJokes = st.selectbox("Select number of jokes", [1, 2, 3])

#Give me a langChain Prompt Template with type of joke and number of jokes "Tell me {noOfJokes}  {{type of joke}} jokes"




def getJoke(noOfJokes, jokeType):
    promptString=f"Tell me {noOfJokes}  {jokeType} jokes"

    gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=google_api_key)

    result = gemini_llm.invoke(promptString)
    st.write(result.content)
    

if st.button("Generate Jokes"):
    getJoke(noOfJokes, jokeType)
