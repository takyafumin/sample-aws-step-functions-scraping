"""
Unit tests for results_handler Lambda function.
"""
import unittest
import json
import sys
import os

# Add the src directory to Python path to import the Lambda function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from results_handler import lambda_handler


class TestResultsHandler(unittest.TestCase):
    """Test cases for results_handler Lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
        self.sample_processed_data = [
            {
                'title': 'Python Programming Tutorial',
                'url': 'https://example.com/python-tutorial',
                'content': 'This is a comprehensive Python programming tutorial...',
                'relevanceScore': 85.5,
                'wordCount': 150,
                'processedAt': '2024-01-01T10:00:00Z'
            },
            {
                'title': 'Advanced Python Concepts',
                'url': 'https://example.com/advanced-python',
                'content': 'Learn advanced Python programming concepts...',
                'relevanceScore': 72.0,
                'wordCount': 120,
                'processedAt': '2024-01-01T10:01:00Z'
            }
        ]
    
    def test_successful_results_handling(self):
        """Test successful results handling with valid processed data."""
        event = {
            'searchWord': 'python programming',
            'processedData': self.sample_processed_data,
            'itemCount': 2,
            'originalItemCount': 3
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('finalResults', response)
        
        final_results = response['finalResults']
        self.assertEqual(final_results['searchWord'], 'python programming')
        self.assertIn('summary', final_results)
        self.assertIn('results', final_results)
        self.assertIn('metadata', final_results)
        
        # Check summary
        summary = final_results['summary']
        self.assertEqual(summary['totalItemsFound'], 3)
        self.assertEqual(summary['totalItemsProcessed'], 2)
        self.assertGreater(summary['averageRelevanceScore'], 0)
        self.assertGreater(summary['topRelevanceScore'], 0)
        
        # Check metadata
        metadata = final_results['metadata']
        self.assertTrue(metadata['processingComplete'])
        self.assertEqual(metadata['resultsCount'], 2)
        self.assertEqual(metadata['totalResults'], 2)
    
    def test_empty_search_word(self):
        """Test handling of empty search word."""
        event = {
            'searchWord': '',
            'processedData': self.sample_processed_data,
            'itemCount': 2,
            'originalItemCount': 3
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIsNone(body['finalResults'])
    
    def test_no_processed_data(self):
        """Test handling when no processed data is provided."""
        event = {
            'searchWord': 'python programming',
            'processedData': [],
            'itemCount': 0,
            'originalItemCount': 0
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        
        final_results = response['finalResults']
        self.assertEqual(final_results['summary']['totalItemsFound'], 0)
        self.assertEqual(final_results['summary']['totalItemsProcessed'], 0)
        self.assertEqual(final_results['summary']['averageRelevanceScore'], 0.0)
        self.assertEqual(final_results['summary']['topRelevanceScore'], 0.0)
        self.assertEqual(len(final_results['results']), 0)
    
    def test_large_dataset_truncation(self):
        """Test that results are truncated to top 10 items."""
        # Create 15 items
        large_processed_data = []
        for i in range(15):
            item = {
                'title': f'Item {i}',
                'url': f'https://example.com/item{i}',
                'content': f'Content for item {i}',
                'relevanceScore': 50 + i,  # Varying scores
                'wordCount': 100,
                'processedAt': '2024-01-01T10:00:00Z'
            }
            large_processed_data.append(item)
        
        event = {
            'searchWord': 'test',
            'processedData': large_processed_data,
            'itemCount': 15,
            'originalItemCount': 15
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        
        final_results = response['finalResults']
        # Should only return top 10 results
        self.assertEqual(len(final_results['results']), 10)
        self.assertEqual(final_results['metadata']['resultsCount'], 10)
        self.assertEqual(final_results['metadata']['totalResults'], 15)
    
    def test_average_relevance_calculation(self):
        """Test that average relevance score is calculated correctly."""
        processed_data = [
            {'relevanceScore': 80.0},
            {'relevanceScore': 60.0},
            {'relevanceScore': 40.0}
        ]
        
        event = {
            'searchWord': 'test',
            'processedData': processed_data,
            'itemCount': 3,
            'originalItemCount': 3
        }
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 200)
        
        final_results = response['finalResults']
        # Average should be (80 + 60 + 40) / 3 = 60.0
        self.assertEqual(final_results['summary']['averageRelevanceScore'], 60.0)
        self.assertEqual(final_results['summary']['topRelevanceScore'], 80.0)
    
    def test_malformed_event(self):
        """Test handling of malformed event that causes exception."""
        event = None
        
        response = lambda_handler(event, self.context)
        
        self.assertEqual(response['statusCode'], 500)
        
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIsNone(body['finalResults'])


if __name__ == '__main__':
    unittest.main()