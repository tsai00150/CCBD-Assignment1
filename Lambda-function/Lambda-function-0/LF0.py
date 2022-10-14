import json
import boto3

# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    # msg_from_user = event['messages'][[0]
    # msg_from_user_content = msg_from_user['unstructured']['text']
    # change this to the message that user submits on 
    # your website using the 'event' variable

    print(event)
    
    {'messages': [{'type': 'unstructured', 'unstructured': {'text': 'hello bot'}}]}
    msg_from_user = event['messages'][0]['unstructured']['text']
    
    print(f"Message from frontend: {msg_from_user}")

    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='AMBVM0T0A2', # MODIFY HERE
            botAliasId='MCERI8AZNP', # MODIFY HERE 
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user
    )
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        
        print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
        print(response)

        msg = {
            "type" : "unstructured",
            "unstructured" : {
                "text" : msg_from_lex[0]['content']
            }
        }
        resp = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'messages' : [
                msg
            ]
        }
        
        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket
        return resp
