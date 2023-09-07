import json
import boto3
import random

def lambda_handler(event, context):
    query_params = event['queryStringParameters']
    location = query_params['location']
    email = query_params['email']
    weather_categories=["Clear","Clouds","Rain","Drizzle","Thunderstorm","Snow","Mist","Fog","Haze","Dust","Smoke"]
    output=""
    location_list = []
    location_list.append(location)
    random_choices = random.sample(weather_categories,5)
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('weather_subscriptions')
    response = table.get_item(Key={'email': email})

    
    if 'Item' in response:
        # If the email exists, update the existing data
        fetched_location_fromdb=response['Item']['location']
        fetched_location_fromdb.append(location)
        if not location in fetched_location_fromdb:
             topic_arn=get_topic_arn_by_name(location.lower())
             report=subscribe_email_to_topic(email, topic_arn)

        table.update_item(
            Key={'email': email},
            UpdateExpression='SET #attr1 = :val1, #attr2 = :val2',  # Update your attributes and values here
            ExpressionAttributeNames={'#attr1': 'weathers', '#attr2': 'location'},  # Replace with your attribute names
            ExpressionAttributeValues={':val1': random_choices, ':val2': fetched_location_fromdb}  # Replace with your attribute values
        )
        topic_arn=get_topic_arn_by_name(location.lower())
        report=subscribe_email_to_topic(email, topic_arn)
        output="new location : "+location+" has been added to your subscription . please check your email and confirm it "
        
    else:
        # If the email does not exist, insert a new record with the data
        table.put_item(Item={'email': email, 'weathers': random_choices, 'location': location_list})  # Replace with your attribute names and values
        topic_arn=get_topic_arn_by_name(location.lower())
        report=subscribe_email_to_topic(email, topic_arn)
        output= "you are subscribed to weather update for location: "+location+" . please check your email and confirm it "

    return {
        'statusCode': 200,
        'headers': {
                'Access-Control-Allow-Origin': '*',  # Replace * with your frontend URL for production use
                'Content-Type': 'application/json',
         },
        'body': json.dumps(output)
    }


def subscribe_email_to_topic(email_address, topic_arn):
    # Send verification email and subscribe the email address to the specified topic
    sns_client = boto3.client('sns', region_name='us-east-1')
    response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email_address
    )

    subscription_arn = response['SubscriptionArn']
    return subscription_arn

def get_topic_arn_by_name(topic_name):
    sns_client = boto3.client('sns', region_name='us-east-1')
    response = sns_client.list_topics()
    topics = response['Topics']
    
    for topic in topics:
        if topic_name in topic['TopicArn']:
            return topic['TopicArn']
    
    # If the topic doesn't exist, create a new one
    response = sns_client.create_topic(Name=topic_name)
    return response['TopicArn']