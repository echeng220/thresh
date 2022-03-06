# thresh: Fundamental Analysis Dashboard

Welcom to the thresh repo!

thresh is a dashboard I built to help retail investors make smarter investment decisions.

I hope you enjoy the https://thresh0.herokuapp.com/](dashboard)!

## What does thresh do?

thresh has a couple of key features to provide more insight into the fundamental performance of a company.
1. View stock price over time.
2. Calculate and plot key fundamental performance metrics.
    - Users can choose from a variety of ratios and metrics (such as EPS, liquidity ratio etc.) to plot for a given ticker.
3. Yield curve visualization.
    - Users can select any day of the year and view the yield curve on that day. 
4. Benchmark returns visualization.
    - This visualization doesn't have an interactive component, but allows users to see recent historical returns of common benchmarks.

NOTE: This version of thresh uses IEX Cloud sandbox data, which means that the values displayed are not real. A secured version of the dashboard under construction, using real-time financial data from IEX Cloud.

## How is thresh built?

thresh gets financial data from IEX Cloud via the REST API.
Some pre-processing logic cleans the data, and Plotly Dash is used to display the data.
thresh is deployed via Heroku.