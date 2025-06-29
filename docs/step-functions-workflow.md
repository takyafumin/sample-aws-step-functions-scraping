# Step Functions Workflow Definition

This document describes the AWS Step Functions workflow for the scraping automation system.

## Workflow Overview

The scraping workflow consists of 4 main Lambda functions orchestrated by AWS Step Functions:

1. **search_word_receiver** - Receives and validates search words
2. **web_scraper** - Performs web scraping based on search words  
3. **data_processor** - Processes and cleans scraped data
4. **results_handler** - Handles final results and prepares output

## Workflow Definition

The Step Functions state machine is defined in `step-functions/scraping-workflow.json`.

### State Diagram

```
Start
  ↓
ReceiveSearchWord (search_word_receiver)
  ↓
CheckSearchWordValid (Choice)
  ↓ (if valid)
PerformWebScraping (web_scraper)
  ↓
CheckScrapingResults (Choice)
  ↓ (if results found)
ProcessScrapedData (data_processor)
  ↓
CheckProcessingResults (Choice)
  ↓ (if successful)
HandleFinalResults (results_handler)
  ↓
WorkflowSuccess (Success)
```

### Error Handling

Each Lambda function state includes:
- **Retry policies** with exponential backoff
- **Catch blocks** for error handling
- **Timeouts** to prevent hanging
- **Choice states** for conditional logic

### Input/Output Coordination

Data flows between states as follows:

#### Input Format
```json
{
  "searchWord": "your search term here"
}
```

#### Between ReceiveSearchWord → PerformWebScraping
```json
{
  "statusCode": 200,
  "searchWord": "your search term here",
  "body": "..."
}
```

#### Between PerformWebScraping → ProcessScrapedData
```json
{
  "statusCode": 200,
  "searchWord": "your search term here",
  "scrapedData": [
    {
      "title": "Article Title",
      "url": "https://example.com",
      "content": "Article content...",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "itemCount": 2
}
```

#### Between ProcessScrapedData → HandleFinalResults
```json
{
  "statusCode": 200,
  "searchWord": "your search term here",
  "processedData": [
    {
      "title": "Article Title",
      "url": "https://example.com", 
      "content": "Cleaned article content...",
      "relevanceScore": 85.5,
      "wordCount": 150,
      "processedAt": "2024-01-01T10:01:00Z"
    }
  ],
  "itemCount": 2,
  "originalItemCount": 3
}
```

#### Final Output
```json
{
  "statusCode": 200,
  "finalResults": {
    "searchWord": "your search term here",
    "processedAt": "2024-01-01T10:02:00Z",
    "summary": {
      "totalItemsFound": 3,
      "totalItemsProcessed": 2,
      "averageRelevanceScore": 78.75,
      "topRelevanceScore": 85.5
    },
    "results": [
      {
        "title": "Article Title",
        "url": "https://example.com",
        "content": "Cleaned article content...",
        "relevanceScore": 85.5,
        "wordCount": 150,
        "processedAt": "2024-01-01T10:01:00Z"
      }
    ],
    "metadata": {
      "processingComplete": true,
      "resultsCount": 1,
      "totalResults": 2
    }
  }
}
```

## Error Scenarios

### No Search Word
If no search word is provided, the workflow fails at the first Choice state.

### No Scraping Results
If no results are found during scraping, the workflow goes to the `HandleNoResults` state and returns an empty result set.

### Lambda Function Failures
Each Lambda function has retry logic. If all retries fail, the workflow goes to the error handling state.

## Deployment

To deploy this workflow:

1. Create the Lambda functions from the source code
2. Update the ARNs in `scraping-workflow.json`
3. Create the Step Functions state machine using the JSON definition
4. Configure appropriate IAM roles and permissions

## Testing

Run the integration tests to verify the complete workflow:

```bash
python -m unittest tests.test_workflow_integration -v
```