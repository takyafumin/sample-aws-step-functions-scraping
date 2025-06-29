"""
Manual test script for sheets_url_recorder Lambda function.
"""
import sys
import os
import json

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'lambda'))

from sheets_url_recorder import lambda_handler


class MockContext:
    """Mock Lambda context for testing."""
    def __init__(self):
        self.function_name = 'sheets-url-recorder'
        self.aws_request_id = 'test-request-id'


def test_manual():
    """Manual test for the sheets_url_recorder function."""
    context = MockContext()
    
    print("=" * 60)
    print("Manual test for sheets_url_recorder Lambda function")
    print("=" * 60)
    
    # Test 1: Missing URL
    print("\n1. Testing missing URL:")
    event1 = {
        'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890'
    }
    response1 = lambda_handler(event1, context)
    print(f"Status Code: {response1['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response1['body']), indent=2)}")
    
    # Test 2: Missing spreadsheet ID
    print("\n2. Testing missing spreadsheet ID:")
    event2 = {
        'url': 'https://drive.google.com/file/d/1234567890/view'
    }
    response2 = lambda_handler(event2, context)
    print(f"Status Code: {response2['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response2['body']), indent=2)}")
    
    # Test 3: Google Sheets service unavailable (expected in test environment)
    print("\n3. Testing with valid input (Google Sheets service unavailable in test environment):")
    event3 = {
        'url': 'https://drive.google.com/file/d/1234567890/view',
        'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890',
        'sheet_range': 'Sheet1!A:F',
        'additional_data': {
            'filename': 'test_document.pdf',
            'file_id': '1234567890',
            'file_size': '1024000',
            'description': 'Test document'
        }
    }
    response3 = lambda_handler(event3, context)
    print(f"Status Code: {response3['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response3['body']), indent=2)}")
    
    print("\n" + "=" * 60)
    print("Manual test completed!")
    print("Note: In a real AWS environment with proper Google Sheets credentials,")
    print("the third test would successfully record the URL to the spreadsheet.")
    print("=" * 60)


if __name__ == '__main__':
    test_manual()