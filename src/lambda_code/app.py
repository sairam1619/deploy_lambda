import os
import time
import boto3
import json
from botocore.exceptions import ClientError 
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
dynamo_table = dynamodb.Table('cmp-jobs-tracker-v3') 
invokeLambda = boto3.client('lambda', region_name='us-west-2')

def load_dynamo_config(client_name,aws_account_id):
    response = invokeLambda.invoke(FunctionName = 'arn:aws:lambda:us-west-2:' + aws_account_id + ':function:' + env +'-cog-generic-load-config-v3',   
                        InvocationType = 'RequestResponse', 
                        Payload = json.dumps({"client_name": client_name})
                        )
    return response['Payload'].read()

def lambda_handler(event, context):
    # time.sleep(30)
    Execution_Id = event['Execution_Id']
    processing_date = event['processing_date'] 
    client_name = event['client_name']

    aws_account_id = context.invoked_function_arn.split(":")[4]
    global env
    env = 'dev' if aws_account_id == '743020291706' else 'prod' 
    print(aws_account_id , '--->', env ) 
    res_data = json.loads(load_dynamo_config(event['client_name'], aws_account_id))

    stage = res_data['stage']
    current_stage = "GCFStatusCheckLambda"  
    
    if stage == current_stage :
        stage ='none'
        dynamo_table.update_item( 
            Key = {"client_id": client_name},         
            UpdateExpression='SET stage = :val1 ',  
            ExpressionAttributeValues={':val1': stage})

    elif stage != current_stage and stage != 'none': 
        return {'client_name': client_name , 'Execution_Id': Execution_Id, 'processing_date': processing_date}  
    
    class GCFStatusCheckFailedException(Exception):
        pass

    response = dynamo_table.scan(FilterExpression=Attr('client_id').eq(client_name))
    print("stage_response :",response) 
    gcf_status = response['Items'][0]['gcf_status']  
    gcd_status = response['Items'][0]['gcd_status']
    
    if gcf_status == gcd_status == "Completed" : 
        print("GCF status check passed ")
    else :
        raise GCFStatusCheckFailedException("GCF status check failed ") 

    return {'client_name': client_name , 'Execution_Id': Execution_Id, 'processing_date': processing_date} 
