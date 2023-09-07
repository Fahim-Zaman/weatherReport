import boto3
import json

queue_url = 'https://sqs.us-east-1.amazonaws.com/038517842892/weather_queue'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:038517842892:'

def send_sns_notification(arn,message,sub):
    sns = boto3.client('sns',region_name='us-east-1')
    sns.publish(TopicArn=arn, Message=message,Subject=sub)
    
def lambda_handler(event, context):
    
    sqs_client = boto3.client('sqs',region_name='us-east-1')

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,  # Maximum number of messages to retrieve in a single call
        VisibilityTimeout=100,    # Time during which the message is hidden from other consumers (in seconds)
        WaitTimeSeconds=7       # Wait time for receiving messages (long polling)
    )
  
    print('start')
    print(response)
    for message in response.get('Messages', []):
        message_body = message['Body']
        receipt_handle = message['ReceiptHandle']
        weather_daily_details = json.loads(message_body)
        print(weather_daily_details)
        # Check if weather_daily_details is not empty
        if weather_daily_details:
            print('hello if')
            print(weather_daily_details)

            arn = SNS_TOPIC_ARN + weather_daily_details['location']
            subject = "Weather details of " + weather_daily_details['location'] + " on " + weather_daily_details['date']
            send_sns_notification(arn, process_the_data(weather_daily_details), subject)

            # Delete the message from the queue to avoid processing it again
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

        else:
            # If weather_daily_details is empty, simply delete the message without further processing
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            print('hello else')
            
    print('end')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def process_the_data(deatils):
    output="Weather update in more details \n"+"Date : "+str(deatils['date'])+"\nTemperature : "+str(deatils['temperature'])+"\nfeels_like : "+str(deatils['feels_like'])+"\ntemp_min : "+str(deatils['temp_min'])+"\ntemp_max : "+str(deatils['temp_max'])+"\npressure : "+str(deatils['pressure'])+"\nhumidity : "+str(deatils['humidity'])+"\nweather : "+str(deatils['weather'])
    
    return output