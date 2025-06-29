"""
Lambda function to upload images to Google Drive and generate shareable URLs.
"""
import json
import logging
import base64
import io
import os
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Google Drive API imports - these would be included in the Lambda layer
try:
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    # Create mock objects for testing when libraries are not available
    build = None
    Credentials = None
    MediaIoBaseUpload = None
    GOOGLE_DRIVE_AVAILABLE = False
    logger.warning("Google Drive API libraries not available")


def get_drive_service():
    """
    Create and return Google Drive service instance.
    
    Returns:
        googleapiclient.discovery.Resource: Google Drive service
    """
    if not GOOGLE_DRIVE_AVAILABLE:
        raise ImportError("Google Drive API libraries not available")
    
    # Service account credentials should be stored as environment variable
    service_account_info = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    if not service_account_info:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY environment variable not set")
    
    try:
        credentials_dict = json.loads(service_account_info)
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Failed to create Google Drive service: {str(e)}")
        raise


def upload_image_to_drive(
    image_data: bytes,
    filename: str,
    folder_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Upload image to Google Drive and return file info with shareable URL.
    
    Args:
        image_data: Binary image data
        filename: Name for the uploaded file
        folder_id: Optional Google Drive folder ID
    
    Returns:
        dict: File information including shareable URL
    """
    if not GOOGLE_DRIVE_AVAILABLE:
        raise ImportError("Google Drive API libraries not available")
        
    try:
        service = get_drive_service()
        
        # Prepare file metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else None
        }
        
        # Remove None values from metadata
        file_metadata = {k: v for k, v in file_metadata.items() if v is not None}
        
        # Create media upload
        media = MediaIoBaseUpload(
            io.BytesIO(image_data),
            mimetype='image/png',  # Default to PNG, could be detected
            resumable=True
        )
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        logger.info(f"File uploaded successfully with ID: {file_id}")
        
        # Make file publicly accessible
        service.permissions().create(
            fileId=file_id,
            body={
                'role': 'reader',
                'type': 'anyone'
            }
        ).execute()
        
        # Generate shareable URL
        shareable_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        return {
            'file_id': file_id,
            'shareable_url': shareable_url,
            'filename': filename
        }
        
    except Exception as e:
        logger.error(f"Failed to upload image to Google Drive: {str(e)}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler to upload images to Google Drive and return shareable URLs.
    
    Args:
        event: Event data containing image data and metadata
        context: Lambda context object
    
    Returns:
        dict: JSON response containing the shareable URL and file info
    """
    try:
        logger.info(f"Received event keys: {list(event.keys())}")
        
        # Extract image data from the event
        image_data_b64 = event.get('imageData', '')
        filename = event.get('filename', 'screenshot.png')
        folder_id = event.get('folderId')  # Optional folder ID
        
        if not image_data_b64:
            logger.warning("No image data found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Image data not found in input',
                    'shareable_url': None
                })
            }
        
        # Decode base64 image data
        try:
            image_data = base64.b64decode(image_data_b64)
            logger.info(f"Decoded image data, size: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode base64 image data: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Invalid base64 image data: {str(e)}',
                    'shareable_url': None
                })
            }
        
        # Upload to Google Drive
        try:
            file_info = upload_image_to_drive(image_data, filename, folder_id)
            logger.info(f"Image uploaded successfully: {file_info}")
            
            # Return success response
            response = {
                'statusCode': 200,
                'shareable_url': file_info['shareable_url'],
                'file_id': file_info['file_id'],
                'filename': file_info['filename'],
                'body': json.dumps({
                    'shareable_url': file_info['shareable_url'],
                    'file_id': file_info['file_id'],
                    'filename': file_info['filename'],
                    'message': 'Image uploaded to Google Drive successfully'
                })
            }
            
            logger.info(f"Returning response with shareable URL: {file_info['shareable_url']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to upload to Google Drive: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': f'Failed to upload to Google Drive: {str(e)}',
                    'shareable_url': None
                })
            }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'shareable_url': None
            })
        }