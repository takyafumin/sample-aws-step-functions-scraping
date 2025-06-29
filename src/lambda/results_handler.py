"""
Lambda function to handle final results and save/format output.
"""
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to handle final results and format output.
    
    Args:
        event: Event data containing processed data from previous step
        context: Lambda context object
    
    Returns:
        dict: JSON response containing final results
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract data from the event (from previous step)
        search_word = event.get('searchWord', '')
        processed_data = event.get('processedData', [])
        item_count = event.get('itemCount', 0)
        original_item_count = event.get('originalItemCount', 0)
        
        if not search_word:
            logger.warning("No search word found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Search word not found in input',
                    'finalResults': None
                })
            }
        
        logger.info(f"Handling results for search word: {search_word}, {item_count} processed items")
        
        # Create final results summary
        final_results = {
            'searchWord': search_word,
            'processedAt': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'totalItemsFound': original_item_count,
                'totalItemsProcessed': item_count,
                'averageRelevanceScore': _calculate_average_relevance(processed_data),
                'topRelevanceScore': _get_top_relevance_score(processed_data)
            },
            'results': processed_data[:10],  # Return top 10 results
            'metadata': {
                'processingComplete': True,
                'resultsCount': min(len(processed_data), 10),
                'totalResults': len(processed_data)
            }
        }
        
        # In a real implementation, this is where you might:
        # - Save results to a database
        # - Send results to an S3 bucket
        # - Send notifications via SNS
        # - Update a dashboard
        
        logger.info(f"Successfully handled results: {item_count} items processed")
        
        # Return final results
        response = {
            'statusCode': 200,
            'finalResults': final_results,
            'body': json.dumps({
                'finalResults': final_results,
                'message': 'Results handling completed successfully'
            })
        }
        
        logger.info(f"Returning final results with {min(len(processed_data), 10)} top results")
        return response
        
    except Exception as e:
        logger.error(f"Error during results handling: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'finalResults': None
            })
        }


def _calculate_average_relevance(processed_data):
    """
    Calculate average relevance score from processed data.
    
    Args:
        processed_data: List of processed items
    
    Returns:
        float: Average relevance score
    """
    if not processed_data:
        return 0.0
    
    total_score = sum(item.get('relevanceScore', 0) for item in processed_data)
    return round(total_score / len(processed_data), 2)


def _get_top_relevance_score(processed_data):
    """
    Get the highest relevance score from processed data.
    
    Args:
        processed_data: List of processed items
    
    Returns:
        float: Highest relevance score
    """
    if not processed_data:
        return 0.0
    
    return max(item.get('relevanceScore', 0) for item in processed_data)