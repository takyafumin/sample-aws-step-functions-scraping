"""
Unit tests for web_scraper Lambda function.
"""
import unittest
import json
import sys
import os

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from web_scraper import lambda_handler


class TestWebScraper(unittest.TestCase):
    """Test cases for web_scraper Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
    
    def test_successful_scraping(self):
        """Test successful web scraping with valid search word."""
        event = {
            'searchWord': 'python programming'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'python programming')
        self.assertIsInstance(response['scrapedData'], list)
        self.assertGreater(response['itemCount'], 0)
        
        # Check that scraped data has the expected structure
        for item in response['scrapedData']:
            self.assertIn('title', item)
            self.assertIn('url', item)
            self.assertIn('content', item)
            self.assertIn('timestamp', item)
    
    def test_empty_search_word(self):
        """Test handling of empty search word."""
        event = {
            'searchWord': ''
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['scrapedData'], [])
    
    def test_missing_search_word_key(self):
        """Test handling of missing searchWord key in event."""
        event = {
            'otherKey': 'some value'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['scrapedData'], [])
    
    def test_japanese_search_word(self):
        """Test handling of Japanese search words."""
        event = {
            'searchWord': 'プログラミング 学習'
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'プログラミング 学習')
        self.assertIsInstance(response['scrapedData'], list)
        
        # Check that search word appears in scraped content
        found_search_word = False
        for item in response['scrapedData']:
            if 'プログラミング 学習' in item['title'] or 'プログラミング 学習' in item['content']:
                found_search_word = True
                break
        self.assertTrue(found_search_word)
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['scrapedData'], [])


if __name__ == '__main__':
    unittest.main()