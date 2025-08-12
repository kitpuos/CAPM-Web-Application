import streamlit as st

st.set_page_config(
    page_title = "Trading App",
    page_icon = "📉",
    layout = "wide"
)

st.markdown("<h1 style='text-align: center;'>Trading Guide App 📊</h1>", unsafe_allow_html=True)
st.header("Your premier platform for comprehensive market insights before making investment decisions.")

st.image("E:/CAPM Web Application/images/trading_app_img.png", use_container_width=True)

# Services introduction
st.markdown("# Our Core Services:")

# Service 1
st.markdown("## :one: Stock Information")
st.write("Access detailed and up-to-date information on individual stocks, including performance metrics, historical trends, and market data.")

# Service 2
st.markdown("## :two: Stock Prediction")
st.write(
    "Analyze projected closing prices for the next 30 days using historical market data and advanced forecasting models. "
    "Leverage these predictions to identify market trends, anticipate potential price movements, and make data-driven investment choices."
)

# Service 3
st.markdown("## :three: CAPM Return")
st.write(
    "Understand how the Capital Asset Pricing Model (CAPM) calculates the expected return of a stock based on its risk profile "
    "and prevailing market conditions."
)

# Service 4
st.markdown("## :four: CAPM Beta")
st.write(
    "Evaluate the Beta coefficient and expected return for individual stocks, helping you assess volatility and market sensitivity."
)