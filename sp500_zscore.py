import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import zscore

def get_sp500_tickers():
    # Fetch the list of S&P 500 companies
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500_df = table[0]
    return sp500_df['Symbol'].tolist()

def get_weekly_zscore(ticker):
    # Download historical data for the ticker
    stock_data = yf.download(ticker, period='1y', interval='1wk')
    stock_data['Return'] = stock_data['Close'].pct_change()
    stock_data = stock_data.dropna()
    stock_data['Z-Score'] = zscore(stock_data['Return'])
    return stock_data

def main():
    tickers = get_sp500_tickers()
    zscore_data = []
    for ticker in tickers:
        try:
            zscore = get_weekly_zscore(ticker)['Z-Score'].iloc[-1]
            zscore_data.append((ticker, zscore))
        except Exception as e:
            print(f"Failed to process {ticker}: {e}")
    
    zscore_data.sort(key=lambda x: x[1])
    for ticker, zscore in zscore_data[:10]:
        print(f"Ticker: {ticker}, Latest Z-Score: {zscore}")

if __name__ == "__main__":
    main()