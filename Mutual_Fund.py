import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import streamlit as st

# Streamlit Title and Description
st.title("Mutual Fund Investment Plan")
st.markdown("An interactive tool to analyze and optimize mutual fund investments.")

# User Input for Monthly Investment and Years
monthly_investment = st.number_input("Enter your monthly investment amount:", min_value=1000, value=5000)
interest_rate = st.number_input("Enter the expected annual interest rate (in %):", min_value=0.0, value=12.0)
years = list(map(int, st.text_input("Enter investment periods (comma-separated, in years):", "1,3,5,10,15,20,25,30").split(',')))

# Data Loading and Integrity Checks
try:
    data = pd.read_csv("nifty50_closing_prices.csv")
    if data.empty:
        raise ValueError("The CSV file is empty.")
    assert 'Date' in data.columns, "Date column not found!"
    st.success("Data loaded successfully!")
except (FileNotFoundError, ValueError) as e:
    st.error(f"Error loading data: {str(e)}")
except AssertionError as e:
    st.error(str(e))

# Data Preprocessing
data['Date'] = pd.to_datetime(data['Date'])
data.fillna(method='ffill', inplace=True)

# Price Trend Visualization
fig = go.Figure()
for company in data.columns[1:]:
    fig.add_trace(go.Scatter(x=data['Date'], y=data[company], mode='lines', name=company, opacity=0.5))
fig.update_layout(
    title='Stock Price Trends of All Indian Companies',
    xaxis_title='Date',
    yaxis_title='Closing Price (INR)',
    hovermode='x',
    template='plotly_white'
)
st.plotly_chart(fig)

# Risk and Growth Analysis
all_companies = data.columns[1:]
volatility_all_companies = data[all_companies].std()
growth_all_companies = data[all_companies].pct_change() * 100
average_growth_all_companies = growth_all_companies.mean()

# ROI Calculation
initial_prices_all = data[all_companies].iloc[0]
final_prices_all = data[all_companies].iloc[-1]
roi_all_companies = ((final_prices_all - initial_prices_all) / initial_prices_all) * 100

# Optimal Investment Strategy
roi_threshold = roi_all_companies.median()
volatility_threshold = volatility_all_companies.median()
selected_companies = roi_all_companies[(roi_all_companies > roi_threshold) & (volatility_all_companies < volatility_threshold)]
selected_volatility = volatility_all_companies[selected_companies.index]
inverse_volatility = 1 / selected_volatility
investment_ratios = (inverse_volatility / inverse_volatility.sum()) * 100

# ROI and Volatility Comparison
fig = go.Figure()
fig.add_trace(go.Bar(y=selected_companies.index, x=selected_companies, orientation='h', name='ROI', marker=dict(color='green')))
fig.add_trace(go.Bar(y=selected_volatility.index, x=selected_volatility, orientation='h', name='Volatility', marker=dict(color='red')))
fig.update_layout(title='ROI and Volatility of Selected Companies', template='plotly_white')
st.plotly_chart(fig)

# Future Value Calculation
def future_value(P, r, n, t):
    return P * (((1 + r/n)**(n*t) - 1) / (r/n)) * (1 + r/n)
avg_roi = selected_companies.mean() / 100
future_values = [future_value(monthly_investment, avg_roi, 12, t) for t in years]

# Future Value Visualization
fig = go.Figure()
fig.add_trace(go.Scatter(x=[f"{t} Years" for t in years], y=future_values, mode='lines+markers', name='Future Value', line=dict(color='blue')))
fig.update_layout(title=f'Expected Value of Investments (₹ {monthly_investment} Per Month)', xaxis_title='Years', yaxis_title='Future Value (INR)', template='plotly_white')
st.plotly_chart(fig)

# Saving Investment Ratios
def save_investment_ratios():
    investment_ratios.to_csv("investment_ratios.csv")
    st.success("Investment ratios saved successfully!")
if st.button("Save Investment Ratios"):
    save_investment_ratios()
