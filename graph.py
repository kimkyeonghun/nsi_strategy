import plotly.graph_objects as go
from plotly.subplots import make_subplots

def ko_make_fig(df, KOSPI, strategy):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df['일자'], y=df['profit'], name="NSI"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=KOSPI['날짜'], y=KOSPI['profit'], name="KOSPI"),
        secondary_y=False,
    )
    if strategy=='bgsf':
        fig.update_layout(
            title_text="Buy the greed, Sell the fear"
        )
    else:
        fig.update_layout(
            title_text="Buy the fear, Sell the greed"
        )


    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Retrun Ratio</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    fig.show()

def en_make_fig(df, SPY, strategy):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['profit'], name="NSI"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=SPY['Date'], y=SPY['profit'], name="S&P 500(SPY)"),
        secondary_y=False,
    )
    if strategy=='bgsf':
        fig.update_layout(
            title_text="Buy the greed, Sell the fear"
        )
    else:
        fig.update_layout(
            title_text="Buy the fear, Sell the greed"
        )


    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Retrun Ratio</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    fig.show()