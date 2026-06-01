import json
# Replace 'your_file_name' with the actual name of your python file
from src.lambda_code.app import lambda_handler 

def test_lambda_handler():
    # 1. Arrange: Provide the data the function expects
    mock_event = {
        "Execution_Id": "test-123-abc",
        "processing_date": "02-01-2024",
        "client_name": "bajafresh"# Add the missing key here
    }
    mock_context = {}

    # 2. Act: Call the function
    response = lambda_handler(mock_event, mock_context)

    # 3. Assert
    assert response["statusCode"] == 200
    # ... rest of your assertions
