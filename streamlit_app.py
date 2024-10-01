import streamlit as st
from requests import get
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

def get_alpaca_data(ticker: str, start_d: datetime, end_d: datetime):
    client = StockHistoricalDataClient(alp_key, alp_secret)

    request_params = StockBarsRequest(
        symbol_or_symbols=ticker, 
        timeframe=TimeFrame.Month, 
        start=start_d, 
        end=end_d,
        adjustment='split'
        )

    bars = client.get_stock_bars(request_params)
    return bars.df

# Streamlit App
st.title('Stock Data Downloader for ECON353')
st.markdown("#### **Retrieves Monthly Stock return data for the Stocktrack Portfolio assignment.**\n\n*Enter a stock ticker and hit the button below. You can then save the xlsx file.  Data includes all OHLC data. Be sure to only include the :green[close] column in the assignment spreadsheet*")

# Create input form
ticker = st.text_input('Enter Stock Ticker (e.g. AAPL, MSFT):', '')
start_date = st.date_input("From:", datetime(2019, 9, 1))
end_date = st.date_input("To:", datetime(2024, 9, 1))

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
        alpaca_data = cache_alpaca_df(get_alpaca_data(ticker, start_date, end_date))

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