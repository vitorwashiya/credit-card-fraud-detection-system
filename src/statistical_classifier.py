import json
import boto3
import numpy as np

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Transaction')


def read_model_parameters_from_s3():
    bucket_name = 'credit-card-fraud-detection-system-model-parameters'
    model_parameters_0_file = 'model_parameters_0.json'
    model_parameters_1_file = 'model_parameters_1.json'

    response = s3.get_object(Bucket=bucket_name, Key=model_parameters_0_file)
    model_parameters_0 = json.loads(response['Body'].read().decode('utf-8'))

    response = s3.get_object(Bucket=bucket_name, Key=model_parameters_1_file)
    model_parameters_1 = json.loads(response['Body'].read().decode('utf-8'))
    return model_parameters_0, model_parameters_1


model_parameters_0, model_parameters_1 = read_model_parameters_from_s3()


def classify_transaction(transaction_data):
    transaction_data = {
        k: float(v)
        for k, v in transaction_data.items()
        if k in [f"V{i}" for i in range(1, 29)]
    }

    mu_0 = np.array(model_parameters_0['mu'])
    sigma_0 = np.array(model_parameters_0['sigma'])

    mu_1 = np.array(model_parameters_1['mu'])
    sigma_1 = np.array(model_parameters_1['sigma'])

    x = np.array([v for _, v in transaction_data.items()])

    g = -(x - mu_1).dot(sigma_1).dot(x - mu_1)
    h = -(x - mu_0).dot(sigma_0).dot(x - mu_0)

    return 1 if g > h else 0


def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']
            new_item = {
                k: list(v.values())[0]
                for k, v in new_item.items() if list(v.values())[0]
            }
            new_item["transaction_time"] = int(new_item["transaction_time"])
            new_item['Model'] = classify_transaction(new_item)
            table.put_item(Item=new_item)

    return {'statusCode': 200, 'body': json.dumps('Success')}
