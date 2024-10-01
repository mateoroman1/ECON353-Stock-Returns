import streamlit as st
from requests import get
import csv
import io
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import xlsxwriter as xc
import pandas as pd

# Load API key
av_key = st.secrets['ALPHAVANTAGE_KEY']
alp_key = st.secrets['ALPACA_KEY']
alp_secret = st.secrets['ALPACA_SECRET']

def get_alpaca_data(ticker: str):
    client = StockHistoricalDataClient(alp_key, alp_secret)

    request_params = StockBarsRequest(
        symbol_or_symbols=ticker, 
        timeframe=TimeFrame.Month, 
        start=datetime(2019, 9, 1), 
        end=datetime(2024, 9, 1),
        adjustment='split'
        )

    bars = client.get_stock_bars(request_params)
    return bars.df

# Streamlit App
st.title('Stock Data Downloader for ECON353')
st.markdown("#### **Retrieves Monthly Stock return data for the Stocktrack Portfolio assignment.**\n\n*Enter a stock ticker and hit the button below. You can then save the xlsx file.  Data is currently only from 2024-09-01 to 2019-09-01 and includes all OHLC data. Be sure to only include the :green[close] column in the assignment spreadsheet*")

# Create input form
ticker = st.text_input('Enter Stock Ticker (e.g. AAPL, MSFT):', '')

@st.cache_data
def cache_alpaca_df(df):
    output = io.BytesIO()
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df_reset = df.reset_index()
    df_reset['timestamp'] = df_reset['timestamp'].dt.tz_localize(None)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_reset.to_excel(writer, sheet_name="Sheet 1", index=False)
        return output

# When user submits
if st.button('Retrieve Stock Data'):
    if ticker:
        alpaca_data = cache_alpaca_df(get_alpaca_data(ticker))

        # Add download button
        st.download_button(
            label="Download Excel Sheet",
            data=alpaca_data,  # Pass the string content here
            file_name=f"{ticker}_stock_data.xlsx",
            mime='application/vnd.ms-excel'
        )
    else:
        st.error("Please enter a valid stock ticker.")

st.markdown(":gray[Made by Mateo Roman because Yahoo Finance is wack:sunglasses:]")