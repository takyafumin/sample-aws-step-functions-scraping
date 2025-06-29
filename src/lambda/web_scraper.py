"""
Lambda function to perform web scraping based on search word.
"""
import json
import logging
import time

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to perform web scraping based on search word.
    
    Args:
        event: Event data containing search word from previous step
        context: Lambda context object
    
    Returns:
        dict: JSON response containing scraped data
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract search word from the event (from previous step)
        search_word = event.get('searchWord', '')
        
        if not search_word:
            logger.warning("No search word found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Search word not found in input',
                    'searchWord': None,
                    'scrapedData': []
                })
            }
        
        logger.info(f"Starting scraping for search word: {search_word}")
        
        # Simulate web scraping (in real implementation, this would make HTTP requests)
        # Adding a small delay to simulate real scraping
        time.sleep(0.1)
        
        # Mock scraped data
        scraped_data = [
            {
                'title': f'Sample Article 1 about {search_word}',
                'url': f'https://example.com/article1?q={search_word}',
                'content': f'This is sample content related to {search_word}...',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'title': f'Sample Article 2 about {search_word}',
                'url': f'https://example.com/article2?q={search_word}',
                'content': f'Another sample content about {search_word}...',
                'timestamp': '2024-01-01T11:00:00Z'
            }
        ]
        
        logger.info(f"Successfully scraped {len(scraped_data)} items")
        
        # Return scraped data
        response = {
            'statusCode': 200,
            'searchWord': search_word,
            'scrapedData': scraped_data,
            'itemCount': len(scraped_data),
            'body': json.dumps({
                'searchWord': search_word,
                'scrapedData': scraped_data,
                'itemCount': len(scraped_data),
                'message': 'Web scraping completed successfully'
            })
        }
        
        logger.info(f"Returning response with {len(scraped_data)} items")
        return response
        
    except Exception as e:
        logger.error(f"Error during web scraping: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'searchWord': event.get('searchWord') if event else None,
                'scrapedData': []
            })
        }