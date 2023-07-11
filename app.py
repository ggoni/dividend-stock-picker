import yfinance as yf
import pandas as pd
import sys
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("ticks", {'axes.grid': True})


def dividend_metrics(ticker):

    analyzed_stock = yf.Ticker(ticker)

    # Payout ratio should be between 30% and 50%

    payout_ratio = analyzed_stock.info['payoutRatio']

    # I want the dividend median growth rate to be over 3%

    lfy_div = analyzed_stock.dividends.resample('A').sum().tail(5)[:-1]
    median_div_growth = lfy_div.pct_change().dropna().median()

    # I also want the (last) Dividend yield to be less than 5%
    closing_prices = analyzed_stock.history(
        period='6y').Close.resample('A').last()

    df_pre_div_yield = pd.concat([lfy_div, closing_prices], axis=1).dropna()

    last_dividend_yield = (df_pre_div_yield.Dividends /
                           df_pre_div_yield.Close).values[-1]

    # The formula is annual dividend per share dividend by free cash flow per share
    # I look for a number below 70%

    last_free_cash_flow = analyzed_stock.cash_flow.T['Free Cash Flow'].head(
        1).values[0]
    last_dividends_paid = analyzed_stock.cash_flow.T['Cash Dividends Paid'].head(
        1).values[0]

    free_cash_flow_payout = abs(last_dividends_paid/last_free_cash_flow)

    # I don't want junk

    quick_ratio = analyzed_stock.info['quickRatio']

    # what about last week z_score

    weekly_closes = analyzed_stock.history(
        period="5y", interval="1wk", actions=False).Close

    weekly_change = weekly_closes.pct_change().dropna()

    z_score = (weekly_change - weekly_change.mean())/weekly_change.std()

    dict_values = {'Last Price': analyzed_stock.history(period='1wk', interval='1d').Close[-1],
                   'Payout Ratio': payout_ratio,
                   'Div Growth': median_div_growth,
                   'Dividend Yield': last_dividend_yield,
                   'FCF Payout': free_cash_flow_payout,
                   'Quick Ratio': quick_ratio,
                   'W Z-Score': z_score[-1]}

    return pd.DataFrame(dict_values, index=['Info'])


def mono(ticker):

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Generate first plot with Weekly Close

    analyzed_stock_daily = yf.Ticker(ticker)

    daily_closes = analyzed_stock_daily.history(
        period="5y", interval="1d", actions=False).Close

    daily_vars = daily_closes.pct_change().dropna()

    z_scores_daily = (daily_vars - daily_vars.mean()) / daily_vars.std()

    # Generate first plot

    sns.lineplot(daily_closes, ax=ax1)
    ax1.title.set_text('Daily close')
    ax1.tick_params(axis='x', rotation=90)

    # Generate second plot with Z-Score

    sns.lineplot(z_scores_daily, ax=ax2)
    ax2.axhline(y=z_scores_daily.mean() + 2 * z_scores_daily.std(),
                color='orange',
                linestyle='--')
    ax2.axhline(y=z_scores_daily.mean() - 2 * z_scores_daily.std(),
                color='orange',
                linestyle='--')
    ax2.title.set_text('Daily Z-Score')
    ax2.tick_params(axis='x', rotation=90)

    fig.suptitle('Plots for ' + ticker)

    return fig


def main():

    st.subheader("Stock Dividend Performance")
    input = st.text_input(
        "Enter a stock ticker here",
        "",
        key="placeholder")

    try:
        st.write(dividend_metrics(input))

        st.markdown(
            "We like:\n - Payout ratio between 30% and 50%\n" +
            "- Dividend median growth rate to be over 3%\n - Dividend yield to be less than 5%\n" +
            "- FCF per share < 70%\n - Not Bad Quick Ratio ")

        st.pyplot(mono(input))

    except:
        st.write("No information available")


if __name__ == '__main__':
    main()
