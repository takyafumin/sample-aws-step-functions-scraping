"""
Lambda function to process scraped data.
"""
import json
import logging
import re
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to process scraped data.
    
    Args:
        event: Event data containing scraped data from previous step
        context: Lambda context object
    
    Returns:
        dict: JSON response containing processed data
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract data from the event (from previous step)
        search_word = event.get('searchWord', '')
        scraped_data = event.get('scrapedData', [])
        
        if not search_word:
            logger.warning("No search word found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Search word not found in input',
                    'searchWord': None,
                    'processedData': []
                })
            }
        
        if not scraped_data:
            logger.warning("No scraped data found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No scraped data found in input',
                    'searchWord': search_word,
                    'processedData': []
                })
            }
        
        logger.info(f"Processing {len(scraped_data)} scraped items for search word: {search_word}")
        
        processed_data = []
        
        for item in scraped_data:
            try:
                # Process each scraped item
                processed_item = {
                    'title': _clean_content(item.get('title', '')),
                    'url': item.get('url', ''),
                    'content': _clean_content(item.get('content', '')),
                    'timestamp': item.get('timestamp', ''),
                    'relevanceScore': _calculate_relevance_score(item, search_word),
                    'wordCount': len(item.get('content', '').split()),
                    'processedAt': datetime.utcnow().isoformat() + 'Z'
                }
                
                # Only include items with minimum relevance score
                if processed_item['relevanceScore'] > 0:
                    processed_data.append(processed_item)
                
            except Exception as item_error:
                logger.warning(f"Error processing item: {str(item_error)}")
                continue
        
        # Sort by relevance score (highest first)
        processed_data.sort(key=lambda x: x['relevanceScore'], reverse=True)
        
        logger.info(f"Successfully processed {len(processed_data)} items")
        
        # Return processed data
        response = {
            'statusCode': 200,
            'searchWord': search_word,
            'processedData': processed_data,
            'itemCount': len(processed_data),
            'originalItemCount': len(scraped_data),
            'body': json.dumps({
                'searchWord': search_word,
                'processedData': processed_data,
                'itemCount': len(processed_data),
                'originalItemCount': len(scraped_data),
                'message': 'Data processing completed successfully'
            })
        }
        
        logger.info(f"Returning response with {len(processed_data)} processed items")
        return response
        
    except Exception as e:
        logger.error(f"Error during data processing: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'searchWord': event.get('searchWord') if event else None,
                'processedData': []
            })
        }


def _clean_content(content):
    """
    Clean and normalize content text.
    
    Args:
        content: Raw content string
    
    Returns:
        str: Cleaned content
    """
    if not content:
        return ""
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Remove common HTML entities (in case they exist)
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    
    return content


def _calculate_relevance_score(item, search_word):
    """
    Calculate relevance score for an item based on search word.
    
    Args:
        item: Scraped item dictionary
        search_word: Search word to match against
    
    Returns:
        float: Relevance score (0-100)
    """
    score = 0
    search_words = search_word.lower().split()
    
    title = item.get('title', '').lower()
    content = item.get('content', '').lower()
    
    # Score based on title matches (higher weight)
    for word in search_words:
        if word in title:
            score += 30
    
    # Score based on content matches
    for word in search_words:
        content_matches = content.count(word)
        score += min(content_matches * 5, 20)  # Cap at 20 points per word
    
    # Bonus for exact phrase match
    if search_word.lower() in title:
        score += 20
    if search_word.lower() in content:
        score += 10
    
    return min(score, 100)  # Cap at 100