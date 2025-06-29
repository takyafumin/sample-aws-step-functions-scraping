# Google Search API Lambda

This Lambda function performs Google Custom Search API requests to retrieve the top 5 search result URLs for a given search word.

## Function Overview

The `google_search_api` Lambda function:
- Receives input from AWS Step Functions containing a search word
- Calls Google Custom Search API to retrieve search results
- Extracts the top 5 URLs from the search results
- Returns the URLs in a standardized JSON format
- Handles error cases gracefully including API failures and missing configuration

## Configuration Requirements

The Lambda function requires the following environment variables:
- `GOOGLE_API_KEY`: Your Google API key with Custom Search API access
- `GOOGLE_SEARCH_ENGINE_ID`: Your Google Custom Search Engine ID

### Setting up Google Custom Search API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create an API key with Custom Search API permissions
4. Set up a Custom Search Engine at [Google CSE](https://cse.google.com/)
5. Configure the Lambda environment variables with your API key and search engine ID

## Input Format

The Lambda function expects an event with a `searchWord` field:

```json
{
  "searchWord": "your search term here"
}
```

## Output Format

### Success Response (HTTP 200)
```json
{
  "statusCode": 200,
  "searchWord": "your search term here",
  "urls": [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com",
    "https://example4.com",
    "https://example5.com"
  ],
  "body": "{\"searchWord\": \"your search term here\", \"urls\": [...], \"message\": \"Found 5 search results\"}"
}
```

### Error Response (HTTP 400 - Missing Search Word)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Search word not found in input\", \"searchWord\": null, \"urls\": []}"
}
```

### Error Response (HTTP 500 - Missing Configuration)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Google API configuration not found\", \"searchWord\": \"search term\", \"urls\": []}"
}
```

### Error Response (HTTP 500 - API Failure)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Failed to perform Google search\", \"searchWord\": \"search term\", \"urls\": []}"
}
```

## Usage Examples

### Basic Usage
```python
event = {"searchWord": "python programming"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "searchWord": "python programming", "urls": [...]}
```

### Japanese Search Words
```python
event = {"searchWord": "プログラミング 学習"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "searchWord": "プログラミング 学習", "urls": [...]}
```

### Step Functions Integration
The function can be used as part of a Step Functions workflow after the search word receiver:
```json
{
  "Comment": "Scraping workflow with Google search",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "GoogleSearch"
    },
    "GoogleSearch": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:google-search-api",
      "End": true
    }
  }
}
```

## Features

- **Top 5 Results**: Returns up to 5 search result URLs
- **Error Handling**: Comprehensive error handling for API failures, network issues, and configuration problems
- **Unicode Support**: Supports search terms in multiple languages including Japanese
- **Timeout Protection**: Includes 30-second timeout for API requests
- **Logging**: Detailed logging for debugging and monitoring
- **Step Functions Ready**: Designed to integrate seamlessly with AWS Step Functions

## Testing

Run the unit tests:
```bash
python -m unittest tests.test_google_search_api -v
```

Run all tests:
```bash
python -m unittest discover tests -v
```

## Files

- `src/lambda/google_search_api.py` - Main Lambda function
- `tests/test_google_search_api.py` - Unit tests
- `docs/google_search_api.md` - This documentation

## API Rate Limits

Please be aware of Google Custom Search API rate limits:
- Free quota: 100 search queries per day
- Paid quota: Up to 10,000 queries per day (requires billing setup)

Configure appropriate retry logic and error handling based on your usage requirements.

## Security Considerations

- Store API keys securely using AWS Systems Manager Parameter Store or AWS Secrets Manager
- Use IAM roles with minimal required permissions
- Monitor API usage to prevent unexpected charges
- Validate and sanitize search input if accepting user-generated content