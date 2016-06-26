# -*- coding: utf-8 -*-
"""

# a script to go into an Alexa skill via amazon lambda
# the skill will allow me to ask Alexa when the next trains are coming
# it will default to Columbia Heights but other stations can be added

"""


import httplib, urllib, urllib2, base64
import json


# my tier 3 WMATA API key
api_key = '83151dadf5be461f96c84af142a9c984'

"""
modified by Austin to report WMATA train arrivals, based on sample code from Amazon
train code is Austin's

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
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

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
    """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Rosslyn Code: "C05"
    
    
    # Dispatch to your skill's intent handlers
    if intent_name == "Rosslyn":
        # stoplist is a set of stop, route pairs. It will get only the route
        # of interest from each stop, so to get multiple, add multiple
        # entries for each stop
        stoplist = [["C05","1"]]
        session_attributes = {}
        card_title = "Intent: Rosslyn"
        speech_output = get_speech(stoplist, "at Rosslyn")
         # If the user either does not replay to the welcome message or says something
        # that is not understood, they will be prompted again with this text.
        reprompt_text = "I don't think this should be read..."
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    #elif intent_name == "WhatsMyColorIntent":
    #    return get_color_from_session(intent, session)
    #elif intent_name == "AMAZON.HelpIntent":
    #    return get_welcome_response()
    #elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
    #    return handle_session_end_request()
    else:
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
    
    """
    define the stop IDs and directions to poll
    Columbia Heights: Code: "E04"
    """
    
    # stoplist is a set of station, group (direction) pairs. It will get only the direction
    # of interest from each tations, so to get multiple, add multiple
    # entries for each station
    stoplist = [["E04","2"]]

    session_attributes = {}
    card_title = "Welcome"
    speech_output = get_speech(stoplist, "")
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

# --------------- WMATA Functions ----------------------


# next train prediction API from WMATA sample code (thanks WMATA!)
def NT(StationCode = ''):
    headers = {
        # Request headers
        'api_key': api_key, 
        }

    params = urllib.urlencode({
        })

    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/StationPrediction.svc/json/GetPrediction/"+StationCode+"?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("error")
    return data

# custom get speech function

def get_speech(stationlist=[], identifier=""):
    
    # get all predictions from each stop, build into a list
    # list contains colors, destinations, and arrival times
    pred = []
    for station in stationlist:
        # grab next train predictions for the stop
        stationdata = json.loads(NT(station[0]))['Trains']
        # go through each prediction for this stop and grab the minutes and the route
        # keep only the ones with the right route
        pred += [[item['Min'], item['Line'], item['DestinationName']] for item in stationdata if item['Group']==station[1]]    
           
    # drop non-int arrivals times (i.e. boarding)
    pred = [item for item in pred if item[0].isdigit()]

    # sort the dataframe by arrival time
    pred_sorted = sorted(pred, key=lambda pred: int(pred[0]))
        
    # color dictionary for speaking colors
    color_dict = {"SV":"silver","OR":"orange","GR":"green","BL":"blue","RD":"red","YL":"yellow"}

    # loop to report each one
    speech_output = "Upcoming trains " + identifier + ": "
    for row in pred_sorted:
        color = color_dict.get(row[1],"unknown")
        speech_output += "a " + color + " train towards " + str(row[2]) + " in " + str(row[0]) + ' minutes, '
     
    return speech_output
            