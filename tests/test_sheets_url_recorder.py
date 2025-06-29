"""
Unit tests for sheets_url_recorder Lambda function.
"""
import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from sheets_url_recorder import lambda_handler, get_sheets_service, write_url_to_sheet


class TestSheetsUrlRecorder(unittest.TestCase):
    """Test cases for sheets_url_recorder Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = Mock()
        self.context.function_name = 'sheets-url-recorder'
        self.context.aws_request_id = 'test-request-id'
    
    def test_successful_url_recording(self):
        """Test successful recording of URL to Google Sheets."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view',
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890',
            'sheet_range': 'Sheet1!A:F'
        }
        
        with patch('sheets_url_recorder.get_sheets_service') as mock_get_service, \
             patch('sheets_url_recorder.write_url_to_sheet') as mock_write:
            
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_write.return_value = True
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(response['url'], event['url'])
            self.assertEqual(response['spreadsheet_id'], event['spreadsheet_id'])
            self.assertTrue(response['success'])
            
            body = json.loads(response['body'])
            self.assertEqual(body['message'], 'URL recorded successfully')
            self.assertTrue(body['success'])
            
            # Verify the service was called correctly
            mock_get_service.assert_called_once()
            mock_write.assert_called_once_with(
                mock_service, 
                event['spreadsheet_id'], 
                event['sheet_range'], 
                event['url'], 
                {}
            )
    
    def test_missing_url(self):
        """Test handling of missing URL in event."""
        event = {
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'URL not found in input')
        self.assertFalse(body['success'])
    
    def test_missing_spreadsheet_id(self):
        """Test handling of missing spreadsheet ID in event."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Spreadsheet ID not found in input')
        self.assertFalse(body['success'])
    
    def test_google_sheets_service_unavailable(self):
        """Test handling when Google Sheets service is unavailable."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view',
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890'
        }
        
        with patch('sheets_url_recorder.get_sheets_service') as mock_get_service:
            mock_get_service.return_value = None
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 503)
            
            body = json.loads(response['body'])
            self.assertIn('error', body)
            self.assertEqual(body['error'], 'Google Sheets service unavailable')
            self.assertFalse(body['success'])
    
    def test_write_url_failure(self):
        """Test handling when writing URL to sheet fails."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view',
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890'
        }
        
        with patch('sheets_url_recorder.get_sheets_service') as mock_get_service, \
             patch('sheets_url_recorder.write_url_to_sheet') as mock_write:
            
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_write.return_value = False
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 500)
            
            body = json.loads(response['body'])
            self.assertIn('error', body)
            self.assertEqual(body['error'], 'Failed to record URL to spreadsheet')
            self.assertFalse(body['success'])
    
    def test_with_additional_data(self):
        """Test URL recording with additional data."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view',
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890',
            'additional_data': {
                'filename': 'test_document.pdf',
                'file_id': '1234567890',
                'file_size': '1024000',
                'description': 'Test document'
            }
        }
        
        with patch('sheets_url_recorder.get_sheets_service') as mock_get_service, \
             patch('sheets_url_recorder.write_url_to_sheet') as mock_write:
            
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_write.return_value = True
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 200)
            self.assertTrue(response['success'])
            
            # Verify additional data was passed correctly
            mock_write.assert_called_once_with(
                mock_service,
                event['spreadsheet_id'],
                'Sheet1!A:F',  # Default range
                event['url'],
                event['additional_data']
            )
    
    def test_default_sheet_range(self):
        """Test that default sheet range is used when not specified."""
        event = {
            'url': 'https://drive.google.com/file/d/1234567890/view',
            'spreadsheet_id': '1abcdefghijklmnopqrstuvwxyz1234567890'
        }
        
        with patch('sheets_url_recorder.get_sheets_service') as mock_get_service, \
             patch('sheets_url_recorder.write_url_to_sheet') as mock_write:
            
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_write.return_value = True
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 200)
            
            # Verify default range was used
            mock_write.assert_called_once_with(
                mock_service,
                event['spreadsheet_id'],
                'Sheet1!A:F',  # Default range
                event['url'],
                {}
            )
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])
        self.assertFalse(body['success'])
    
    @patch('sheets_url_recorder.GOOGLE_APIS_AVAILABLE', False)
    def test_get_sheets_service_no_google_apis(self):
        """Test get_sheets_service when Google APIs are not available."""
        service = get_sheets_service()
        self.assertIsNone(service)
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('sheets_url_recorder.GOOGLE_APIS_AVAILABLE', True)
    def test_get_sheets_service_no_credentials(self):
        """Test get_sheets_service when credentials are not available."""
        service = get_sheets_service()
        self.assertIsNone(service)
    
    @patch('sheets_url_recorder.GOOGLE_APIS_AVAILABLE', True)
    @patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': '{"type": "service_account", "project_id": "test"}'})
    def test_get_sheets_service_success(self):
        """Test successful creation of Google Sheets service."""
        # This test requires Google APIs to be available, so we'll skip it if not
        try:
            from sheets_url_recorder import service_account, build
        except ImportError:
            self.skipTest("Google APIs not available for testing")
        
        with patch('sheets_url_recorder.service_account') as mock_service_account, \
             patch('sheets_url_recorder.build') as mock_build:
            
            mock_credentials = Mock()
            mock_service_account.Credentials.from_service_account_info.return_value = mock_credentials
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            service = get_sheets_service()
            
            self.assertEqual(service, mock_service)
            mock_service_account.Credentials.from_service_account_info.assert_called_once()
            mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_credentials)
    
    def test_write_url_to_sheet_no_service(self):
        """Test write_url_to_sheet when service is None."""
        result = write_url_to_sheet(None, 'spreadsheet_id', 'Sheet1!A:F', 'http://example.com')
        self.assertFalse(result)
    
    @patch('datetime.datetime')
    def test_write_url_to_sheet_success(self, mock_datetime):
        """Test successful writing of URL to sheet."""
        # Mock datetime
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-01T00:00:00'
        
        # Mock service
        mock_service = Mock()
        mock_spreadsheets = Mock()
        mock_values = Mock()
        mock_append = Mock()
        mock_execute = Mock()
        
        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_spreadsheets.values.return_value = mock_values
        mock_values.append.return_value = mock_append
        mock_append.execute.return_value = {'updates': {'updatedRange': 'Sheet1!A2:F2'}}
        
        additional_data = {
            'filename': 'test.pdf',
            'file_id': '123',
            'file_size': '1024',
            'description': 'Test file'
        }
        
        result = write_url_to_sheet(
            mock_service, 
            'spreadsheet_id', 
            'Sheet1!A:F', 
            'http://example.com',
            additional_data
        )
        
        self.assertTrue(result)
        
        # Verify the API call was made correctly
        expected_body = {
            'values': [['2023-01-01T00:00:00Z', 'http://example.com', 'test.pdf', '123', '1024', 'Test file']]
        }
        
        mock_values.append.assert_called_once_with(
            spreadsheetId='spreadsheet_id',
            range='Sheet1!A:F',
            valueInputOption='RAW',
            body=expected_body
        )


if __name__ == '__main__':
    unittest.main()