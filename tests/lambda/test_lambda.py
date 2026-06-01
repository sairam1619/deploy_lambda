import json
# Replace 'your_file_name' with the actual name of your python file
from src.lambda_code.app.py import lambda_handler 

def test_lambda_handler():
    # 1. Arrange: Setup a dummy event and context
    mock_event = {}
    mock_context = {}

    # 2. Act: Call the function
    response = lambda_handler(mock_event, mock_context)

    # 3. Assert: Verify the response structure and status code
    assert response["statusCode"] == 200
    
    # Parse the JSON body to verify its contents
    body = json.loads(response["body"])
    assert body["message"] == "Hello from AWS Lambda!"
    assert body["status"] == "success"
