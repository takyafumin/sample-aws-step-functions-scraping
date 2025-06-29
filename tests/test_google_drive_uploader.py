"""
Unit tests for google_drive_uploader Lambda function.
"""
import unittest
import json
import sys
import os
import base64
from unittest.mock import patch, MagicMock, mock_open

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from google_drive_uploader import lambda_handler, upload_image_to_drive, get_drive_service


class TestGoogleDriveUploader(unittest.TestCase):
    """Test cases for google_drive_uploader Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
        # Create a simple test image (1x1 PNG in base64)
        self.test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        self.test_image_data = base64.b64decode(self.test_image_b64)
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    @patch('google_drive_uploader.upload_image_to_drive')
    def test_successful_image_upload(self, mock_upload):
        """Test successful image upload to Google Drive."""
        # Mock successful upload
        mock_upload.return_value = {
            'file_id': 'test_file_id_123',
            'shareable_url': 'https://drive.google.com/file/d/test_file_id_123/view',
            'filename': 'test_image.png'
        }
        
        event = {
            'imageData': self.test_image_b64,
            'filename': 'test_image.png'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['file_id'], 'test_file_id_123')
        self.assertEqual(response['shareable_url'], 'https://drive.google.com/file/d/test_file_id_123/view')
        self.assertEqual(response['filename'], 'test_image.png')
        
        body = json.loads(response['body'])
        self.assertEqual(body['shareable_url'], 'https://drive.google.com/file/d/test_file_id_123/view')
        self.assertEqual(body['message'], 'Image uploaded to Google Drive successfully')
        
        # Verify upload function was called with correct parameters
        mock_upload.assert_called_once_with(self.test_image_data, 'test_image.png', None)
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    @patch('google_drive_uploader.upload_image_to_drive')
    def test_upload_with_folder_id(self, mock_upload):
        """Test image upload with folder ID specified."""
        mock_upload.return_value = {
            'file_id': 'test_file_id_456',
            'shareable_url': 'https://drive.google.com/file/d/test_file_id_456/view',
            'filename': 'folder_image.png'
        }
        
        event = {
            'imageData': self.test_image_b64,
            'filename': 'folder_image.png',
            'folderId': 'test_folder_id'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        mock_upload.assert_called_once_with(self.test_image_data, 'folder_image.png', 'test_folder_id')
    
    def test_missing_image_data(self):
        """Test handling of missing image data."""
        event = {
            'filename': 'test.png'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image data not found in input')
        self.assertIsNone(body['shareable_url'])
    
    def test_empty_image_data(self):
        """Test handling of empty image data."""
        event = {
            'imageData': '',
            'filename': 'test.png'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image data not found in input')
        self.assertIsNone(body['shareable_url'])
    
    def test_invalid_base64_data(self):
        """Test handling of invalid base64 image data."""
        event = {
            'imageData': 'invalid_base64_data!!!',
            'filename': 'test.png'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Invalid base64 image data', body['error'])
        self.assertIsNone(body['shareable_url'])
    
    def test_default_filename(self):
        """Test default filename when not provided."""
        with patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True), \
             patch('google_drive_uploader.upload_image_to_drive') as mock_upload:
            
            mock_upload.return_value = {
                'file_id': 'test_file_id_789',
                'shareable_url': 'https://drive.google.com/file/d/test_file_id_789/view',
                'filename': 'screenshot.png'
            }
            
            event = {
                'imageData': self.test_image_b64
            }
            
            response = lambda_handler(event, self.context)
            
            self.assertEqual(response['statusCode'], 200)
            mock_upload.assert_called_once_with(self.test_image_data, 'screenshot.png', None)
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    @patch('google_drive_uploader.upload_image_to_drive')
    def test_google_drive_upload_failure(self, mock_upload):
        """Test handling of Google Drive upload failure."""
        mock_upload.side_effect = Exception("Drive API error")
        
        event = {
            'imageData': self.test_image_b64,
            'filename': 'test.png'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Failed to upload to Google Drive', body['error'])
        self.assertIsNone(body['shareable_url'])
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])
        self.assertIsNone(body['shareable_url'])
    
    @patch.dict(os.environ, {'GOOGLE_SERVICE_ACCOUNT_KEY': '{"type": "service_account"}'})
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    @patch('google_drive_uploader.build')
    @patch('google_drive_uploader.Credentials')
    def test_get_drive_service_success(self, mock_credentials, mock_build):
        """Test successful Google Drive service creation."""
        # Ensure imports are available for this test
        import google_drive_uploader
        google_drive_uploader.build = mock_build
        google_drive_uploader.Credentials = mock_credentials
        
        mock_creds = MagicMock()
        mock_credentials.from_service_account_info.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = get_drive_service()
        
        self.assertEqual(service, mock_service)
        mock_credentials.from_service_account_info.assert_called_once()
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', False)
    def test_get_drive_service_no_libraries(self):
        """Test Google Drive service creation when libraries not available."""
        with self.assertRaises(ImportError):
            get_drive_service()
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    def test_get_drive_service_no_credentials(self):
        """Test Google Drive service creation without credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                get_drive_service()
    
    @patch.dict(os.environ, {'GOOGLE_SERVICE_ACCOUNT_KEY': 'invalid_json'})
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    def test_get_drive_service_invalid_credentials(self):
        """Test Google Drive service creation with invalid credentials."""
        with self.assertRaises(Exception):
            get_drive_service()
    
    @patch('google_drive_uploader.get_drive_service')
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    def test_upload_image_to_drive_success(self, mock_get_service):
        """Test successful image upload to Google Drive."""
        # Mock Drive service and MediaIoBaseUpload
        import google_drive_uploader
        mock_media_upload = MagicMock()
        google_drive_uploader.MediaIoBaseUpload = MagicMock(return_value=mock_media_upload)
        
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock file creation response
        mock_service.files().create().execute.return_value = {'id': 'test_file_id'}
        
        result = upload_image_to_drive(self.test_image_data, 'test.png')
        
        self.assertEqual(result['file_id'], 'test_file_id')
        self.assertEqual(result['shareable_url'], 'https://drive.google.com/file/d/test_file_id/view')
        self.assertEqual(result['filename'], 'test.png')
        
        # Verify permissions were set
        mock_service.permissions().create.assert_called_once()
    
    @patch('google_drive_uploader.get_drive_service')
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    def test_upload_image_to_drive_with_folder(self, mock_get_service):
        """Test image upload to specific folder."""
        # Mock MediaIoBaseUpload
        import google_drive_uploader
        mock_media_upload = MagicMock()
        google_drive_uploader.MediaIoBaseUpload = MagicMock(return_value=mock_media_upload)
        
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.files().create().execute.return_value = {'id': 'test_file_id'}
        
        upload_image_to_drive(self.test_image_data, 'test.png', 'folder_id')
        
        # Verify create was called with correct parameters
        self.assertTrue(mock_service.files().create.called)
        # Check that the call included the folder_id in parents
        call_args = mock_service.files().create.call_args
        self.assertIn('body', call_args.kwargs)
        self.assertIn('parents', call_args.kwargs['body'])
        self.assertEqual(call_args.kwargs['body']['parents'], ['folder_id'])
    
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', False)
    def test_upload_image_to_drive_no_libraries(self):
        """Test image upload when Google Drive libraries not available."""
        with self.assertRaises(ImportError):
            upload_image_to_drive(self.test_image_data, 'test.png')

    @patch('google_drive_uploader.get_drive_service')
    @patch('google_drive_uploader.GOOGLE_DRIVE_AVAILABLE', True)
    def test_upload_image_to_drive_failure(self, mock_get_service):
        """Test image upload failure."""
        # Mock MediaIoBaseUpload
        import google_drive_uploader
        mock_media_upload = MagicMock()
        google_drive_uploader.MediaIoBaseUpload = MagicMock(return_value=mock_media_upload)
        
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.files().create().execute.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            upload_image_to_drive(self.test_image_data, 'test.png')


if __name__ == '__main__':
    unittest.main()