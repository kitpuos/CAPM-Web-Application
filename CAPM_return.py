## Importing necessary libraries
import datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import streamlit as st
import yfinance as yf
import CAPM_functions as fn


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
start = dt(dt.today().year - years, end.month, end.day)
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
    
    ## Plotting the CAPM return graph
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Price of all the stocks")
        fig = fn.plot_capm_return(stocks_df)
        st.plotly_chart(fig, use_container_width = True)
    
    with col2:
        st.markdown("### Normalized Price of all the stocks")
        normalized_df = fn.normalize_prices(stocks_df.copy())
        fig = fn.plot_capm_return(normalized_df)
        st.plotly_chart(fig, use_container_width = True)
    
    ## Calculating daily returns

    stocks_daily_returns = fn.daily_returns(stocks_df.copy())
    print(stocks_daily_returns.head(10))

    ## Displaying daily returns

    beta, alpha = {}, {}

    for i in stocks_daily_returns.columns:
        if i != 'Date' and i != 'SP500':
            beta[i], alpha[i] = fn.calculate_beta(stocks_daily_returns, i)
            #beta[i] = beta
            #alpha[i] = alpha
    
    print(beta, alpha)

    beta_df = pd.DataFrame(columns = ['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 4)) for i in beta.values()]

    with col1:
        st.markdown("### Beta Values")
        st.dataframe(beta_df, use_container_width = True)
    
    rf = 0
    rm = stocks_daily_returns['SP500'].mean() * 252

    return_df = pd.DataFrame()
    return_value = []

    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    
    return_df = pd.DataFrame(
        {
            'Stock': list(beta.keys()),
            'Return Value': return_value
        }
    )

    with col2:
        st.markdown("### Calculated return using CAPM")
        st.dataframe(return_df, use_container_width = True)