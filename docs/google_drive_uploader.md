# Google Drive Uploader Lambda

This Lambda function uploads images to Google Drive and returns shareable URLs for the uploaded files.

## Function Overview

The `google_drive_uploader` Lambda function:
- Receives base64-encoded image data from AWS Step Functions
- Uploads the image to Google Drive using the Google Drive API
- Sets the file permissions to be publicly readable
- Returns a shareable URL for the uploaded file
- Handles error cases gracefully with proper logging

## Input Format

The Lambda function expects an event with the following fields:

```json
{
  "imageData": "base64_encoded_image_data",
  "filename": "optional_filename.png",
  "folderId": "optional_google_drive_folder_id"
}
```

### Required Fields
- `imageData`: Base64-encoded image data (required)

### Optional Fields
- `filename`: Name for the uploaded file (default: "screenshot.png")
- `folderId`: Google Drive folder ID where the file should be uploaded (default: root folder)

## Output Format

### Success Response (HTTP 200)
```json
{
  "statusCode": 200,
  "shareable_url": "https://drive.google.com/file/d/FILE_ID/view",
  "file_id": "GOOGLE_DRIVE_FILE_ID",
  "filename": "uploaded_filename.png",
  "body": "{\"shareable_url\": \"https://drive.google.com/file/d/FILE_ID/view\", \"file_id\": \"GOOGLE_DRIVE_FILE_ID\", \"filename\": \"uploaded_filename.png\", \"message\": \"Image uploaded to Google Drive successfully\"}"
}
```

### Error Response (HTTP 400 - Missing Image Data)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Image data not found in input\", \"shareable_url\": null}"
}
```

### Error Response (HTTP 400 - Invalid Base64 Data)
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid base64 image data: error details\", \"shareable_url\": null}"
}
```

### Error Response (HTTP 500 - Upload Failure)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Failed to upload to Google Drive: error details\", \"shareable_url\": null}"
}
```

### Error Response (HTTP 500 - Internal Error)
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"shareable_url\": null}"
}
```

## Setup Requirements

### Google Drive API Setup
1. Create a Google Cloud Project
2. Enable the Google Drive API
3. Create a Service Account
4. Download the service account credentials JSON file
5. Share your Google Drive folder with the service account email (if using a specific folder)

### Environment Variables
- `GOOGLE_SERVICE_ACCOUNT_KEY`: JSON string containing the service account credentials

### Dependencies
The following Python packages are required:
- `google-api-python-client`
- `google-auth`

## Usage Examples

### Basic Image Upload
```python
event = {
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
    "filename": "screenshot.png"
}
response = lambda_handler(event, context)
# Returns: {"statusCode": 200, "shareable_url": "https://drive.google.com/file/d/FILE_ID/view", ...}
```

### Upload to Specific Folder
```python
event = {
    "imageData": "base64_image_data_here",
    "filename": "captured_image.png",
    "folderId": "1a2b3c4d5e6f7g8h9i0j"
}
response = lambda_handler(event, context)
```

### Step Functions Integration
The function can be used as a step in a Step Functions workflow:
```json
{
  "Comment": "Scraping workflow with Google Drive upload",
  "StartAt": "CaptureScreenshot",
  "States": {
    "CaptureScreenshot": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:screenshot-capturer",
      "Next": "UploadToGoogleDrive"
    },
    "UploadToGoogleDrive": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:google-drive-uploader",
      "End": true
    }
  }
}
```

## Testing

Run the unit tests:
```bash
python -m unittest tests.test_google_drive_uploader -v
```

## Security Considerations

- Service account credentials should be stored securely as environment variables
- Uploaded files are made publicly readable by default for sharing purposes
- Consider implementing file size limits and content validation in production
- Monitor Google Drive API usage quotas and rate limits

## Files

- `src/lambda/google_drive_uploader.py` - Main Lambda function
- `tests/test_google_drive_uploader.py` - Unit tests