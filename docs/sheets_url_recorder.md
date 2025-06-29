# Sheets URL Recorder Lambda

This Lambda function records URLs from Google Drive files to Google Sheets.

## Function Overview

The `sheets_url_recorder` Lambda function:
- Receives input containing URL and spreadsheet information
- Authenticates with Google Sheets API using service account credentials
- Records URLs with timestamps and additional metadata to specified Google Sheets
- Handles error cases gracefully with appropriate HTTP status codes

## Input Format

The Lambda function expects an event with the following fields:

```json
{
  "url": "https://drive.google.com/file/d/1234567890/view",
  "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
  "sheet_range": "Sheet1!A:F",
  "additional_data": {
    "filename": "document.pdf",
    "file_id": "1234567890",
    "file_size": "1024000",
    "description": "Sample document"
  }
}
```

### Required Fields
- `url`: The URL to be recorded (required)
- `spreadsheet_id`: The Google Sheets spreadsheet ID (required)

### Optional Fields
- `sheet_range`: The range in A1 notation where data should be appended (default: "Sheet1!A:F")
- `additional_data`: Object containing additional metadata to record

## Output Format

### Success Response (HTTP 200)
```json
{
  "statusCode": 200,
  "url": "https://drive.google.com/file/d/1234567890/view",
  "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
  "success": true,
  "body": "{\"message\": \"URL recorded successfully\", \"url\": \"...\", \"success\": true}"
}
```

### Error Response (HTTP 400 - Missing Required Field)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"URL not found in input\", \"success\": false}"
}
```

### Error Response (HTTP 503 - Service Unavailable)
```json
{
  "statusCode": 503,
  "body": "{\"error\": \"Google Sheets service unavailable\", \"success\": false}"
}
```

### Error Response (HTTP 500 - Internal Error)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"success\": false}"
}
```

## Data Written to Sheets

The function writes the following columns to the spreadsheet:
1. **Timestamp** (ISO 8601 format with 'Z' suffix)
2. **URL** (the provided URL)
3. **Filename** (from additional_data, if provided)
4. **File ID** (from additional_data, if provided)
5. **File Size** (from additional_data, if provided)
6. **Description** (from additional_data, if provided)

## Configuration

### Environment Variables
- `GOOGLE_SHEETS_CREDENTIALS`: JSON string containing Google service account credentials

### Required Google Sheets API Permissions
The service account must have the following scope:
- `https://www.googleapis.com/auth/spreadsheets`

## Usage Examples

### Basic Usage
```python
event = {
    "url": "https://drive.google.com/file/d/1234567890/view",
    "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890"
}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "success": true, ...}
```

### With Additional Data
```python
event = {
    "url": "https://drive.google.com/file/d/1234567890/view",
    "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
    "additional_data": {
        "filename": "report.pdf",
        "file_id": "1234567890",
        "file_size": "2048000",
        "description": "Monthly report"
    }
}
response = lambda_handler(event, context)
```

### Step Functions Integration
The function can be integrated into a Step Functions workflow:
```json
{
  "Comment": "URL recording workflow",
  "StartAt": "RecordUrlToSheets",
  "States": {
    "RecordUrlToSheets": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:sheets-url-recorder",
      "End": true
    }
  }
}
```

## Dependencies

The function requires the following Python packages:
- `google-api-python-client`
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`

## Testing

Run the unit tests:
```bash
python -m unittest tests.test_sheets_url_recorder -v
```

Run all tests:
```bash
python -m unittest discover tests -v
```

## Files

- `src/lambda/sheets_url_recorder.py` - Main Lambda function
- `tests/test_sheets_url_recorder.py` - Unit tests
- `requirements.txt` - Python dependencies

## Security Considerations

- Store Google service account credentials securely in AWS Secrets Manager or environment variables
- Use least privilege principle for Google Sheets API permissions
- Validate and sanitize input data before writing to sheets
- Monitor API usage to prevent quota exhaustion