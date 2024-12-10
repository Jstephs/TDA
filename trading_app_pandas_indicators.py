
# Full implementation of the trading app using Pandas-based indicators
import os
import logging
import asyncio
import yfinance as yf
import plotly.graph_objects as go
from textblob import TextBlob
from dotenv import load_dotenv
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import numpy as np
import pandas as pd
import streamlit as st
import tweepy

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

# Technical Indicators with Pandas
def calculate_rsi(data, period=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_sma(data, period):
    return data['Close'].rolling(window=period).mean()

# Twitter API Integration
def fetch_twitter_data(stock_symbol, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret, max_tweets=10):
    try:
        auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
        auth.set_access_token(twitter_access_token, twitter_access_secret)
        api = tweepy.API(auth)
        tweets = tweepy.Cursor(api.search_tweets, q=f"${stock_symbol}", lang="en").items(max_tweets)
        return [tweet.text for tweet in tweets]
    except Exception as e:
        logging.error(f"Error fetching tweets: {e}")
        return []

# Sentiment Analysis on Tweets
def analyze_twitter_sentiment(tweets):
    sentiments = [TextBlob(tweet).sentiment.polarity for tweet in tweets]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"

# Streamlit Integration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
st.title("Next-Gen Trading Platform with Pandas-Based Indicators")
st.write("Trade smarter with real-time market depth, portfolio tracking, and sentiment analysis.")

try:
    api_key, secret_key, news_api_key, twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret = load_env_variables()
    stock_symbol = st.text_input("Enter a stock ticker", "AAPL")
    multi_tickers = st.text_input("Enter multiple tickers (comma-separated)", "AAPL,MSFT,GOOGL").split(',')

    if st.button("Analyze Stock Indicators"):
        data = yf.download(stock_symbol, period="1mo", interval="1d")
        data['RSI'] = calculate_rsi(data)
        data['SMA'] = calculate_sma(data, 20)
        st.write(f"RSI for {stock_symbol}:", data['RSI'].tail())
        st.write(f"SMA for {stock_symbol}:", data['SMA'].tail())

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
