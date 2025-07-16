import json
import boto3
import uuid
import datetime
import os

dynamodb = boto3.resource('dynamodb')
kinesis = boto3.client('kinesis')

TABLE_NAME = os.environ['TWEET_TABLE_NAME']
KINESIS_STREAM_NAME = os.environ.get('TWEET_STREAM_NAME', 'tweet-stream')

# Header CORS standar
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def lambda_handler(event, context):
    method = event.get('httpMethod')

    # Handle preflight CORS request
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight OK'})
        }

    if method == 'POST':
        try:
            body = json.loads(event['body'])
            tweet_id = str(uuid.uuid4())
            created_at = datetime.datetime.utcnow().isoformat()

            item = {
                'id': tweet_id,
                'username': body['username'],
                'tweet': body['tweet'],
                'created_at': created_at
            }

            # Simpan ke DynamoDB
            table = dynamodb.Table(TABLE_NAME)
            table.put_item(Item=item)

            # Kirim ke Kinesis stream
            kinesis.put_record(
                StreamName=KINESIS_STREAM_NAME,
                Data=json.dumps(item),
                PartitionKey=item['username']
            )

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps(item)
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': str(e)})
            }

    # Jika method tidak didukung
    return {
        'statusCode': 405,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': 'Method not allowed'})
    }
