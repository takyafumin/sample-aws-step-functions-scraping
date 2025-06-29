# Search Word Receiver Lambda

This Lambda function receives search words from AWS Step Functions input and returns them in JSON format.

## Function Overview

The `search_word_receiver` Lambda function:
- Receives input from AWS Step Functions
- Extracts the `searchWord` field from the event
- Returns the search word in a standardized JSON format
- Handles error cases gracefully

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
  "body": "{\"searchWord\": \"your search term here\", \"message\": \"Search word received successfully\"}"
}
```

### Error Response (HTTP 400 - Missing Search Word)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Search word not found in input\", \"searchWord\": null}"
}
```

### Error Response (HTTP 500 - Internal Error)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"searchWord\": null}"
}
```

## Usage Examples

### Basic Usage
```python
event = {"searchWord": "python programming"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "searchWord": "python programming", ...}
```

### Japanese Search Words
```python
event = {"searchWord": "プログラミング 学習"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "searchWord": "プログラミング 学習", ...}
```

### Step Functions Integration
The function can be used as the first step in a Step Functions workflow:
```json
{
  "Comment": "Scraping workflow",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "NextStep"
    }
  }
}
```

## Testing

Run the unit tests:
```bash
python -m unittest tests.test_search_word_receiver -v
```

Run manual tests:
```bash
python manual_test.py
```

## Files

- `src/lambda/search_word_receiver.py` - Main Lambda function
- `tests/test_search_word_receiver.py` - Unit tests
- `manual_test.py` - Manual testing script