import streamlit as st
import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification
from scipy.special import softmax

# Set Streamlit page configuration
st.set_page_config(page_title="Tweet Sentiment Analysis", page_icon="📊", layout="wide")

# Hide Streamlit default footer and add custom footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
footer:after {
    content:'©2023 Sravathi AI Technology. All rights reserved.'; 
    visibility: visible;
    display: block;
    position: relative;
    padding: 5px;
    top: 2px;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load the trained sentiment analysis model
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Define preprocessing function
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

# Define function for predicting sentiment
def predict_sentiment(text):
    try:
        text = preprocess(text)
        encoded_input = tokenizer(text, return_tensors='pt')
        output = model(**encoded_input)
        scores = output.logits[0].detach().numpy()
        scores = softmax(scores)

        ranking = scores.argsort()[::-1]
        label = config.id2label[ranking[0]]
        score = scores[ranking[0]]

        return label, score
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

# Streamlit UI components
st.title('Tweet Sentiment Analysis')

with st.form("tweet_sentiment_form"):
    text_input = st.text_input('Enter the tweet text:')
    submitted = st.form_submit_button("Analyze Sentiment")

if submitted:
    if not text_input.strip():
        st.error("Please enter some text.")
    else:
        sentiment_label, sentiment_score = predict_sentiment(text_input)
        if sentiment_label is not None and sentiment_score is not None:
            st.write("Sentiment:", sentiment_label)
            st.write("Confidence Score:", sentiment_score)
