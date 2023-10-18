# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 18:43:59 2023

@author: neera
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import os
import pymongo
import time
import logging

#cwd = os.chdir("D:\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")


api_key = 'pos4x0jdsi9vi6m0'
api_secret = '359qisg4c4fbui6ihsxkb99nqxsn1dna'
oldepoch=0

def minute_passed(oldepoch):
    return time.time() - oldepoch >= 180


kite = KiteConnect(api_key=api_key)
#print(kite.login_url()) #use this url to manually login and authorize yourself

#generate trading session
request_token = "NVSa60AcYn0ABq7QFUg2YlSy70o3b15H" #Extract request token from the redirect url obtained after you authorize yourself by loggin in

#data = kite.generate_session(request_token, api_secret=api_secret)
#data["access_token"]


#create kite trading object
kite.set_access_token("2ke6L5ZjbELsLYlqx5pPaH83IKgb0XF7")

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

def tokenLookup(instrument_df,symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]))
    return token_list

#####################update ticker list######################################
tickers = ["INFY", "ACC", "ICICIBANK","NIFTY 50"]
#############################################################################

#create KiteTicker object
kws = KiteTicker(api_key,kite.access_token)
tokens = tokenLookup(instrument_df,tickers)

def on_ticks(ws,ticks):
    # Callback to receive ticks.
    #logging.debug("Ticks: {}".format(ticks))
    global oldepoch
    if(minute_passed(oldepoch)):
        oldepoch = time.time()
        print(oldepoch)
        logging.debug("Ticks: {}".format(ticks))
        print(ticks)
        insert_ticks(ticks)

    

def on_connect(ws,response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    #logging.debug("on connect: {}".format(response))
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL,tokens) # Set all token tick in `full` mode.
    #ws.set_mode(ws.MODE_FULL,[tokens[0]])  # Set one token tick in `full` mode.
 



def insert_ticks(ticks):
    client = pymongo.MongoClient(r"mongodb://localhost:27017/")
    mydb = client["kite"]
    for tick in ticks:
        try:
            tok = "TOKEN"+str(tick['instrument_token'])
            #print(tok)
            mydict = { "name": tick['instrument_token'], "timestamp": tick['exchange_timestamp'] 
                      , "ohlc": tick['ohlc'],"last_price": tick['last_price']}
            #print(mydict)
            #print("before")
            mycol = mydb[str(tick['instrument_token'])]   
            #print(mydict)
            #print("after")
            #print("collecion name="+ str(tick['instrument_token']))
            x = mycol.insert_one(mydict)   
            #print(x.inserted_id)
        except:
            pass



kws.on_ticks=on_ticks
kws.on_connect=on_connect
print("Before kws.connect")
kws.connect()
print("After kws.connect")
