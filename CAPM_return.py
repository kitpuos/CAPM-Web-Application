## Importing necessary libraries
import datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import streamlit as st
import yfinance as yf


## Page configuration
st.set_page_config(
    page_title = "CAPM Return Calculator",
    page_icon = "📈",
    layout = "wide"
)

## Title of the application
st.title("CAPM Return Calculator")


## Input fields for user data

col1, col2 = st.columns([1, 1])
with col1:
    selected_stocks = st.multiselect("Select Stocks",
                        options = ["AAPL", "GOOGL", "MSFT", "NFLX", "AMZN", "TSLA", "META", "NVDA", "JPM", "MGM"],
                        default = ["AAPL", "GOOGL"])
with col2:
    years = st.number_input("Investment Duration (Years)", min_value = 1, max_value = 25, value = 1, step = 1)


## Downloading stock data

dt = datetime.date
end = dt.today()
start = dt(dt.today().year - years, dt.today().month, dt.today().day)
SP500 = web.DataReader(['SP500'], 'fred', start, end)

stocks_df = pd.DataFrame()

for stock in selected_stocks:
    data = yf.download(stock, period = f'{years}y', auto_adjust=True)
    stocks_df[f'{stock}'] = data['Close']

stocks_df.reset_index(inplace = True)
SP500.reset_index(inplace = True)


## Adjusting columns

SP500.columns = ['Date', 'SP500']

if not selected_stocks:
    st.warning("Please select at least one stock to proceed.")
else:
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, SP500, on = 'Date', how = 'inner')

    ## Alignment
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Dataframe head")
        st.dataframe(stocks_df.head(10), use_container_width = True)

    with col2:
        st.markdown("### Dataframe tail")
        st.dataframe(stocks_df.tail(10), use_container_width = True)