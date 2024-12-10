
import os
import logging
import asyncio
import yfinance as yf
from dotenv import load_dotenv
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import streamlit as st

# Load environment variables securely from .env file
def load_env_variables():
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not all([api_key, secret_key]):
        raise EnvironmentError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment variables.")
    return api_key, secret_key

# Real-Time Alpaca Streaming
async def start_alpaca_stream(api_key, secret_key, stock_symbol):
    try:
        stream = Stream(api_key, secret_key, base_url=URL("https://paper-api.alpaca.markets"), data_feed="iex")

        @stream.on_trade(stock_symbol)
        async def on_trade(data):
            logging.info(f"Trade update for {stock_symbol}: {data}")
            st.write(f"Alpaca Real-Time Data: {data}")

        await stream.run()
    except Exception as e:
        logging.error(f"Error in Alpaca streaming: {e}")
        st.error(f"Error in Alpaca streaming: {e}")

# Real-Time Yahoo Finance Data
def fetch_yahoo_live_data(stock_symbol):
    try:
        ticker = yf.Ticker(stock_symbol)
        return ticker.history(period="1d").iloc[-1]
    except Exception as e:
        logging.error(f"Error in Yahoo Finance live data: {e}")
        st.error(f"Error in Yahoo Finance live data: {e}")
        return None

# Fetch Yahoo Finance Historical Data
def fetch_yahoo_historical_data(stock_symbol, start_date, end_date):
    try:
        data = yf.download(stock_symbol, start=start_date, end=end_date)
        return data
    except Exception as e:
        logging.error(f"Error in Yahoo Finance historical data: {e}")
        st.error(f"Error in Yahoo Finance historical data: {e}")
        return None

# Streamlit Integration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
st.title("Option 3: Both APIs for Live and Historical Data")
st.write("Stream live data and fetch historical data from Alpaca and Yahoo Finance.")

try:
    api_key, secret_key = load_env_variables()
    stock_symbol = st.text_input("Enter a stock ticker", "AAPL")
    if st.button("Start Alpaca Stream"):
        st.write(f"Streaming Alpaca data for {stock_symbol}...")
        asyncio.run(start_alpaca_stream(api_key, secret_key, stock_symbol))
    if st.button("Fetch Yahoo Live Data"):
        yahoo_live_data = fetch_yahoo_live_data(stock_symbol)
        if yahoo_live_data is not None:
            st.write(f"Yahoo Finance Live Data for {stock_symbol}: {yahoo_live_data}")
    if st.button("Fetch Historical Data"):
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        historical_data = fetch_yahoo_historical_data(stock_symbol, start_date, end_date)
        if historical_data is not None:
            st.write(f"Yahoo Finance Historical Data for {stock_symbol}: {historical_data}")
except EnvironmentError as env_error:
    st.error(f"Environment Error: {env_error}")
except Exception as e:
    st.error(f"Application Error: {e}")
