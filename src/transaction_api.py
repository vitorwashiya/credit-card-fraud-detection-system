import json
import boto3


def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        transaction_data = json.loads(event['body'])
        dynamodb = boto3.resource('dynamodb')
        table_name = 'Transaction'
        table = dynamodb.Table(table_name)
        table.put_item(Item=transaction_data)

        return {
            'statusCode': 200,
            'body': json.dumps('Transaction data loaded into DynamoDB')
        }
    else:
        return {'statusCode': 405, 'body': json.dumps('Method Not Allowed')}
