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


## Sidebar for inputs

st.sidebar.header("User Inputs")

selected_stocks = st.sidebar.multiselect("Select Stocks",
                    options = ["AAPL", "GOOGL", "MSFT", "NFLX", "AMZN", "TSLA", "META", "NVDA", "JPM", "MGM"],
                    default = ["TSLA", "GOOGL", "AMZN", "META"])
years = st.sidebar.number_input("Investment Duration (Years)", min_value = 1, max_value = 25, value = 1, step = 1)


st.sidebar.markdown("---")
st.sidebar.info("Select your preferred stocks and duration, then view results in the tabs below.")

## Downloading stock data

try:
    with st.spinner("Fetching stock data..."):
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
        SP500.columns = ['Date', 'SP500']        
        
        stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
        stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
        stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
        stocks_df = pd.merge(stocks_df, SP500, on = 'Date', how = 'inner')

    ## Tabs for better navigation
    tab1, tab2, tab3 = st.tabs(["📊 Price Data", "📉 Beta Analysis", "📈 CAPM Results"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Raw Price Data (Head)")
            st.dataframe(stocks_df.head(), use_container_width = True)

        with col2:
            st.markdown("### Raw Price Data (Tail)")
            st.dataframe(stocks_df.tail(), use_container_width = True)

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
    

    ## Beta Calculation

    stocks_daily_returns = fn.daily_returns(stocks_df.copy())
    
    beta, alpha = {}, {}

    for i in stocks_daily_returns.columns:
        if i not in ['Date', 'SP500']:
            beta[i], alpha[i] = fn.calculate_beta(stocks_daily_returns, i)
            #beta[i] = beta
            #alpha[i] = alpha
    

    beta_df = pd.DataFrame({
        'Stock': beta.keys(),
        'Beta Value': [str(round(i, 4)) for i in beta.values()]
    })


    with tab2:
        st.markdown("### Beta Values for Selected Stocks")
        st.dataframe(beta_df.style.background_gradient(cmap='coolwarm'), use_container_width = True)
    

    ## CAPM Return Calculation

    rf = 0
    rm = stocks_daily_returns['SP500'].mean() * 252
    
    return_df = pd.DataFrame(
        {
            'Stock': list(beta.keys()),
            'Return Value (%)': [round(rf + (value * (rm - rf)), 2) for value in beta.values()]
        }
    )

    # with col2:
    #     st.markdown("### Calculated return using CAPM")
    #     st.dataframe(return_df, use_container_width = True)
    with tab3:
        st.markdown("### 📌 CAPM Formula")
        st.latex(r"E(R_i) = R_f + \beta_i (E(R_m) - R_f)")

        ## KPI cards
        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Market Return (Rm)", f"{rm:.2f}%")
        kpi2.metric("Risk-Free Rate (Rf)", f"{rf:.2f}%")

        st.markdown("### Calculated Return Using CAPM")
        st.dataframe(return_df.style.background_gradient(cmap="YlGn"), use_container_width=True)

        ## Download button
        st.download_button(
            "📥 Download CAPM Results",
            return_df.to_csv(index=False),
            "capm_results.csv",
            "text/csv"
        )

except:
    st.warning("Please select at least one stock to proceed.")