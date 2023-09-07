import json
import boto3
import requests
from datetime import datetime, timedelta

API_KEY = '5e9e3981db0547b71afd4f1b4c1c74e2'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'
sqs_client = boto3.client('sqs', region_name='us-east-1')

def lambda_handler(event, context):
    query_params = event['queryStringParameters']
    location = query_params['location']
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    queue_url=get_queue_url_by_name('weather_queue')

    try:
        response = requests.get(FORECAST_URL, params=params)
        data = response.json()

        # Filter forecast data for the next 7 days
        forecast_data = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_seven_days = [today + timedelta(days=i) for i in range(1,8)]

        for entry in data['list']:
            
            forecast_date = datetime.strptime(entry['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if forecast_date in next_seven_days:
                forecast_entry = {
                    'date': entry['dt_txt'],
                    'temperature': entry['main']['temp'],
                    'feels_like': entry['main']['feels_like'],
                    'temp_min': entry['main']['temp_min'],
                    'temp_max': entry['main']['temp_max'],
                    'pressure': entry['main']['pressure'],
                    'humidity': entry['main']['humidity'],
                    'wind_speed': entry['wind']['speed'],
                    'weather': entry['weather'][0]['main'],
                    'description': entry['weather'][0]['description'],
                    'location': location.lower()
                    
                }
                for i in range(4):
                    response = sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(forecast_entry)
                    )
                forecast_data.append(forecast_entry)
             
        return  {
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
  
