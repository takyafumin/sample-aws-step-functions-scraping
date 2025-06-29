"""
Unit tests for page_capture Lambda function.
"""
import unittest
import json
import sys
import os
import tempfile
import base64

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from page_capture import lambda_handler, capture_page_screenshot, create_placeholder_image


class TestPageCapture(unittest.TestCase):
    """Test cases for page_capture Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
    
    def test_successful_url_capture(self):
        """Test successful capture of a valid URL."""
        event = {
            'url': 'https://example.com'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['url'], 'https://example.com')
        self.assertIsNotNone(response['imagePath'])
        self.assertIsNotNone(response['imageData'])
        
        body = json.loads(response['body'])
        self.assertEqual(body['url'], 'https://example.com')
        self.assertEqual(body['message'], 'Page screenshot captured successfully')
        
        # Verify image file exists and is not empty
        image_path = response['imagePath']
        self.assertTrue(os.path.exists(image_path))
        self.assertGreater(os.path.getsize(image_path), 0)
        
        # Verify base64 data is valid
        image_data = response['imageData']
        self.assertIsInstance(image_data, str)
        self.assertGreater(len(image_data), 0)
        
        # Test base64 decoding works
        try:
            decoded_data = base64.b64decode(image_data)
            self.assertGreater(len(decoded_data), 0)
        except Exception as e:
            self.fail(f"Base64 decoding failed: {e}")
    
    def test_missing_url(self):
        """Test handling of missing URL in event."""
        event = {
            'otherKey': 'some value'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'URL not found in input')
        self.assertIsNone(body['imageData'])
        self.assertIsNone(body['imagePath'])
    
    def test_empty_url(self):
        """Test handling of empty URL."""
        event = {
            'url': ''
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIsNone(body['imageData'])
        self.assertIsNone(body['imagePath'])
    
    def test_invalid_url_format(self):
        """Test handling of invalid URL format."""
        event = {
            'url': 'not-a-valid-url'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Invalid URL format', body['error'])
        self.assertIsNone(body['imageData'])
    
    def test_various_valid_urls(self):
        """Test handling of various valid URL formats."""
        valid_urls = [
            'https://www.google.com',
            'http://example.org',
            'https://github.com/user/repo',
            'https://subdomain.example.com/path?param=value'
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                event = {'url': url}
                response = lambda_handler(event, self.context)
                
                self.assertEqual(response['statusCode'], 200)
                self.assertEqual(response['url'], url)
                self.assertIsNotNone(response['imagePath'])
                self.assertIsNotNone(response['imageData'])
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])
        self.assertIsNone(body['imageData'])
        self.assertIsNone(body['imagePath'])
    
    def test_capture_page_screenshot_function(self):
        """Test the capture_page_screenshot function directly."""
        url = 'https://test.example.com'
        
        image_path, image_data = capture_page_screenshot(url)
        
        # Verify file was created
        self.assertIsNotNone(image_path)
        self.assertTrue(os.path.exists(image_path))
        self.assertGreater(os.path.getsize(image_path), 0)
        
        # Verify base64 data
        self.assertIsInstance(image_data, str)
        self.assertGreater(len(image_data), 0)
        
        # Verify base64 decoding
        decoded_data = base64.b64decode(image_data)
        self.assertGreater(len(decoded_data), 0)
        
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)
    
    def test_create_placeholder_image_function(self):
        """Test the create_placeholder_image function directly."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            url = 'https://test.example.com'
            create_placeholder_image(temp_path, url)
            
            # Verify file was created and has content
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_japanese_url(self):
        """Test handling of URLs with Japanese domains/paths."""
        event = {
            'url': 'https://example.co.jp/パス'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['url'], 'https://example.co.jp/パス')
        self.assertIsNotNone(response['imagePath'])
        self.assertIsNotNone(response['imageData'])


if __name__ == '__main__':
    unittest.main()