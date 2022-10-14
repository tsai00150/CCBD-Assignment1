import json
import boto3
from datetime import datetime

VALID_CITIES = {"manhattan"}
VALID_CUISINES = {
    "indian", "chinese",
    "japanese", "italian",
    "french", "korean", "american"
}

DATE_FORMAT = r"%Y-%m-%d"
TIME_FORMAT = r"%H:%S"

def _invalid_session_state(slotToElicit, msg = None):
    INVALID_SESSION_STATE = {
        "sessionState" : {
            "dialogAction" : {
                "type": "ElicitSlot",
                "slotToElicit": slotToElicit
            }
        }
    }
    
    if msg:
        INVALID_SESSION_STATE["sessionState"]["dialogAction"]["message"] = {
        "contentType": "PlainText",
        "content": msg
    }
        
    print(INVALID_SESSION_STATE)
        
    return INVALID_SESSION_STATE
        
    
VALID_SESSION_STATE = {
    "sessionState" : {
        "dialogAction" : {
            "type": "Delegate"
        }
    }
}


def _validate_city(city):
    # Set the invalid session state for cities
    msg = f"Sorry, I'm still not availble in {city.title()}"
    slot_to_elicit = "city"
    session_state = _invalid_session_state(slot_to_elicit, msg)

    if city.lower() in VALID_CITIES:
        session_state = VALID_SESSION_STATE

    return session_state

def _validate_cuisine_type(cuisine_type):
    # Set the invalid session state for cuisine type
    msg = f"Sorry, I don't know of any {cuisine_type} restaurants :("
    slot_to_elicit = "cuisine_type"
    session_state = _invalid_session_state(slot_to_elicit, msg)

    if cuisine_type.lower() in VALID_CUISINES:
        session_state = VALID_SESSION_STATE

    return session_state

def _validate_party_number(party_number):
    # Set the invalid session state for party number
    msg = f"Sorry, Invalid party number"
    slot_to_elicit = "party_number"
    session_state = _invalid_session_state(slot_to_elicit, msg)

    if int(party_number) > 0 and party_number.isdigit():
        session_state = VALID_SESSION_STATE

    return session_state

def _validate_date(date):
    # Set the invalid session state for date
    msg = f"I can't make reservations in the past!"
    slot_to_elicit = "date"
    session_state = _invalid_session_state(slot_to_elicit, msg)

    proposed_date = datetime.strptime(date, DATE_FORMAT).date()
    current_date = datetime.now().date()

    if proposed_date >= current_date:
        session_state = VALID_SESSION_STATE

    return session_state

def _validate_time(date, time):
    # Set the invalid session state for time
    msg = f"I can't make reservations in the past!"
    slot_to_elicit = "time"
    session_state = _invalid_session_state(slot_to_elicit, msg)

    proposed_date = datetime.strptime(
        " ".join((date, time)),
        " ".join((DATE_FORMAT, TIME_FORMAT))
    )

    current_date = datetime.now()

    if proposed_date >= current_date:
        session_state = VALID_SESSION_STATE

    return session_state

def validate_slots(slot):
    time = slot["time"]
    date = slot["date"]
    party_number = slot["party_number"]
    cuisine_type = slot["cuisine_type"]
    city = slot["city"]
    elicit_slot = None
    
    response = VALID_SESSION_STATE
    if not time is None:
        response = _validate_time(date["value"]["interpretedValue"], time["value"]["interpretedValue"])
        elicit_slot = "time"
    elif not date is None:
        response = _validate_date(date["value"]["interpretedValue"])
        elicit_slot = "date"
    elif not party_number is None:
        response = _validate_party_number(party_number["value"]["interpretedValue"])
        elicit_slot = "party_number"
    elif not cuisine_type is None:
        response = _validate_cuisine_type(cuisine_type["value"]["interpretedValue"])
        elicit_slot = "cuisine_type"
    elif not city is None:
        response = _validate_city(city["value"]["interpretedValue"])
        elicit_slot = "city"
        
         
    if response["sessionState"]["dialogAction"]["type"] == "ElicitSlot":
        slot[elicit_slot] = None
    
    return response, slot
    
def send_sqs_msg(slots):
    
    sqs_client = boto3.client('sqs')    
    response = sqs_client.send_message(
        QueueUrl = "https://sqs.us-east-1.amazonaws.com/764420359320/DiningConciergeSQS",
        MessageBody = json.dumps(slots)
    )
    
    return response

def lambda_handler(event, context):
    # TODO implement
    
    # Get the session information 
    session_state = event["sessionState"]
    intent = session_state["intent"]

    # print(event)
    
    # Check if the intent has not reached the fulfillment state
    if event["invocationSource"] == "DialogCodeHook":
        
        response = {
            "sessionState" : {
                "dialogAction" : {
                    "type" : "Delegate"
                },
                "intent" : intent
            }
        }
        
        # print(event)
        # proposed_next_state = event["proposedNextState"]
        slots = intent["slots"]

        response, new_slots = validate_slots(slots)
        intent["slots"] = new_slots
        response["sessionState"]["intent"] = intent
        
        print("Response")
        print(response)
        return response

    
    if event["invocationSource"] == "FulfillmentCodeHook":
         # Default dialog action
        # response = {
        #     "fulfillmentState" : "Failed"
        # }
        
        # if confirmation_state == "Confirmed":
        

        
        # Extract the necessary slots to then send to SQS
        slots = {
            slot : value["value"]["interpretedValue"]
            for slot, value in intent["slots"].items()
        }
        
        # send msg to sqs
        sqs_response = send_sqs_msg(slots)
        
        # Update the response dialogAction
        # to indicate that the intent has been fulfilled
        response = {
            "sessionState" : {
                "dialogAction" : {
                    "type" : "Close"
                },
                "intent" : {
                    "name" : intent["name"],
                    "slots" : intent["slots"],
                    "state" : "Fulfilled"
                }
            }
        }
    
    
        
    return response
