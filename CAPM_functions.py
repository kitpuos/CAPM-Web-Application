import numpy as np
import plotly.express as px

## Function to plot the CAPM return graph

def plot_capm_return(df):
    fig = px.line()
    for i in df.columns[1:]:
        fig.add_scatter(x = df['Date'], y = df[i], mode = 'lines', name = i)
    
    fig.update_layout(
        width = 450, margin = dict(l = 20, r = 20, t = 50, b = 20),
        legend = dict(orientation = 'h', yanchor = 'bottom', y = 1.02, xanchor = 'right', x = 1),
    )
    
    return fig

## Function to normalize the prices based on initial price

def normalize_prices(df):
    for col in df.columns[1:]:
        df[col] = df[col] / df[col].iloc[0]
    return df

## Function to calculate daily returns

# def daily_returns(df):
#     for i in df.columns[1:]:
#         for j in range(1, len(df)):
#             df[i][j] = ((df[i][j] - df[i][j-1]) / df[i][j-1]) * 100
#         df[i][0] = 0
#     df = df.dropna()
#     return df

def daily_returns(df):
    for col in df.columns[1:]:
        df.loc[1:, col] = ((df[col].iloc[1:].values - df[col].iloc[:-1].values) / df[col].iloc[:-1].values) * 100
        df.loc[0, col] = 0
    return df.dropna()

## Function to calculate beta

def calculate_beta(stocks_daily_returns, stock):
    rm = stocks_daily_returns['SP500'].mean() * 252
    beta, alpha = np.polyfit(stocks_daily_returns['SP500'], stocks_daily_returns[stock], 1)
    return beta, alpha