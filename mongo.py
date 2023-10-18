# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 12:11:54 2023

@author: neera
"""

import pymongo
from mongoengine import *
import pandas as pd
import ast
import plotly as py
from datetime import datetime
from plotly import __version__
import cufflinks
import plotly.graph_objects as go


client = pymongo.MongoClient(r"mongodb://localhost:27017/")

db = client["kite"]
my_collection = db["256265"]



     
extracted_data = my_collection.find()

df = pd.json_normalize(extracted_data)

fig=df.iplot(kind ='Candlestick', x ='A', y ='B', mode ='markers',asFigure=True)
#fig.write_html("tmp.html")
py.offline.plot(fig)


fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                open=df['ohlc.open'],
                high=df['ohlc.high'],
                low=df['ohlc.low'],
                close=df['ohlc.close'])])

fig.show()
py.offline.plot(fig)
