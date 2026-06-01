import pytest
import os
from unittest.mock import MagicMock, patch

# This assumes we will pass the module path as an argument or 
# you can use a conftest.py approach. For simplicity, we define the import.
from src.lambda_code.app import lambda_handler

def test_lambda_handler_generic():
    """
    Universal test that mocks environment variables and 
    handles any event structure without modification.
    """
    
    # 1. Mock Environment Variables: 
    # This automatically clears/fakes all env vars so your code doesn't crash 
    # when looking for them.
    with patch.dict(os.environ, {"AWS_REGION": "us-west-2", "DUMMY_VAR": "true"}, clear=True):
        
        # 2. Arrange: Create a generic event. 
        # Using MagicMock allows your code to access any key (event['any'])
        # without raising a KeyError.
        mock_event = MagicMock()
        mock_context = MagicMock()

        # 3. Act: Invoke the handler
        # If your code expects dictionary-like access, MagicMock handles it.
        try:
            response = lambda_handler(mock_event, mock_context)
            
            # 4. Assert: We only check for the universal standard: a status code.
            assert "statusCode" in response
            assert isinstance(response["statusCode"], int)
            
        except Exception as e:
            # This catches cases where the Lambda code is fundamentally broken
            pytest.fail(f"Lambda handler failed with error: {e}")
