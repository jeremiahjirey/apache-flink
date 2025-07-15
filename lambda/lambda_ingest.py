import boto3
import json
import os
import uuid
from datetime import datetime

kinesis = boto3.client('kinesis')
STREAM_NAME = os.environ['STREAM_NAME']

def lambda_handler(event, context):
    body = json.loads(event['body'])

    # Tambahkan metadata
    transaction = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": body.get("user_id"),
        "amount": body.get("amount"),
        "region": body.get("region")
    }

    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(transaction),
        PartitionKey=transaction["user_id"]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Transaction received.", "id": transaction["id"]})
    }
