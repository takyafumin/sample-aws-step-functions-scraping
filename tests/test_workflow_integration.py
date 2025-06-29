"""
Integration tests for the Step Functions workflow.
"""
import unittest
import json
import sys
import os

# Add the src directory to Python path to import the Lambda functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

from search_word_receiver import lambda_handler as search_word_receiver_handler
from web_scraper import lambda_handler as web_scraper_handler
from data_processor import lambda_handler as data_processor_handler
from results_handler import lambda_handler as results_handler_handler


class TestStepFunctionsWorkflow(unittest.TestCase):
    """Integration tests for the complete Step Functions workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {}  # Mock context object
    
    def test_complete_workflow_success(self):
        """Test the complete workflow with valid input."""
        # Step 1: Search word receiver
        initial_input = {'searchWord': 'python programming'}
        step1_response = search_word_receiver_handler(initial_input, self.context)
        
        self.assertEqual(step1_response['statusCode'], 200)
        self.assertEqual(step1_response['searchWord'], 'python programming')
        
        # Step 2: Web scraper (use output from step 1)
        step2_input = {
            'searchWord': step1_response['searchWord']
        }
        step2_response = web_scraper_handler(step2_input, self.context)
        
        self.assertEqual(step2_response['statusCode'], 200)
        self.assertGreater(step2_response['itemCount'], 0)
        self.assertIsInstance(step2_response['scrapedData'], list)
        
        # Step 3: Data processor (use output from step 2)
        step3_input = {
            'searchWord': step2_response['searchWord'],
            'scrapedData': step2_response['scrapedData']
        }
        step3_response = data_processor_handler(step3_input, self.context)
        
        self.assertEqual(step3_response['statusCode'], 200)
        self.assertIsInstance(step3_response['processedData'], list)
        
        # Step 4: Results handler (use output from step 3)
        step4_input = {
            'searchWord': step3_response['searchWord'],
            'processedData': step3_response['processedData'],
            'itemCount': step3_response['itemCount'],
            'originalItemCount': step3_response['originalItemCount']
        }
        step4_response = results_handler_handler(step4_input, self.context)
        
        self.assertEqual(step4_response['statusCode'], 200)
        self.assertIn('finalResults', step4_response)
        
        # Verify final results structure
        final_results = step4_response['finalResults']
        self.assertEqual(final_results['searchWord'], 'python programming')
        self.assertIn('summary', final_results)
        self.assertIn('results', final_results)
        self.assertTrue(final_results['metadata']['processingComplete'])
    
    def test_workflow_with_empty_search_word(self):
        """Test workflow behavior with empty search word."""
        # Step 1: Search word receiver with empty search word
        initial_input = {'searchWord': ''}
        step1_response = search_word_receiver_handler(initial_input, self.context)
        
        # Should fail at step 1
        self.assertEqual(step1_response['statusCode'], 400)
        
        # Workflow should not continue past step 1
        # This simulates the Choice state checking statusCode
    
    def test_workflow_with_japanese_search_word(self):
        """Test workflow with Japanese search word."""
        # Step 1: Search word receiver
        initial_input = {'searchWord': 'プログラミング 学習'}
        step1_response = search_word_receiver_handler(initial_input, self.context)
        
        self.assertEqual(step1_response['statusCode'], 200)
        
        # Continue through the workflow
        step2_response = web_scraper_handler({
            'searchWord': step1_response['searchWord']
        }, self.context)
        
        self.assertEqual(step2_response['statusCode'], 200)
        
        step3_response = data_processor_handler({
            'searchWord': step2_response['searchWord'],
            'scrapedData': step2_response['scrapedData']
        }, self.context)
        
        self.assertEqual(step3_response['statusCode'], 200)
        
        step4_response = results_handler_handler({
            'searchWord': step3_response['searchWord'],
            'processedData': step3_response['processedData'],
            'itemCount': step3_response['itemCount'],
            'originalItemCount': step3_response['originalItemCount']
        }, self.context)
        
        self.assertEqual(step4_response['statusCode'], 200)
        self.assertEqual(step4_response['finalResults']['searchWord'], 'プログラミング 学習')
    
    def test_workflow_data_flow(self):
        """Test that data flows correctly between workflow steps."""
        initial_input = {'searchWord': 'machine learning'}
        
        # Execute workflow steps
        step1_response = search_word_receiver_handler(initial_input, self.context)
        step2_response = web_scraper_handler({'searchWord': step1_response['searchWord']}, self.context)
        step3_response = data_processor_handler({
            'searchWord': step2_response['searchWord'],
            'scrapedData': step2_response['scrapedData']
        }, self.context)
        step4_response = results_handler_handler({
            'searchWord': step3_response['searchWord'],
            'processedData': step3_response['processedData'],
            'itemCount': step3_response['itemCount'],
            'originalItemCount': step3_response['originalItemCount']
        }, self.context)
        
        # Verify search word consistency throughout workflow
        self.assertEqual(step1_response['searchWord'], 'machine learning')
        self.assertEqual(step2_response['searchWord'], 'machine learning')
        self.assertEqual(step3_response['searchWord'], 'machine learning')
        self.assertEqual(step4_response['finalResults']['searchWord'], 'machine learning')
        
        # Verify data transformation
        self.assertGreater(len(step2_response['scrapedData']), 0)
        self.assertGreater(len(step3_response['processedData']), 0)
        self.assertGreater(len(step4_response['finalResults']['results']), 0)
        
        # Verify that processed data has additional fields compared to scraped data
        scraped_item = step2_response['scrapedData'][0]
        processed_item = step3_response['processedData'][0]
        
        # Scraped data should have basic fields
        self.assertIn('title', scraped_item)
        self.assertIn('url', scraped_item)
        self.assertIn('content', scraped_item)
        
        # Processed data should have additional fields
        self.assertIn('relevanceScore', processed_item)
        self.assertIn('wordCount', processed_item)
        self.assertIn('processedAt', processed_item)


if __name__ == '__main__':
    unittest.main()