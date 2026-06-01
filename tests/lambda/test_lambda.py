import unittest
from unittest.mock import MagicMock, patch
import json
import io

# Assuming your original file is named 'lambda_function.py'
import lambda_function 

class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        # Mock context object
        self.context = MagicMock()
        self.context.invoked_function_arn = "arn:aws:lambda:us-west-2:743020291706:function:dev-my-function"
        
        # Sample event
        self.event = {
            'Execution_Id': 'exec-123',
            'processing_date': '2026-06-01',
            'client_name': 'test-client'
        }

    @patch('lambda_function.dynamo_table')
    @patch('lambda_function.invokeLambda')
    def test_lambda_handler_success(self, mock_lambda, mock_dynamo):
        # Setup mocks
        # Mock load_dynamo_config response
        config_data = json.dumps({"stage": "GCFStatusCheckLambda"}).encode('utf-8')
        mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_data)}
        
        # Mock DynamoDB scan response
        mock_dynamo.scan.return_value = {
            'Items': [{'gcf_status': 'Completed', 'gcd_status': 'Completed'}]
        }

        # Run handler
        result = lambda_function.lambda_handler(self.event, self.context)

        # Assertions
        self.assertEqual(result['client_name'], 'test-client')
        mock_dynamo.update_item.assert_called_once()

    @patch('lambda_function.dynamo_table')
    @patch('lambda_function.invokeLambda')
    def test_lambda_handler_failure(self, mock_lambda, mock_dynamo):
        # Setup mocks
        config_data = json.dumps({"stage": "OtherStage"}).encode('utf-8')
        mock_lambda.invoke.return_value = {'Payload': io.BytesIO(config_data)}
        
        # Simulate failed status check
        mock_dynamo.scan.return_value = {
            'Items': [{'gcf_status': 'Failed', 'gcd_status': 'Completed'}]
        }

        # Verify custom exception is raised
        with self.assertRaises(lambda_function.GCFStatusCheckFailedException):
            lambda_function.lambda_handler(self.event, self.context)

if __name__ == '__main__':
    unittest.main()
