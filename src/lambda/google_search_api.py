"""
Lambda function to perform Google Custom Search API requests and return top 5 URLs.
"""
import json
import logging
import os
import urllib.parse
import urllib.request
import urllib.error

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to perform Google Custom Search API requests.
    
    Args:
        event: Event data containing search word
        context: Lambda context object
    
    Returns:
        dict: JSON response containing top 5 search result URLs
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
                    'searchWord': None,
                    'urls': []
                })
            }
        
        logger.info(f"Performing Google search for: {search_word}")
        
        # Get Google Custom Search API configuration
        api_key = os.environ.get('GOOGLE_API_KEY')
        search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            logger.error("Missing Google API configuration")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Google API configuration not found',
                    'searchWord': search_word,
                    'urls': []
                })
            }
        
        # Perform Google Custom Search API request
        search_results = perform_google_search(search_word, api_key, search_engine_id)
        
        if search_results is None:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to perform Google search',
                    'searchWord': search_word,
                    'urls': []
                })
            }
        
        # Extract top 5 URLs from search results
        urls = extract_urls_from_results(search_results)
        
        logger.info(f"Found {len(urls)} URLs for search word: {search_word}")
        
        # Return the search results in JSON format
        response = {
            'statusCode': 200,
            'searchWord': search_word,
            'urls': urls,
            'body': json.dumps({
                'searchWord': search_word,
                'urls': urls,
                'message': f'Found {len(urls)} search results'
            })
        }
        
        logger.info(f"Returning response with {len(urls)} URLs")
        return response
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'searchWord': event.get('searchWord') if event else None,
                'urls': []
            })
        }


def perform_google_search(search_word, api_key, search_engine_id):
    """
    Perform a Google Custom Search API request.
    
    Args:
        search_word (str): The search term
        api_key (str): Google API key
        search_engine_id (str): Google Custom Search Engine ID
    
    Returns:
        dict: Search results from Google API, or None if error
    """
    try:
        # Construct the API URL
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': search_word,
            'num': 5  # Request top 5 results
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
        
        logger.info(f"Making request to Google Custom Search API")
        
        # Make the HTTP request
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                logger.info("Successfully received Google search results")
                return result
            else:
                logger.error(f"Google API returned status code: {response.status}")
                return None
                
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error during Google search: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        logger.error(f"URL error during Google search: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Google search: {str(e)}")
        return None


def extract_urls_from_results(search_results):
    """
    Extract URLs from Google Custom Search API results.
    
    Args:
        search_results (dict): Results from Google Custom Search API
    
    Returns:
        list: List of URLs (up to 5)
    """
    urls = []
    
    try:
        items = search_results.get('items', [])
        
        for item in items[:5]:  # Limit to top 5 results
            url = item.get('link')
            if url:
                urls.append(url)
                
        logger.info(f"Extracted {len(urls)} URLs from search results")
        
    except Exception as e:
        logger.error(f"Error extracting URLs from search results: {str(e)}")
    
    return urls