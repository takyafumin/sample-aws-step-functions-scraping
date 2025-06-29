"""
Unit tests for search_word_receiver Lambda function.
"""
import unittest
import json
import sys
import os

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from search_word_receiver import lambda_handler


class TestSearchWordReceiver(unittest.TestCase):
    """Test cases for search_word_receiver Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
    
    def test_successful_search_word_extraction(self):
        """Test successful extraction of search word from event."""
        event = {
            'searchWord': 'python programming'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'python programming')
        
        body = json.loads(response['body'])
        self.assertEqual(body['searchWord'], 'python programming')
        self.assertEqual(body['message'], 'Search word received successfully')
    
    def test_empty_search_word(self):
        """Test handling of empty search word."""
        event = {
            'searchWord': ''
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIsNone(body['searchWord'])
    
    def test_missing_search_word_key(self):
        """Test handling of missing searchWord key in event."""
        event = {
            'otherKey': 'some value'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Search word not found in input')
        self.assertIsNone(body['searchWord'])
    
    def test_complex_search_word(self):
        """Test handling of complex search words with special characters."""
        event = {
            'searchWord': 'AWS Lambda & Step Functions 2024'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'AWS Lambda & Step Functions 2024')
        
        body = json.loads(response['body'])
        self.assertEqual(body['searchWord'], 'AWS Lambda & Step Functions 2024')
    
    def test_japanese_search_word(self):
        """Test handling of Japanese search words."""
        event = {
            'searchWord': 'プログラミング 学習'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'プログラミング 学習')
        
        body = json.loads(response['body'])
        self.assertEqual(body['searchWord'], 'プログラミング 学習')
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        # This test simulates an exception during processing
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])
        self.assertIsNone(body['searchWord'])


if __name__ == '__main__':
    unittest.main()