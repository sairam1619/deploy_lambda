import pytest
import os
import json
from unittest.mock import patch

# Import your handler
from src.lambda_code.app import lambda_handler

class UniversalEvent(dict):
    """A dictionary that returns an empty string instead of KeyError."""
    def __getitem__(self, key):
        return self.get(key, "test-value")

def test_lambda_handler_generic():
    """
    Universal test: Works for any Lambda, ignores env vars, 
    and handles JSON serialization without crashes.
    """
    # 1. Mock Environment Variables
    with patch.dict(os.environ, {"AWS_REGION": "us-west-2"}, clear=True):
        
        # 2. Arrange: Use our UniversalEvent container
        mock_event = UniversalEvent()
        mock_context = {}

        # 3. Act: Invoke the handler
        try:
            response = lambda_handler(mock_event, mock_context)
            
            # 4. Assert: Validate the response structure
            assert "statusCode" in response
            assert isinstance(response["statusCode"], int)
            
            # Verify the body can be parsed as JSON
            body = json.loads(response["body"])
            assert isinstance(body, dict)
            
        except Exception as e:
            pytest.fail(f"Lambda handler failed with error: {e}")
