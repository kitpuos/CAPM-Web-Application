## CAPM Beta Analysis Page

import datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import streamlit as st
import yfinance as yf
import utils.functions as fn

## Page configuration
st.set_page_config(
    page_title="CAPM Beta Analysis",
    page_icon="🔍",
    layout="wide"
)

## Initialize session state for beta analysis
if 'beta_data' not in st.session_state:
    st.session_state.beta_data = {}

## Title
st.markdown("<h1 style='text-align: center;'>🔍 CAPM Beta Analysis</h1>", unsafe_allow_html=True)

## Main content area - User inputs section

## Create columns for inputs
input_col1, input_col2 = st.columns([1, 1])

with input_col1:
    # Stock selection - no default selection
    single_stock = st.selectbox(
        "Choose a stock:",
        ["Select a stock..."] + ["AAPL", "GOOGL", "MSFT", "NFLX", "AMZN", "TSLA", "META", "NVDA", "JPM", "MGM"],
        index=0  # Default to "Select a stock..."
    )

with input_col2:
    # Years selection
    years = st.number_input("Number of Years", min_value=1, max_value=25, value=1, step=1)

## Check if a valid stock is selected
if single_stock == "Select a stock...":
    ## Display initial message when no stock is selected
    st.markdown("---")
    st.info("🎯 **Welcome to CAPM Beta Analysis!**")
    
    st.markdown("""
    ### 📋 Instructions:
    1. **Select a stock** from the dropdown above
    2. **Choose the analysis period** (number of years)
    3. **View the results** including:
       - Beta coefficient and expected return
       - Interactive regression plot
       - Risk assessment and statistical summary
    
    ### 📊 What is Beta?
    - **Beta > 1**: Stock is more volatile than the market (higher risk, potentially higher returns)
    - **Beta < 1**: Stock is less volatile than the market (lower risk, more stable)
    - **Beta = 1**: Stock moves exactly with the market
    
    ### 📈 CAPM Formula:
    """)
    
    st.latex(r"E(R_i) = R_f + \beta_i (E(R_m) - R_f)")
    
    st.markdown("""
    **Where:**
    - $E(R_i)$ = Expected return of the investment
    - $R_f$ = Risk-free rate
    - $β_i$ = Beta of the investment
    - $E(R_m)$ = Expected return of the market
    """)
    
    ## Sample visualization placeholder
    st.markdown("### 📊 Sample Analysis Preview:")
    
    # Create a sample plot to show what users can expect
    import plotly.graph_objects as go
    
    sample_fig = go.Figure()
    sample_fig.add_trace(go.Scatter(
        x=[-2, -1, 0, 1, 2],
        y=[-1.5, -0.8, 0, 0.9, 2.1],
        mode='markers',
        name='Stock Returns',
        marker=dict(color='blue', size=8, opacity=0.6)
    ))
    sample_fig.add_trace(go.Scatter(
        x=[-2, 2],
        y=[-1.6, 2.0],
        mode='lines',
        name='Expected Return (β=0.9)',
        line=dict(color='red', width=2)
    ))
    sample_fig.update_layout(
        title="Sample Beta Analysis",
        xaxis_title="Market Returns (%)",
        yaxis_title="Stock Returns (%)",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(sample_fig, use_container_width=True)

else:
    ## Create unique key for current beta selection
    beta_selection = f"{single_stock}_{years}"
    
    ## Check if we need new data or use cached data
    need_new_beta_data = (
        'current_beta_selection' not in st.session_state or 
        st.session_state.current_beta_selection != beta_selection or
        beta_selection not in st.session_state.beta_data
    )
    
    ## Main analysis when a stock is selected
    try:
        if need_new_beta_data:
            with st.spinner(f"Fetching data for {single_stock}..."):
                # Get data
                dt = datetime.date
                end = dt.today()
                start = dt(dt.today().year - years, end.month, end.day)
                
                SP500 = web.DataReader(['SP500'], 'fred', start, end)
                stock_data = yf.download(single_stock, period=f'{years}y', auto_adjust=True)
                
                # Prepare dataframe
                stock_df = pd.DataFrame()
                stock_df['Date'] = stock_data.index
                stock_df[single_stock] = stock_data['Close'].values
                
                SP500.reset_index(inplace=True)
                SP500.columns = ['Date', 'SP500']
                stock_df.reset_index(drop=True, inplace=True)
                stock_df['Date'] = pd.to_datetime(stock_df['Date'])
                stock_df = pd.merge(stock_df, SP500, on='Date', how='inner')
                
                # Calculate returns and beta
                stock_returns = fn.daily_returns(stock_df.copy())
                beta_value, alpha_value = fn.calculate_beta(stock_returns, single_stock)
                
                # Calculate CAPM return
                rf = 0
                rm = stock_returns['SP500'].mean() * 252
                capm_return = rf + (beta_value * (rm - rf))
                
                # Calculate additional statistics
                y_pred = alpha_value + beta_value * stock_returns['SP500']
                ss_res = np.sum((stock_returns[single_stock] - y_pred) ** 2)
                ss_tot = np.sum((stock_returns[single_stock] - np.mean(stock_returns[single_stock])) ** 2)
                r_squared = 1 - (ss_res / ss_tot)
                correlation = np.corrcoef(stock_returns['SP500'], stock_returns[single_stock])[0,1]
                volatility = np.std(stock_returns[single_stock])
                
                ## Store in session state
                st.session_state.beta_data[beta_selection] = {
                    'stock_returns': stock_returns,
                    'beta_value': beta_value,
                    'alpha_value': alpha_value,
                    'capm_return': capm_return,
                    'rf': rf,
                    'rm': rm,
                    'r_squared': r_squared,
                    'correlation': correlation,
                    'volatility': volatility,
                    'single_stock': single_stock,
                    'years': years
                }
                
                st.session_state.current_beta_selection = beta_selection
        
        ## Get data from session state
        beta_data = st.session_state.beta_data[beta_selection]
        stock_returns = beta_data['stock_returns']
        beta_value = beta_data['beta_value']
        alpha_value = beta_data['alpha_value']
        capm_return = beta_data['capm_return']
        rf = beta_data['rf']
        rm = beta_data['rm']
        r_squared = beta_data['r_squared']
        correlation = beta_data['correlation']
        volatility = beta_data['volatility']
        
        ## Display Results Section
        st.markdown("---")
        #st.header(f"📊 Analysis Results for {single_stock}")
        st.markdown(f"<h2 style='text-align: center;'>📊 Analysis Results for {single_stock}</h2>", unsafe_allow_html=True)
        
        ## Key Results at the top
        empty_col1, result_col1, result_col2, result_col3, empty_col2 = st.columns([5, 2, 2, 2, 5])
        
        with result_col1:
            st.metric("Beta (β)", f"{beta_value:.4f}")
        with result_col2:
            st.metric("Expected Return", f"{capm_return:.2f}%")
        with result_col3:
            st.metric("Alpha (α)", f"{alpha_value:.4f}")
        
        st.markdown("---")
        
        ## Main analysis layout
        analysis_col1, analysis_col2 = st.columns([1, 1])
        
        with analysis_col1:
            ## Detailed Analysis
            st.markdown("<h3 style='text-align: center;'>📈 Detailed Analysis</h3>", unsafe_allow_html=True)
            
            # CAPM Formula
            st.markdown("### 📌 CAPM Formula")
            st.latex(r"E(R_i) = R_f + \beta_i (E(R_m) - R_f)")
            
            # Parameters breakdown
            st.markdown("### 📊 Parameters Used")
            param_data = {
                "Parameter": ["Risk-free Rate (Rf)", "Market Return (Rm)", "Beta (β)", "Alpha (α)"],
                "Value": [f"{rf:.2f}%", f"{rm:.2f}%", f"{beta_value:.4f}", f"{alpha_value:.4f}"]
            }
            param_df = pd.DataFrame(param_data)
            st.dataframe(param_df, use_container_width=True)
            
            
        
        with analysis_col2:
            ## Regression Plot
            st.markdown(f"<h3 style='text-align: center;'>📈 {single_stock} vs S&P500 Regression</h3>", unsafe_allow_html=True)
            
            # Create the regression plot
            fig = fn.plot_beta_regression_detailed(stock_returns, single_stock, beta_value, alpha_value)
            st.plotly_chart(fig, use_container_width=True)
        
        # Risk Assessment
        st.markdown("### 🎯 Risk Assessment")
        if beta_value > 1:
            st.error(f"🔴 **High Risk Stock**: {single_stock} is {abs(beta_value-1)*100:.1f}% more volatile than the market")
            risk_interpretation = "This stock tends to amplify market movements - higher potential returns but also higher risk."
        elif beta_value < 1:
            st.success(f"🟢 **Low Risk Stock**: {single_stock} is {abs(1-beta_value)*100:.1f}% less volatile than the market")
            risk_interpretation = "This stock is more stable than the market - lower risk but potentially lower returns."
        else:
            st.info(f"🟡 **Market Risk**: {single_stock} moves exactly with the market")
            risk_interpretation = "This stock follows market movements closely."
        
        st.write(risk_interpretation)
        
        ## Additional Statistics Section
        st.markdown("---")
        st.subheader("📊 Statistical Summary")
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric("R-squared", f"{r_squared:.4f}")
        with stats_col2:
            st.metric("Correlation", f"{correlation:.4f}")
        with stats_col3:
            st.metric("Volatility (σ)", f"{volatility:.4f}")
        with stats_col4:
            st.metric("Sample Size", f"{len(stock_returns):,} days")
        
        ## Data Summary Table
        summary_data = {
            "Metric": ["R-squared", "Correlation with Market", "Stock Volatility", "Market Volatility", "Analysis Period"],
            "Value": [
                f"{r_squared:.4f}",
                f"{correlation:.4f}",
                f"{volatility:.4f}",
                f"{np.std(stock_returns['SP500']):.4f}",
                f"{len(stock_returns)} trading days ({years} year{'s' if years > 1 else ''})"
            ],
            "Interpretation": [
                f"{'Strong' if r_squared > 0.7 else 'Moderate' if r_squared > 0.4 else 'Weak'} relationship with market",
                f"{'Strong' if abs(correlation) > 0.7 else 'Moderate' if abs(correlation) > 0.4 else 'Weak'} correlation",
                f"{'High' if volatility > 3 else 'Moderate' if volatility > 1.5 else 'Low'} volatility",
                f"Market volatility reference",
                f"Analysis based on {years} year{'s' if years > 1 else ''} of data"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error loading data for {single_stock}: {str(e)}")
        st.info("Please try selecting a different stock or check your internet connection.")

## Footer
st.markdown("---")
st.markdown("💡 **Tip**: Try different stocks and time periods to compare their beta relationships with the S&P500 market index.")