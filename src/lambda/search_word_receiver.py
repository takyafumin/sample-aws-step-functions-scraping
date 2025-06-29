"""
Lambda function to receive search words from Step Functions input.
"""
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to receive search words from Step Functions input.
    
    Args:
        event: Event data from Step Functions containing search words
        context: Lambda context object
    
    Returns:
        dict: JSON response containing the search words
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract search word from the event
        search_word = event.get('searchWord', '')
        
        if not search_word:
            logger.warning("No search word found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Search word not found in input',
                    'searchWord': None
                })
            }
        
        logger.info(f"Extracted search word: {search_word}")
        
        # Return the search word in JSON format
        response = {
            'statusCode': 200,
            'searchWord': search_word,
            'body': json.dumps({
                'searchWord': search_word,
                'message': 'Search word received successfully'
            })
        }
        
        logger.info(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'searchWord': None
            })
        }