"""
Lambda function to record URLs to Google Sheets.
"""
import json
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    logger.warning("Google APIs not available. Install google-api-python-client for full functionality.")
    GOOGLE_APIS_AVAILABLE = False


def get_sheets_service():
    """
    Create and return Google Sheets service object.
    
    Returns:
        Google Sheets service object or None if not available
    """
    if not GOOGLE_APIS_AVAILABLE:
        return None
    
    try:
        # In a real deployment, credentials would be stored in AWS Secrets Manager
        # or as environment variables. For now, we'll use a placeholder approach.
        credentials_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_json:
            logger.error("Google Sheets credentials not found in environment variables")
            return None
        
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Failed to create Google Sheets service: {str(e)}")
        return None


def write_url_to_sheet(service, spreadsheet_id: str, sheet_range: str, url: str, additional_data: Optional[Dict] = None) -> bool:
    """
    Write URL and additional data to Google Sheets.
    
    Args:
        service: Google Sheets service object
        spreadsheet_id: The ID of the target spreadsheet
        sheet_range: The range in A1 notation (e.g., 'Sheet1!A:C')
        url: The URL to record
        additional_data: Optional dictionary with additional data to record
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not service:
        logger.error("Google Sheets service not available")
        return False
    
    try:
        # Prepare the data row
        import datetime
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        
        row_data = [timestamp, url]
        
        # Add additional data if provided
        if additional_data:
            for key in ['filename', 'file_id', 'file_size', 'description']:
                row_data.append(additional_data.get(key, ''))
        
        # Append the data to the sheet
        body = {
            'values': [row_data]
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"Successfully wrote URL to sheet. Updated range: {result.get('updates', {}).get('updatedRange')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write URL to sheet: {str(e)}")
        return False


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler to record URLs to Google Sheets.
    
    Args:
        event: Event data containing URL and sheet information
        context: Lambda context object
    
    Returns:
        dict: JSON response indicating success or failure
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract required parameters from the event
        url = event.get('url', '')
        spreadsheet_id = event.get('spreadsheet_id', '')
        sheet_range = event.get('sheet_range', 'Sheet1!A:F')  # Default range
        
        if not url:
            logger.warning("No URL found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'URL not found in input',
                    'success': False
                })
            }
        
        if not spreadsheet_id:
            logger.warning("No spreadsheet ID found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Spreadsheet ID not found in input',
                    'success': False
                })
            }
        
        logger.info(f"Recording URL: {url} to spreadsheet: {spreadsheet_id}")
        
        # Get Google Sheets service
        service = get_sheets_service()
        if not service:
            return {
                'statusCode': 503,
                'body': json.dumps({
                    'error': 'Google Sheets service unavailable',
                    'success': False
                })
            }
        
        # Extract additional data if provided
        additional_data = event.get('additional_data', {})
        
        # Write URL to sheet
        success = write_url_to_sheet(service, spreadsheet_id, sheet_range, url, additional_data)
        
        if success:
            response = {
                'statusCode': 200,
                'url': url,
                'spreadsheet_id': spreadsheet_id,
                'success': True,
                'body': json.dumps({
                    'message': 'URL recorded successfully',
                    'url': url,
                    'spreadsheet_id': spreadsheet_id,
                    'success': True
                })
            }
            logger.info(f"Successfully recorded URL to spreadsheet")
            return response
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to record URL to spreadsheet',
                    'success': False
                })
            }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'success': False
            })
        }