# -*- coding: utf-8 -*-
"""
Spyder Editor
# a script to go into an Alexa skill
# the skill will allow me to ask Alexa when my buses are coming
# it will poll the 63, 64, 70, and 79 southbound to start
# it will then report the first several 

"""

from __future__ import print_function

import httplib, urllib, urllib2, base64
import json


# my tier 3 WMATA API key
api_key = '83151dadf5be461f96c84af142a9c984'

"""
modified by Austin to report bus arrivals, based on sample code from Amazon
bus code is Austin's

"""



def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill 
    Keeping this in but not using it - I might eventually use it to
    let users (me?) pick a route or direction or something    
    """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    """
    # Dispatch to your skill's intent handlers
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")
    """
    
    raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = get_speech()
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't think this should be read..."
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

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

def get_speech():
    session_attributes = {}
    reprompt_text = None
    
    # define the stop IDs to poll
    # 63 south at sherman and girard
    #1001930
    # 64 south at 11th and Harvard
    #1003048
    # 70 south at Georgia and Gresham
    #1001948
    # 79 south at Georgia and Columbia
    #1001986 

    stoplist = [1001930, 1003048, 1001986]
    routelist = [63, 64, 70, 79]

    # get all predictions from each stop, build into a small data frame
    # data frame contains pairs of route name and arrival times
    pred = []
    for stop in stoplist:
        # grab next bus predictions for the stop
        stopdata = json.loads(NBP(str(int(stop))))['Predictions']
        # go through each prediction for this stop and grab the minutes and the route
        pred += [(item['Minutes'], item['RouteID']) for item in stopdata]        

    # sort the dataframe by arrival time
    pred_sorted = sorted(pred, key=lambda pred: pred[0])
        
    # filter to report the stops in arrival order, report all lines at least once
    # report all times under 10 minutes
    MinLim = 10
    SeenRoutes = []
    pred_sifted =[]
    for i in range(0,len(pred_sorted)):
        # if it is in a seen route and less than MinLim, delete
        if pred_sorted[i][1] in SeenRoutes:
            if pred_sorted[i][0] < MinLim:
                pred_sifted.append(pred_sorted[i])
        else:
            SeenRoutes.append(pred_sorted[i][1])
            pred_sifted.append(pred_sorted[i])

        
    # loop to report each one
    speech_output = "Upcoming bus arrivals: "
    for row in pred_sifted:
        speech_output += "the " + str(row[1]) + " in " + str(row[0]) + ' minutes, '
     
    return speech_output
            