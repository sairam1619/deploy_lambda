import pytest
import json
import io
from unittest.mock import MagicMock, patch
# Replace 'main' with the filename of your lambda code
from main import lambda_handler, GCFStatusCheckFailedException

@pytest.fixture
def mock_context():
    context = MagicMock()
    # Simulating the ARN structure to trigger 'dev' environment
    context.invoked_function_arn = "arn:aws:lambda:us-west-2:743020291706:function:dev-func"
    return context

@pytest.fixture
def base_event():
    return {
        'Execution_Id': 'exec-001',
        'processing_date': '2026-06-01',
        'client_name': 'test-client'
    }

@patch('main.dynamo_table')
@patch('main.invokeLambda')
def test_lambda_handler_success(mock_lambda, mock_dynamo, base_event, mock_context):
    # 1. Setup Mock for load_dynamo_config (Lambda call)
    config_response = json.dumps({"stage": "GCFStatusCheckLambda"}).encode('utf-8')
    mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_response)}
    
    # 2. Setup Mock for DynamoDB scan (Status check)
    mock_dynamo.scan.return_value = {
        'Items': [{'gcf_status': 'Completed', 'gcd_status': 'Completed'}]
    }
    
    # 3. Execute
    response = lambda_handler(base_event, mock_context)
    
    # 4. Assert
    assert response['client_name'] == 'test-client'
    mock_dynamo.update_item.assert_called_once()

@patch('main.dynamo_table')
@patch('main.invokeLambda')
def test_lambda_handler_status_mismatch_raises_exception(mock_lambda, mock_dynamo, base_event, mock_context):
    # Setup mock for config
    config_response = json.dumps({"stage": "OtherStage"}).encode('utf-8')
    mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_response)}
    
    # Setup mock for failed DynamoDB status
    mock_dynamo.scan.return_value = {
        'Items': [{'gcf_status': 'InProgress', 'gcd_status': 'Completed'}]
    }
    
    # Assert Exception
    with pytest.raises(GCFStatusCheckFailedException):
        lambda_handler(base_event, mock_context)

@patch('main.dynamo_table')
@patch('main.invokeLambda')
def test_lambda_handler_early_exit(mock_lambda, mock_dynamo, base_event, mock_context):
    # Setup mock for a stage that shouldn't proceed
    config_response = json.dumps({"stage": "SomeOtherStage"}).encode('utf-8')
    mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_response)}
    
    # This should return before reaching the scan/exception logic
    response = lambda_handler(base_event, mock_context)
    
    assert response['Execution_Id'] == 'exec-001'
    mock_dynamo.scan.assert_not_called()
