import streamlit as st
import pandas as pd
import yfinance as yf
import time

# Function to get the list of S&P 500 tickers
@st.cache_data
def get_sp500_tickers():
    sp500url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    data_table = pd.read_html(sp500url)
    tickers = data_table[0]['Symbol'].tolist()
    
    for i in range(len(tickers)):
        if tickers[i] == 'BRK.B':
            tickers[i] = 'BRK-B'
        elif tickers[i] == 'BF.B':
            tickers[i]= 'BF-B'
            
    return tickers

# Function to fetch stock prices
@st.cache_data
def fetch_prices(tickers, start_date, end_date):
    prices = []
    for name in tickers:
        data = yf.download(name, start=start_date, end=end_date)
        if not data.empty:
            open_price = data['Open'][0]
            close_price = data['Close'][0]
            last_updated = pd.Timestamp.now()
            prices.append((name, open_price, close_price, last_updated))
    return prices

# Function to display prices in a dataframe
def display_prices(prices):
    df = pd.DataFrame(prices, columns=['Ticker', 'Open Price', 'Close Price', 'Last Updated Time'])
    st.dataframe(df)

# Streamlit app layout
st.title("Live S&P 500 Stock Prices")

# Get the list of S&P 500 tickers
tickers = get_sp500_tickers()

# Input date range
start_date = st.date_input("Start Date", value=pd.to_datetime('2024-08-28'))
end_date = st.date_input("End Date", value=pd.to_datetime('2024-08-29'))

# Initialize session state
if 'prices' not in st.session_state:
    st.session_state.prices = fetch_prices(tickers, start_date, end_date)

# Refresh Prices button
if st.button('Refresh Prices'):
    st.session_state.prices = fetch_prices(tickers, start_date, end_date)

# Show prices in a grid
display_prices(st.session_state.prices)

# Checkbox for real-time updates
real_time = st.checkbox('Show in real-time')

if real_time:
    refresh_interval = st.number_input('Refresh interval (seconds)', min_value=1, max_value=60, value=10)
    st.write(f"Prices will refresh every {refresh_interval} seconds.")
    
    # Loop to update prices in real-time
    while True:
        st.session_state.prices = fetch_prices(tickers, start_date, end_date)
        display_prices(st.session_state.prices)
        time.sleep(refresh_interval)
        st.rerun()
