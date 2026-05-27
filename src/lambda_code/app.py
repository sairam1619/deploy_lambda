import json
import boto3
import os
import sys
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta

s3_client = boto3.client('s3')

# Connection to DynamoDB Table
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tracker_table = dynamodb.Table('cmp-jobs-tracker-v3')
invokeLambda = boto3.client('lambda', region_name='us-west-2')

ses_client = boto3.client('ses', region_name="us-west-2")
SENDER = "DataDelivers CMP <noreply@cmp.io>"  
RECIPIENT = ["ramu@datadelivers.com","PST@datadelivers.com","jodonnell@datadelivers.com","santhu@datadelivers.com"]

def load_dynamo_config(client_name):
	response = invokeLambda.invoke(FunctionName = env +'-cog-generic-load-config-v3',   
						InvocationType = 'RequestResponse', 
						Payload = json.dumps({"client_name": client_name})
						)
	return response['Payload'].read()

def init_env(context):
	global env 
	aws_account_id = context.invoked_function_arn.split(":")[4]
	env = 'dev' if aws_account_id == '743020291706' else 'prod' 
	print(aws_account_id , '--->', env ) 
	
def update_stage(client_name, stage):
	tracker_table.update_item(
		Key = {"client_id": client_name},         
		UpdateExpression='SET stage = :val1 ', 
		ExpressionAttributeValues={':val1': stage})
	
def stage_check(client_name, stage):

    # Stage Check 
	current_stage = 'DataStatusCheckInLandingZone' 
	if stage == current_stage :
		# Passing stage as none
		update_stage(client_name, 'none')
		return True
	elif stage != current_stage and stage != 'none': 
        # Passing the input stage 
		update_stage(client_name, stage)
		return False
	

class MissingFilesInLandingZone(Exception):
	pass
class RepeatedDataInLandingZone(Exception):
	pass


def lambda_handler(event, context):
	
	print("event :",event) 
	client_name = event['client_name']
	Execution_Id = event['Execution_Id']
	stage = event['stage']
	ready_file_date = event['ready_file_date']
	
    # initialize env variable
	init_env(context)

    
	# Get client configurations 
	res_data = json.loads(load_dynamo_config(event['client_name']))
	processing_date = res_data['landing_processing_date']
	print('processing_date is ', processing_date)

	# Stage Check 
	if not stage_check(client_name, stage):
		return {'client_name' : client_name , 'processing_date' : processing_date ,'Execution_Id': Execution_Id }
	
	# Checking if the ready file date is different from the processing_date 
	if ready_file_date != processing_date.replace('-','') : 
		raise MissingFilesInLandingZone('''The ready file date ({ready_file_date}) and the processing_date ({processing_date}) is not matching , moving files to temp location!!'''.format(ready_file_date = ready_file_date, processing_date = processing_date))
		

	# invoking a lambda function on Monday, Saturday, and Sunday
	if "demo_refresh" in res_data:
		
        # Determine current day
		current_time = datetime.now()
		current_day = current_time.strftime('%A')
		
		if current_day not in ['Monday', 'Saturday', 'Sunday'] and res_data["demo_refresh"] == True :
			response = invokeLambda.invoke(
				FunctionName='demo-2024',
				InvocationType='Event',
				Payload=json.dumps({"client_name": "demo2024"})
			)
			print("Lambda function 'demo2024' invoked successfully. Response:", response)
		
	
	bucket_name = res_data['bucket_name']
	landing_prefix = res_data['landing_prefix']
	refined_prefix = res_data['refined_prefix']
	table_names_source = res_data['expected_tables']
	print('table_names_source are ', table_names_source)
	
	model = res_data['model']

	try:
		if model == 'restaurant_v3':
			# Table names from landing zone
			response = s3_client.list_objects(
				Bucket=bucket_name,
				Delimiter='/',
				MaxKeys=60,  
				Prefix=landing_prefix + processing_date + '/')
			print("response is ", response)
			prefixes = []
			if 'CommonPrefixes' in response:
				prefixes = response['CommonPrefixes']
			
			# Capture table names from the folder names
			table_names = []
			if len(prefixes) > 0:
				table_names = [prefix['Prefix'].split('/')[-2] for prefix in prefixes]
			
			tables_length = len(table_names) # count of received files 
			print("count of files received :", tables_length)

			# Extract processed dates from refined zone
			prefix = refined_prefix +'daily/' + 'date=''' 
			print('bucket_name and prefix is ', bucket_name, prefix)
			
			refined_dates = []
			Response = s3_client.list_objects(
				Bucket=bucket_name,
				Delimiter='/',
				Prefix=prefix)
			print('Response is',Response)
	
			prefixes = []
			if 'CommonPrefixes' in Response:
				prefixes = Response['CommonPrefixes']
				print('length is ',len(prefixes))
			if len(prefixes) > 0:
				refined_dates = [prefix['Prefix'].split('/')[-2].split("=")[1] for prefix in prefixes]
			print('refined_dates are ', refined_dates)
			
			total_table_count = len(table_names_source) # expected table count 
			missing_tables_list = list(set(table_names_source) - set(table_names))
			missing_tables = ', '.join(i for i in sorted(missing_tables_list))
			
			extra_tables_list = list(set(table_names) - set(table_names_source))
			extra_tables = ', '.join(i for i in sorted(extra_tables_list))
			print("Missing files in the spool ", missing_tables)
			print("Extra files in the spool ",extra_tables)
			print(tables_length)
			
			
			if (processing_date not in refined_dates): 
				if len(missing_tables_list) == 0 : 
					print('Data is good to process for the date ', processing_date)
					if len(extra_tables_list) > 0 :
						send_notification(client_name,extra_tables,processing_date)
						print("Received new files in the spool :", extra_tables) 
						
				else:
					raise MissingFilesInLandingZone('Please check data in landing zone. It seems {missing_tables} files are missing for the {processing_date}'.format(missing_tables=missing_tables, processing_date=processing_date))
			else:
				raise RepeatedDataInLandingZone('Please check data in landing zone. It seems data is already processed for date {processing_date}'.format(processing_date=processing_date))
					
	except Exception as e:
		print(e)
		raise e
	
	return {'client_name': client_name, 'processing_date': processing_date , 'Execution_Id': Execution_Id}

def send_notification(client_name,extra_tables,processing_date) :
	CHARSET = "UTF-8"
	try:
		SUBJECT = "Received New Files In Landing For {client_name}".format(client_name = client_name )
		BODY_TEXT = "{env}: Received the following new files in {client_name}'s landing location for {processing_date} processing_date.Please check the landing location! : {extra_tables} ".format(client_name = client_name, processing_date = processing_date, extra_tables = extra_tables, env = env.title())
		#Provide the contents of the email.
		response = ses_client.send_email(
			Destination={
				'ToAddresses':
					RECIPIENT,
			},
			Message={
				'Body': {
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
			Source=SENDER,
		)
	except Exception as e:
		print(e.response['Error']['Message'])
		raise e