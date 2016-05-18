# -*- coding: utf-8 -*-
"""
Spyder Editor
# a script to go into an Alexa skill
# the skill will allow me to ask Alexa when my buses are coming
# it will poll the 63, 64, 70, and 79 southbound to start
# it will then report the first several 

"""



import httplib, urllib, urllib2, base64
import json
import numpy as np
import pandas as pd

# my tier 3 WMATA API key
api_key = '83151dadf5be461f96c84af142a9c984'

# next bus prediction API
def NBP(StopID = ''):
    headers = {
    # Basic Authorization Sample
    # 'Authorization': 'Basic %s' % base64.encodestring('{username}:{password}'),
    }
    params = urllib.urlencode({
        # Specify your subscription key
        'api_key': api_key,
        # Specify values for the following required parameters
        'StopID': StopID,
        })
 
    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/NextBusService.svc/json/jPredictions?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    return data

# define the stop IDs to poll
# 63 south at sherman and girard
#1001930
# 64 south at 11th and Harvard
#1003048
# 70 south at Georgia and Gresham
#1001948
# 79 south at Georgia and Columbia
#1001986 

stoplist = [1001930, 1003048, 1001948, 1001986]

# get all predictions from each stop, build into a small data frame
# data frame contains pairs of route name and arrival times
pred = pd.DataFrame()
for stop in stoplist:
    data = NBP(stop)
    [['routenum',time]]
    pred.append
    
columns = ['route','time']

# filter to report the stops in arrival order, report all lines at least once
# report all times under 5 minutes
# sort the dataframe

# for lines that appear multipl times, remove any that are more than 5 minutes away


# loop to report each one

