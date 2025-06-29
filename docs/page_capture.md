# Page Capture Lambda

This Lambda function captures screenshots of web pages and returns them as image files.

## Function Overview

The `page_capture` Lambda function:
- Receives input containing a URL to capture
- Takes a screenshot of the specified web page
- Saves the image to temporary storage (/tmp)
- Returns the image data in base64 format along with the file path
- Handles error cases gracefully

## Input Format

The Lambda function expects an event with a `url` field:

```json
{
  "url": "https://example.com"
}
```

## Output Format

### Success Response (HTTP 200)
```json
{
  "statusCode": 200,
  "url": "https://example.com",
  "imagePath": "/tmp/screenshot_request-id.png",
  "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
  "body": "{\"url\": \"https://example.com\", \"imagePath\": \"/tmp/screenshot_request-id.png\", \"message\": \"Page screenshot captured successfully\"}"
}
```

### Error Response (HTTP 400 - Missing URL)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"URL not found in input\", \"imageData\": null, \"imagePath\": null}"
}
```

### Error Response (HTTP 400 - Invalid URL Format)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid URL format: invalid-url\", \"imageData\": null, \"imagePath\": null}"
}
```

### Error Response (HTTP 500 - Internal Error)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"imageData\": null, \"imagePath\": null}"
}
```

## Usage Examples

### Basic Usage
```python
event = {"url": "https://example.com"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "url": "https://example.com", "imagePath": "/tmp/screenshot_xxx.png", ...}
```

### Japanese URLs
```python
event = {"url": "https://example.co.jp/パス"}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "url": "https://example.co.jp/パス", ...}
```

### Step Functions Integration
The function can be used in a Step Functions workflow for web scraping:
```json
{
  "Comment": "Scraping workflow with page capture",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "CaptureSearchResults"
    },
    "CaptureSearchResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:page-capture",
      "Next": "ProcessImages"
    }
  }
}
```

## Implementation Details

### Current Implementation
The current implementation creates placeholder images for testing purposes. In a production Lambda environment, this should be replaced with actual browser automation using:

- **Puppeteer** with Chrome/Chromium (recommended for Lambda)
- **Playwright** with browser binaries
- Pre-built Lambda layers containing browser binaries

### Production Setup Requirements
For production deployment, you would need:

1. **Browser Binary**: Chrome/Chromium binary compatible with Lambda runtime
2. **Puppeteer/Playwright**: Node.js package or Python equivalent (pyppeteer)
3. **Lambda Layer**: Pre-built layer with browser dependencies
4. **Memory**: Increased Lambda memory allocation (512MB+ recommended)
5. **Timeout**: Extended timeout for page loading and capture

### Example Production Implementation
```python
# Using pyppeteer (Python port of Puppeteer)
import asyncio
from pyppeteer import launch

async def capture_real_screenshot(url):
    browser = await launch({
        'headless': True,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--no-zygote',
            '--single-process'
        ]
    })
    
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 720})
    await page.goto(url, {'waitUntil': 'networkidle2'})
    
    screenshot_path = f'/tmp/screenshot_{context.aws_request_id}.png'
    await page.screenshot({'path': screenshot_path, 'fullPage': True})
    
    await browser.close()
    return screenshot_path
```

## Testing

Run the unit tests:
```bash
python -m unittest tests.test_page_capture -v
```

Run all tests:
```bash
python -m unittest discover tests -v
```

## Error Handling

The function handles various error scenarios:
- Missing URL in input
- Invalid URL format
- Internal processing errors
- File system errors

All errors are logged and return appropriate HTTP status codes with error messages.

## Files

- `src/lambda/page_capture.py` - Main Lambda function
- `tests/test_page_capture.py` - Unit tests
- `docs/page_capture.md` - This documentation file