"""
Unit tests for data_processor Lambda function.
"""
import unittest
import json
import sys
import os

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from data_processor import lambda_handler


class TestDataProcessor(unittest.TestCase):
    """Test cases for data_processor Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
        self.sample_scraped_data = [
            {
                'title': 'Python Programming Tutorial',
                'url': 'https://example.com/python-tutorial',
                'content': 'This is a comprehensive Python programming tutorial for beginners...',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'title': 'Advanced Python Concepts',
                'url': 'https://example.com/advanced-python',
                'content': 'Learn advanced Python programming concepts and techniques...',
                'timestamp': '2024-01-01T11:00:00Z'
            }
        ]
    
    def test_successful_processing(self):
        """Test successful data processing with valid scraped data."""
        event = {
            'searchWord': 'python programming',
            'scrapedData': self.sample_scraped_data
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['searchWord'], 'python programming')
        self.assertIsInstance(response['processedData'], list)
        self.assertGreater(response['itemCount'], 0)
        
        # Check that processed data has the expected structure
        for item in response['processedData']:
            self.assertIn('title', item)
            self.assertIn('url', item)
            self.assertIn('content', item)
            self.assertIn('relevanceScore', item)
            self.assertIn('wordCount', item)
            self.assertIn('processedAt', item)
            self.assertGreaterEqual(item['relevanceScore'], 0)
    
    def test_empty_search_word(self):
        """Test handling of empty search word."""
        event = {
            'searchWord': '',
            'scrapedData': self.sample_scraped_data
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['processedData'], [])
    
    def test_missing_scraped_data(self):
        """Test handling of missing scraped data."""
        event = {
            'searchWord': 'python programming',
            'scrapedData': []
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['processedData'], [])
    
    def test_relevance_score_calculation(self):
        """Test that relevance scores are calculated correctly."""
        event = {
            'searchWord': 'python',
            'scrapedData': self.sample_scraped_data
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        
        # All items should have relevance scores > 0 since they contain 'python'
        for item in response['processedData']:
            self.assertGreater(item['relevanceScore'], 0)
        
        # Items should be sorted by relevance score (highest first)
        scores = [item['relevanceScore'] for item in response['processedData']]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_content_cleaning(self):
        """Test that content is properly cleaned."""
        scraped_data_with_messy_content = [
            {
                'title': '  Python   Tutorial  ',
                'url': 'https://example.com',
                'content': '  This   is   messy   content   with   extra   spaces  ',
                'timestamp': '2024-01-01T10:00:00Z'
            }
        ]
        
        event = {
            'searchWord': 'python',
            'scrapedData': scraped_data_with_messy_content
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        
        processed_item = response['processedData'][0]
        self.assertEqual(processed_item['title'], 'Python Tutorial')
        self.assertNotIn('  ', processed_item['content'])  # No double spaces
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['processedData'], [])


if __name__ == '__main__':
    unittest.main()