# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 15:01:18 2023

@author: neera
"""

import plotly as py
from datetime import datetime
from plotly import __version__
import cufflinks
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from plotly.offline import plot
import numpy as np

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    df = DF.copy()
    df["MA_Fast"]=df["close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df["MACD_Histogram"]=df["MACD"]-df["Signal"]
    df.dropna(inplace=True)
    return df

def bollBnd(DF,n):
    "function to calculate Bollinger Band"
    df = DF.copy()
    df["MA"] = df['close'].rolling(n).mean()
    #df["MA"] = df['close'].ewm(span=n,min_periods=n).mean()
    df["BB_up"] = df["MA"] + 2*df['close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_dn"] = df["MA"] - 2*df['close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df

df=pd.read_csv(r"D:\python\NSE_NIFTY.csv")

df = df[(df["time"]> "2023-10-16T00:00:00Z") & (df["time"]< "2023-10-17T00:00:00Z")]

macd = MACD(df,12,26,9)

bollBnd = bollBnd(df,20)


df=bollBnd

fig = go.Figure(data=[go.Candlestick(x=df['time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])



fig = go.Line(data_frame = bollBnd, x = bollBnd.index, y = ['BB_up', 'BB_dn'])

fig.show()
py.offline.plot(fig)




#subplots

fig = make_subplots(rows = 2, cols = 1,shared_xaxes=True, row_titles=["OHLC","MACD"] ,vertical_spacing=.25)

# ----------------
# Candlestick Plot
fig.add_trace(go.Candlestick(x = df['time'],
                             open = df['open'],
                             high = df['high'],
                             low = df['low'],
                             close = df['close'], showlegend=False,
                             name = 'candlestick'),
              row = 1, col = 1)

# Moving Average
fig.add_trace(go.Scatter(x = df['time'],
                         y = df['MA'],
                         line_color = 'black',
                         name = 'sma'),
              row = 1, col = 1)

# Upper Bound
fig.add_trace(go.Scatter(x = df['time'],
                         y = df['BB_up'] ,
                         line_color = 'green',
                         line = {'dash': 'dash'},
                         name = 'upper band',
                         opacity = 0.5),
              row = 1, col = 1)

# Lower Bound fill in between with parameter 'fill': 'tonexty'
fig.add_trace(go.Scatter(x = df['time'],
                         y = df['BB_dn'],
                         line_color = 'grey',
                         line = {'dash': 'dash'},
                         fill = 'tonexty',
                         name = 'lower band',
                         opacity = 0.5),
              row = 1, col = 1)

fig.append_trace(go.Scatter(x=macd['time'], y=macd['MACD'], line=dict(color='#C42836', width=1),
    name='MACD Line'), row=2, col=1)

fig.append_trace(go.Scatter(x=macd['time'], y=macd['Signal'], line=dict(color='limegreen', width=1),
    name='Signal Line'), row=2, col=1)

colors = np.where(macd['MACD'] < 0, '#EA071C', '#57F219')


fig.append_trace(go.Bar(x=macd['time'], y=macd['MACD_Histogram'], name='Histogram', marker_color=colors), row=2, col=1)
#plot(fig)
fig.update_layout(
    autosize=False,
    width=1200,
    height=600,
)
#fig.show()
py.offline.plot(fig)





