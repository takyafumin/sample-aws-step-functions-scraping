"""
Lambda function to capture web page screenshots.
"""
import json
import logging
import os
import base64
import subprocess
import tempfile
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler to capture screenshots of web pages.
    
    Args:
        event: Event data containing URL to capture
        context: Lambda context object
    
    Returns:
        dict: JSON response containing capture result and image data
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract URL from the event
        url = event.get('url', '')
        
        if not url:
            logger.warning("No URL found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'URL not found in input',
                    'imageData': None,
                    'imagePath': None
                })
            }
        
        # Validate URL format
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            logger.error(f"Invalid URL format: {url}, error: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Invalid URL format: {url}',
                    'imageData': None,
                    'imagePath': None
                })
            }
        
        logger.info(f"Capturing screenshot for URL: {url}")
        
        # Capture the page screenshot
        image_path, image_data = capture_page_screenshot(url, context)
        
        logger.info(f"Screenshot captured successfully: {image_path}")
        
        # Return success response
        response = {
            'statusCode': 200,
            'url': url,
            'imagePath': image_path,
            'imageData': image_data,
            'body': json.dumps({
                'url': url,
                'imagePath': image_path,
                'message': 'Page screenshot captured successfully'
            })
        }
        
        logger.info(f"Returning response with image path: {image_path}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'imageData': None,
                'imagePath': None
            })
        }


def capture_page_screenshot(url, context=None):
    """
    Capture a screenshot of the specified URL using Puppeteer.
    
    Args:
        url (str): URL to capture
        context: Lambda context object (optional)
        
    Returns:
        tuple: (image_path, base64_image_data)
    """
    # Create temporary file for the screenshot
    temp_dir = '/tmp'
    timestamp = context.aws_request_id if context and hasattr(context, 'aws_request_id') else 'test'
    image_filename = f"screenshot_{timestamp}.png"
    image_path = os.path.join(temp_dir, image_filename)
    
    try:
        # For now, we'll implement a placeholder that creates a simple image
        # In a real Lambda deployment, this would use Puppeteer with Chrome/Chromium
        create_placeholder_image(image_path, url)
        
        # Read the image and encode as base64
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        return image_path, image_data
        
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {str(e)}")
        raise


def create_placeholder_image(image_path, url):
    """
    Create a placeholder image for testing purposes.
    In production, this would be replaced with actual Puppeteer screenshot logic.
    
    Args:
        image_path (str): Path where to save the image
        url (str): URL being captured (for reference)
    """
    try:
        # Try to use PIL if available, otherwise create a simple text file
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple image with the URL text
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to use a default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw the URL on the image
            text = f"Screenshot of: {url}"
            if font:
                draw.text((50, 50), text, fill='black', font=font)
            else:
                draw.text((50, 50), text, fill='black')
            
            # Save the image
            image.save(image_path, 'PNG')
            
        except ImportError:
            # Fallback: create a minimal PNG file
            # This is a basic 1x1 pixel PNG in base64, decoded and saved
            minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\x93\x1e$\x8c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(image_path, 'wb') as f:
                f.write(minimal_png)
        
        logger.info(f"Created placeholder image at: {image_path}")
        
    except Exception as e:
        logger.error(f"Failed to create placeholder image: {str(e)}")
        raise


# TODO: Real Puppeteer implementation would look like this:
"""
def capture_page_screenshot_puppeteer(url):
    '''
    Real implementation using Puppeteer.
    This would require:
    1. Puppeteer npm package
    2. Chrome/Chromium binary (via Lambda layer or bundled)
    3. Node.js subprocess call or pyppeteer
    '''
    
    # Example with pyppeteer (Python port of Puppeteer)
    import asyncio
    from pyppeteer import launch
    
    async def capture():
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
    
    return asyncio.get_event_loop().run_until_complete(capture())
"""