import streamlit as st
import pandas as pd
import requests
import weaviate
import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import cohere
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def analyzeFoodImage(base64_image):
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this food image and provide its nutritional benefits and other health parameters."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.json())

    if response.ok:
        json_response = response.json()
        if json_response and 'choices' in json_response and json_response['choices']:
            return json_response['choices'][0]['text']
        else:
            st.warning("No response received from the model.")
            st.write(json_response)
    else:
        st.error("Error analyzing image")
        st.error(f"Status code: {response.status_code}")
        st.error(f"Response content: {response.text}")


# Weaviate client connection
URL = os.getenv('YOUR_WCS_URL')
APIKEY = os.getenv('YOUR_WCS_API_KEY')

# Connect to a WCS instance
weaviate_client = weaviate.connect_to_wcs(
    cluster_url=URL,
    auth_credentials=weaviate.auth.AuthApiKey(APIKEY),
    skip_init_checks=True)

# Cohere client connection
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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)
    return chunks


# def vectorization(chunks):
#     response = co.embed(
#         texts=chunks,
#         model='embed-english-v3.0',
#         input_type='classification'
#     )
#     vectorstore = Weaviate.from_texts(
#         chunks, response, client=client, by_text=False
#     )
#     return vectorstore

def process_input(input_text):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a buddy to the user and you will analyze the journal entry by user and give a feedback to the user that contains parameters like overall mood, health and fitness, food nutritional benefits, productivity. You should give the user feedback such that you praise them for the good things and suggest methods to improve on what they did bad"},
            {"role": "user", "content": input_text},
        ],
        max_tokens=200
    )
    return completion.choices[0].message.content

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")
    return base64_image

def main():
    # Fetch the daily quote
    quote_info = daily_quote()

    # Display the daily quote at the top of the page with a larger font
    st.write(f"<div style='font-size: 24px;'>Daily Quote: {quote_info[0]}</div>", unsafe_allow_html=True)
    st.write(f"<div style='font-size: 14px; text-align: right;'>{quote_info[1]}</div>", unsafe_allow_html=True)

    st.title("Your AI Journaling Buddy")

    # Create a text input box for user input
    user_input = st.text_area("Enter text:")
    sumbit_button = st.button("Submit")

    if sumbit_button:
        st.subheader("Hmm....")
        with st.spinner("Analyzing your daily journal entry..."):
            response = process_input(user_input)
        st.subheader("My feedback to your today's journal entry:")
        st.success(response)

    # Create a text box to display the input
    st.sidebar.title("Input Display")
    st.sidebar.markdown(user_input, unsafe_allow_html=True)

    chunks = chunk_splitting(user_input)
    print("chunks created successfully")

    # vectorStore = vectorization(chunks)
    # print("embeddings created successfully and stored in vector store")

    weaviate_client.close()

    # Create the columns
    left, right = st.columns(2)
    # Create an upload box for images
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        # Display the uploaded image
        st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

        # Save the uploaded image to a folder
        image_folder = "uploaded_images"
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join(image_folder, uploaded_image.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.read())

        # Convert image to base64 string
        base64_image = image_to_base64(image_path)

        # Analyze the image using OpenAI function
        response = analyzeFoodImage(base64_image)

        # Display the output in a text area
        st.success(response)


if __name__ == "__main__":
    main()
