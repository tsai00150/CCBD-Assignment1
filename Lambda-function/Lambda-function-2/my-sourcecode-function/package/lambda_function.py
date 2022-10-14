from __future__ import print_function
import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError

def send_mail(CUISINE, PPL, DATE, TIME, RECIPIENT, email_info):
    SENDER = "Cloud Computing & Big Data Project 1 <th2990@columbia.edu>"
    AWS_REGION = "us-east-1"
    SUBJECT = "Dining Concierge Assistant Suggestions"
    
    foodlist = []
    n = 1
    for name, addr in email_info:
        foodlist.append(str(n)+". "+name+", located at "+addr )
        n+=1
    BODY_TEXT = "Hello! Here are my "+CUISINE+" restaurant suggestions for "+\
    PPL+" people, for "+DATE+" at "+TIME+": "+', '.join(foodlist)+". Enjoy your meal!"
    
    BODY_HTML = "<html><head></head><body><p>"+BODY_TEXT+"</p></body></html>"            

    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return "Email sent!"


# Reference: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
# Reference: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html


region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-dca-pqqvgswcm2dc5uyq5zkq65hx2u.us-east-1.es.amazonaws.com'
index = 'restaurants'
url = host + '/' + index + '/_search'

# Lambda execution starts here
def lambda_handler(event, context):
    for record in event['Records']:
        payload = json.loads(record["body"])
        CUISINE = payload['cuisine_type']
        PPL = payload['party_number']
        DATE = payload['date']
        TIME = payload['time']
        RECIPIENT = payload['email_address']
        # Put the user query into the query DSL for more accurate search results.
        # Note that certain fields are boosted (^).
        query = {
            "size": 3,
            "query": {
                "multi_match": {
                    "query": CUISINE
                }
            }
        }

        # Elasticsearch 6.x requires an explicit Content-Type header
        headers = { "Content-Type": "application/json" }

        # Make the signed HTTP request
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

        client = boto3.client('dynamodb')

        # get data from dynamodb, store them in email_info
        text_json = json.loads(r.text)
        email_info = []
        for e in text_json['hits']['hits']:
        
            data = client.get_item(
                    TableName='yelp-restaurants',
                    Key={
                        'id': {'S': e["_source"]['RestaurantID']}
                        }
                    )
            address = [x['S'] for x in data['Item']['address']['L']]
            email_info.append((data['Item']['name']['S'], ', '.join(address)))
            
        resp = send_mail(CUISINE, PPL, DATE, TIME, RECIPIENT, email_info)

    return resp
