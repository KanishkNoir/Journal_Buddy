import streamlit as st
import pandas as pd
import requests
import weaviate
import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import cohere
import os
import openai
from dotenv import load_dotenv
load_dotenv()

# Openai api_key
openai.api_key = 'OPENAI_API_KEY'

# Openai gpt response
response = openai.Completion.create(
    engine="text-davinci-003",  # Specify the engine you want to use
    prompt="Once upon a time",
    max_tokens=50
)

print(response.choices[0].text.strip())

# Weaviate client connection
URL = os.getenv('YOUR_WCS_URL')
APIKEY = os.getenv('YOUR_WCS_API_KEY')

# Connect to a WCS instance
client = weaviate.connect_to_wcs(
    cluster_url=URL,
    auth_credentials=weaviate.auth.AuthApiKey(APIKEY))

#Cohere client connection
co = cohere.Client('COHERE_API_KEY')

def daily_quote():
    url = "https://quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com/quote"
    querystring = {"token": "ipworld.info"}
    headers = {
        "X-RapidAPI-Key": "6bec5978aemshf6ed715ed18aa04p17df5djsnc6d22e95d8c8",
        "X-RapidAPI-Host": "quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if response.ok:
        try:
            quote_data = response.json()
            text = quote_data.get("text", "Failed to fetch daily quote")  # Default text if missing
            author = quote_data.get("author", "Unknown")  # Default to "Unknown" if author is missing
            return text, author
        except Exception as e:
            print("Error processing daily quote:", e)
            return "Failed to fetch daily quote"
    else:
        print("Error fetching daily quote:", response.text)
        return "Failed to fetch daily quote"

def chunk_splitting(text):
    # Create a text splitter
    text_splitter = text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_text(text)


# def create_embeddings(chunks):
#     response = co.embed(
#         texts=chunks,
#         model='embed-english-v3.0',
#         input_type='classification'
#     )

def main():
    # Fetch the daily quote
    quote_info = daily_quote()

    # Display the daily quote at the top of the page with a larger font
    st.write(f"<div style='font-size: 24px;'>Daily Quote: {quote_info[0]}</div>", unsafe_allow_html=True)
    st.write(f"<div style='font-size: 14px; text-align: right;'>{quote_info[1]}</div>", unsafe_allow_html=True)

    st.title("Input Output App")

    assert client.is_live()

    # Create the columns
    left, right = st.columns(2)
    # Create an upload box for images
    left.file_uploader("Please insert Images on habits and health!")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)

    # Create a text input box for user input
    user_input = st.text_area("Enter text:")
    st.button("Submit")

    # Create a text box to display the input
    st.sidebar.title("Input Display")
    st.sidebar.markdown(user_input, unsafe_allow_html=True)

    chunks = chunk_splitting(user_input)
    print("chunks created successfully")

    # embeddings = create_embeddings(chunks)

    # Create a text output box to display the processed output
    output_text = process_input(user_input)
    st.text_area("Output:", value=output_text, height=200)

    client.close()

def process_input(input_text):
    # You can add your processing logic here
    # For now, just return the input text as output
    return input_text


if __name__ == "__main__":
    main()
