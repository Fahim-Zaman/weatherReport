import json
import boto3
import requests
from datetime import datetime, timedelta

API_KEY = '5e9e3981db0547b71afd4f1b4c1c74e2'
API_URL = 'http://api.openweathermap.org/data/2.5/weather'
sqs_client = boto3.client('sqs', region_name='us-east-1')

def lambda_handler(event, context):
    location = event.get('queryStringParameters', {}).get('location')
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    queue_url=get_queue_url_by_name('weather_queue')
    forecast_data = []

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()
      
        weather_data = {
            'date':str(datetime.now()),
            'location': data['name'].lower(),
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'weather': data['weather'][0]['description']
        }

        for i in range(7):
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(weather_data)
                 )
        
        forecast_data.append(weather_data)

        return {
        'statusCode': 200,
        'headers': {
                'Access-Control-Allow-Origin': '*',  # Replace * with your frontend URL for production use
                'Content-Type': 'application/json',
         },
        'body': json.dumps(forecast_data)
    }
    
    except Exception as e:
        return{
                'statusCode': 500,
                'headers': {
                        'Access-Control-Allow-Origin': '*',  # Replace * with your frontend URL for production use
                        'Content-Type': 'application/json',
                 },
                'body': json.dumps({'error': str(e)})
            }



def get_queue_url_by_name(queue_name):
    sqs_client = boto3.client('sqs', region_name='us-east-1')
    response = sqs_client.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']
    return queue_url