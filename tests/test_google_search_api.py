"""
Unit tests for google_search_api Lambda function.
"""
import unittest
import json
import sys
import os
from unittest.mock import patch, Mock, mock_open

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from google_search_api import lambda_handler, perform_google_search, extract_urls_from_results


class TestGoogleSearchApi(unittest.TestCase):
    """Test cases for google_search_api Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
        self.mock_api_key = 'test_api_key'
        self.mock_search_engine_id = 'test_search_engine_id'
        
        # Mock Google API response
        self.mock_search_results = {
            'items': [
                {'link': 'https://example1.com'},
                {'link': 'https://example2.com'},
                {'link': 'https://example3.com'},
                {'link': 'https://example4.com'},
                {'link': 'https://example5.com'}
            ]
        }
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_api_key', 'GOOGLE_SEARCH_ENGINE_ID': 'test_search_engine_id'})
    @patch('google_search_api.perform_google_search')
    def test_successful_search(self, mock_perform_search):
        """Test successful Google search with valid search word."""
        mock_perform_search.return_value = self.mock_search_results
        
        event = {
            'searchWord': 'python programming'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'python programming')
        self.assertEqual(len(response['urls']), 5)
        self.assertEqual(response['urls'][0], 'https://example1.com')
        
        body = json.loads(response['body'])
        self.assertEqual(body['searchWord'], 'python programming')
        self.assertEqual(len(body['urls']), 5)
        self.assertIn('Found 5 search results', body['message'])
    
    def test_missing_search_word(self):
        """Test handling of missing search word."""
        event = {
            'otherKey': 'some value'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Search word not found in input')
        self.assertIsNone(body['searchWord'])
        self.assertEqual(body['urls'], [])
    
    def test_empty_search_word(self):
        """Test handling of empty search word."""
        event = {
            'searchWord': ''
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Search word not found in input')
        self.assertIsNone(body['searchWord'])
        self.assertEqual(body['urls'], [])
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_configuration(self):
        """Test handling of missing Google API configuration."""
        event = {
            'searchWord': 'test search'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Google API configuration not found')
        self.assertEqual(body['searchWord'], 'test search')
        self.assertEqual(body['urls'], [])
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_api_key', 'GOOGLE_SEARCH_ENGINE_ID': 'test_search_engine_id'})
    @patch('google_search_api.perform_google_search')
    def test_google_search_failure(self, mock_perform_search):
        """Test handling of Google search API failure."""
        mock_perform_search.return_value = None
        
        event = {
            'searchWord': 'test search'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Failed to perform Google search')
        self.assertEqual(body['searchWord'], 'test search')
        self.assertEqual(body['urls'], [])
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_api_key', 'GOOGLE_SEARCH_ENGINE_ID': 'test_search_engine_id'})
    @patch('google_search_api.perform_google_search')
    def test_japanese_search_word(self, mock_perform_search):
        """Test handling of Japanese search words."""
        mock_perform_search.return_value = self.mock_search_results
        
        event = {
            'searchWord': 'プログラミング 学習'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'プログラミング 学習')
        self.assertEqual(len(response['urls']), 5)
        
        body = json.loads(response['body'])
        self.assertEqual(body['searchWord'], 'プログラミング 学習')
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Internal server error', body['error'])
        self.assertIsNone(body['searchWord'])
        self.assertEqual(body['urls'], [])
    
    def test_extract_urls_from_results(self):
        """Test URL extraction from Google search results."""
        urls = extract_urls_from_results(self.mock_search_results)
        
        self.assertEqual(len(urls), 5)
        self.assertEqual(urls[0], 'https://example1.com')
        self.assertEqual(urls[4], 'https://example5.com')
    
    def test_extract_urls_from_empty_results(self):
        """Test URL extraction from empty search results."""
        empty_results = {'items': []}
        urls = extract_urls_from_results(empty_results)
        
        self.assertEqual(len(urls), 0)
        self.assertEqual(urls, [])
    
    def test_extract_urls_from_partial_results(self):
        """Test URL extraction from search results with only 3 items."""
        partial_results = {
            'items': [
                {'link': 'https://example1.com'},
                {'link': 'https://example2.com'},
                {'link': 'https://example3.com'}
            ]
        }
        
        urls = extract_urls_from_results(partial_results)
        
        self.assertEqual(len(urls), 3)
        self.assertEqual(urls[0], 'https://example1.com')
        self.assertEqual(urls[2], 'https://example3.com')
    
    def test_extract_urls_with_missing_links(self):
        """Test URL extraction from results with some missing links."""
        results_with_missing_links = {
            'items': [
                {'link': 'https://example1.com'},
                {'title': 'No link here'},
                {'link': 'https://example3.com'},
                {},
                {'link': 'https://example5.com'}
            ]
        }
        
        urls = extract_urls_from_results(results_with_missing_links)
        
        # Should only extract valid URLs
        self.assertEqual(len(urls), 3)
        self.assertEqual(urls[0], 'https://example1.com')
        self.assertEqual(urls[1], 'https://example3.com')
        self.assertEqual(urls[2], 'https://example5.com')
    
    @patch('urllib.request.urlopen')
    def test_perform_google_search_success(self, mock_urlopen):
        """Test successful Google search API call."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(self.mock_search_results).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = perform_google_search('test search', self.mock_api_key, self.mock_search_engine_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['items']), 5)
        self.assertEqual(result['items'][0]['link'], 'https://example1.com')
    
    @patch('urllib.request.urlopen')
    def test_perform_google_search_http_error(self, mock_urlopen):
        """Test Google search API HTTP error handling."""
        from urllib.error import HTTPError
        
        mock_urlopen.side_effect = HTTPError(
            url='test_url', 
            code=403, 
            msg='Forbidden', 
            hdrs={}, 
            fp=None
        )
        
        result = perform_google_search('test search', self.mock_api_key, self.mock_search_engine_id)
        
        self.assertIsNone(result)
    
    @patch('urllib.request.urlopen')
    def test_perform_google_search_invalid_json(self, mock_urlopen):
        """Test Google search API invalid JSON response handling."""
        # Mock HTTP response with invalid JSON
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = b'invalid json response'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = perform_google_search('test search', self.mock_api_key, self.mock_search_engine_id)
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()