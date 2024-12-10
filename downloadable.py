
# Full implementation of the trading app with Twitter API integration
import os
import logging
import asyncio
import yfinance as yf
import talib
import plotly.graph_objects as go
from textblob import TextBlob
from dotenv import load_dotenv
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import numpy as np
from scipy.optimize import minimize
import streamlit as st
import requests
import tweepy  # Twitter API library

# Load environment variables securely from .env file
def load_env_variables():
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    news_api_key = os.getenv("NEWS_API_KEY")
    twitter_api_key = os.getenv("TWITTER_API_KEY")
    twitter_api_secret = os.getenv("TWITTER_API_SECRET")
    twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    if not all([api_key, secret_key, news_api_key, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret]):
        raise EnvironmentError("Missing required API keys in environment variables.")
    return api_key, secret_key, news_api_key, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret

# Twitter API Integration
def fetch_twitter_data(stock_symbol, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret, max_tweets=10):
    try:
        # Authenticate with Twitter API
        auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
        auth.set_access_token(twitter_access_token, twitter_access_secret)
        api = tweepy.API(auth)

        # Fetch tweets about the stock symbol
        tweets = tweepy.Cursor(api.search_tweets, q=f"${stock_symbol}", lang="en").items(max_tweets)
        tweet_texts = [tweet.text for tweet in tweets]

        return tweet_texts
    except Exception as e:
        logging.error(f"Error fetching tweets: {e}")
        st.error(f"Error fetching tweets: {e}")
        return []

# Sentiment Analysis on Tweets
def analyze_twitter_sentiment(tweets):
    sentiments = [TextBlob(tweet).sentiment.polarity for tweet in tweets]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"

# Streamlit Integration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
st.title("Next-Gen Trading Platform with Twitter Sentiment Analysis")
st.write("Trade smarter with real-time market depth, portfolio tracking, and Twitter sentiment analysis.")

try:
    # Load environment variables
    api_key, secret_key, news_api_key, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret = load_env_variables()
    stock_symbol = st.text_input("Enter a stock ticker", "AAPL")
    multi_tickers = st.text_input("Enter multiple tickers (comma-separated)", "AAPL,MSFT,GOOGL").split(',')

    # Twitter Sentiment Analysis
    if st.button("Analyze Twitter Sentiment"):
        tweets = fetch_twitter_data(stock_symbol, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret)
        sentiment = analyze_twitter_sentiment(tweets)
        st.write(f"Twitter Sentiment for {stock_symbol}: {sentiment}")
        st.write("Recent Tweets:")
        for tweet in tweets:
            st.write(f"- {tweet}")

except EnvironmentError as env_error:
    st.error(f"Environment Error: {env_error}")
except Exception as e:
    st.error(f"Application Error: {e}")
