import numpy as np
import plotly.express as px
import plotly.graph_objects as go

## Function to plot interactive plotly charts

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

## New function for detailed beta regression plot (matching your reference image)
def plot_beta_regression_detailed(daily_returns, stock, beta, alpha):
    import plotly.graph_objects as go
    import numpy as np

    fig = go.Figure()

    # Scatter points
    fig.add_trace(go.Scatter(
        x = daily_returns['SP500'], y = daily_returns[stock], mode = 'markers', name = 'Stock Returns',
        marker = dict(color = 'blue', size = 8, opacity = 0.6), showlegend = False
    ))

    # Regression line
    min_x = daily_returns['SP500'].min()
    max_x = daily_returns['SP500'].max()

    fig.add_trace(go.Scatter(
        x = [min_x, max_x], y = [alpha + beta * min_x, alpha + beta * max_x], mode = 'lines',
        name = f'Expected Return (β={beta:.2f})', line = dict(color = 'red', width = 2)
    ))

    # Layout changes for full width & top legend

    fig.update_layout(
        xaxis_title = "Market Returns (%)", yaxis_title = "Stock Returns (%)",
        legend = dict(orientation = "h", yanchor = "bottom", y = 1.02, xanchor = "center", x = 0.5),
        margin = dict(l = 20, r = 20, t = 50, b = 20),
        autosize = True
    )

    return fig