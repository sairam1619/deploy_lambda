import pytest
import json
import io
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to sys.path so 'src' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.lambda_code.app import lambda_handler

@pytest.fixture
def mock_context():
    context = MagicMock()
    # Matches the logic in your code to set env = 'dev'
    context.invoked_function_arn = "arn:aws:lambda:us-west-2:743020291706:function:dev-func"
    return context

@pytest.fixture
def event():
    return {
        'Execution_Id': 'exec-123',
        'processing_date': '2026-06-01',
        'client_name': 'test-client'
    }

@patch('src.lambda_code.app.dynamo_table')
@patch('src.lambda_code.app.invokeLambda')
def test_lambda_handler_success(mock_lambda, mock_dynamo, event, mock_context):
    # 1. Mock Lambda configuration response
    config_response = json.dumps({"stage": "GCFStatusCheckLambda"}).encode('utf-8')
    mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_response)}
    
    # 2. Mock DynamoDB scan response
    mock_dynamo.scan.return_value = {
        'Items': [{'gcf_status': 'Completed', 'gcd_status': 'Completed'}]
    }
    
    # 3. Execute
    response = lambda_handler(event, mock_context)
    
    # 4. Assertions
    assert response['client_name'] == 'test-client'
    mock_dynamo.update_item.assert_called_once()

@patch('src.lambda_code.app.dynamo_table')
@patch('src.lambda_code.app.invokeLambda')
def test_lambda_handler_failed_status(mock_lambda, mock_dynamo, event, mock_context):
    # Mock config
    config_response = json.dumps({"stage": "GCFStatusCheckLambda"}).encode('utf-8')
    mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_response)}
    
    # Mock status mismatch
    mock_dynamo.scan.return_value = {
        'Items': [{'gcf_status': 'Failed', 'gcd_status': 'Completed'}]
    }
    
    # Assert Exception
    with pytest.raises(Exception):
        lambda_handler(event, mock_context)
