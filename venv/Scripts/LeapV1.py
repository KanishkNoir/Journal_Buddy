import streamlit as st
import pandas as pd
import requests
import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def analyzeFoodImage(base64_image, key):
    api_key = key
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
                        "text": "You are a nutrionist and your role is to analyze the food image and then tell its nutrition facts, its advantages and disadvantagesm its alternatives and its role in a healthy diet."
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
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # Parse JSON data
    data = response.json()

    # Extract and print the content
    content = data['choices'][0]['message']['content']
    return content


# # Weaviate client connection
# URL = os.getenv('YOUR_WCS_URL')
# APIKEY = os.getenv('YOUR_WCS_API_KEY')
#
# # Connect to a WCS instance
# weaviate_client = weaviate.connect_to_wcs(
#     cluster_url=URL,
#     auth_credentials=weaviate.auth.AuthApiKey(APIKEY),
#     skip_init_checks=True)

# # Cohere client connection
# co = cohere.Client('COHERE_API_KEY')


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


# def chunk_splitting(text):
#     # Create a text splitter
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=100,
#         chunk_overlap=20,
#         length_function=len,
#         is_separator_regex=False,
#     )
#     chunks = text_splitter.split_text(text)
#     return chunks


# def vectorization(chunks):
#     embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
#     vectorstore = Weaviate.from_texts(
#         chunks, embeddings, client=weaviate_client, by_text=False
#     )
#     return vectorstore

def process_input(input_text):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "you are a feedback provider. Analyze the user's journal entry and reflect on it with quotes and affirmations depending on user's moood. Analyze user's productivity and give them feedback how to improve it if its bad and praise them if its good. Analyze the user's activities towards health and fitness and provide feedback and suggestions on it. If the user has entered about food intake them analyze them and suggest adavantages and disadvantages about that and alternative choices. In the end summarize your feedback with a overrall understanding of user's entry and help them maintain a healthy lifestyle."},
            {"role": "user", "content": input_text},
        ],
        max_tokens=400
    )
    print(completion)
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
    st.markdown("In case the daily quote is not visible that means max API requests have expired.")

    st.title("Journal Buddy")

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
    st.sidebar.title("Why daily journaling?")
    st.sidebar.markdown("Daily journaling involves regularly documenting thoughts, experiences, and reflections, usually on a daily basis, to process emotions, document life, and encourage personal development. The practice offers numerous benefits such as mental clarity, stress reduction, heightened self-awareness, improved problem-solving abilities, and the ability to monitor personal growth. It contributes to mental health by serving as a therapeutic outlet for emotions, aiding in anxiety management, stress reduction, and coping with depression through the clarification of thoughts and emotions. Daily journal entries can encompass a wide range of topics including daily activities, thoughts, feelings, goals, challenges, and achievements, providing a personalized space for self-expression.", unsafe_allow_html=True)

    # chunks = chunk_splitting(user_input)
    # print("chunks created successfully")

    # vectorStore = vectorization(chunks)
    # print("embeddings created successfully and stored in vector store")

    st.chat_input("(COMING SOON!) RAG based chatbot that will help you in your journaling and personal growth!")
    # weaviate_client.close()

    # Create an upload box for images
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    openai_key = st.text_input("Enter your OpenAI API key.")

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
        response = analyzeFoodImage(base64_image, openai_key)

        # Display the output in a text area
        st.success(response)


if __name__ == "__main__":
    main()
