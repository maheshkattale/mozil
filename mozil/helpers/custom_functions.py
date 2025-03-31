
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO
from django.core.files.storage import FileSystemStorage
import time
from .validations import hosturl
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from mozil.settings import *
import locale
from urllib.parse import urlparse, parse_qs
from datetime import datetime,date,timedelta
from PIL import Image, ImageDraw, ImageFont
from mimetypes import guess_type
from django.conf import settings
import logging
from django.utils.text import slugify

# def save_file(folder_path, uploaded_file, request):
#     os.makedirs(folder_path, exist_ok=True)
#     sanitized_filename = os.path.basename(uploaded_file.name)  # Sanitize filename
#     file_path = os.path.join(folder_path, sanitized_filename)

#     # Save the uploaded file temporarily
#     temp_file_path = os.path.join(folder_path, f"temp_{sanitized_filename}")
#     try:
#         with default_storage.open(temp_file_path, 'wb+') as temp_destination:
#             for chunk in uploaded_file.chunks():
#                 temp_destination.write(chunk)

#         # Open the image with Pillow
#         with Image.open(temp_file_path) as img:
#             draw = ImageDraw.Draw(img)
            
#             # Define the font and size
#             try:
#                 font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf')
#                 font = ImageFont.truetype(font_path, 36)
#             except IOError:
#                 font = ImageFont.load_default()

#             # Get the current month and year
#             current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#             text = f"{current_date}"

#             # Measure text size
#             text_bbox = draw.textbbox((0, 0), text, font=font)
#             text_width = text_bbox[2] - text_bbox[0]
#             text_height = text_bbox[3] - text_bbox[1]

#             # Define text position and rectangle background
#             padding = 10
#             text_position = (padding, padding)
#             rectangle_position = (
#                 text_position[0] - padding,
#                 text_position[1] - padding,
#                 text_position[0] + text_width + padding,
#                 text_position[1] + text_height + padding
#             )

#             # Draw rectangle and text
#             draw.rectangle(rectangle_position, fill="#6e6e6e")
#             draw.text(text_position, text, fill="white", font=font)

#             # Save the final image
#             img.save(file_path)

#     except Exception as e:
#         # Log error and cleanup
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)
#         print(ValueError(f"Failed to process the image: {e}"))
#         return ''

#     finally:
#         # Remove the temporary file
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)

#     # Get the relative file path for the URL
#     relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
#     file_url = request.build_absolute_uri(settings.MEDIA_URL + relative_file_path.replace("\\", "/"))
#     return file_url

def format_indian_rupees(number):
    number=int(number)
    locale.setlocale(locale.LC_ALL, 'en_IN')
    return locale.format_string("%d", number, grouping=True)

def extract_lat_lng_from_url(google_maps_url):
    # Parse the URL
    parsed_url = urlparse(google_maps_url)
    # Extract the path and split by '/'
    path_segments = parsed_url.path.split('/')
    for segment in path_segments:
        if '@' in segment:  # Look for the segment with '@' containing coordinates
            coordinates = segment.split('@')[1].split(',')[:2]  # Get lat and lng
            latitude = coordinates[0]
            longitude = coordinates[1]
            return float(latitude), float(longitude)
    return None, None

# def save_file(folder_path, uploaded_file, request):
#     # Ensure the folder exists
#     os.makedirs(folder_path, exist_ok=True)
    
#     # Sanitize the filename
#     sanitized_filename = os.path.basename(uploaded_file.name)
#     file_path = os.path.join(folder_path, sanitized_filename)

#     try:
#         # Validate MIME type
#         mime_type, _ = guess_type(uploaded_file.name)
#         if not mime_type:
#             raise ValueError("Invalid file type.")

#         # Check if the file is an image or video
#         is_image = mime_type.startswith("image/")
#         is_video = mime_type.startswith("video/")
#         if not (is_image or is_video):
#             raise ValueError("Unsupported file type. Only images and videos are allowed.")

#         # Save the uploaded file
#         with default_storage.open(file_path, 'wb+') as destination:
#             for chunk in uploaded_file.chunks():
#                 destination.write(chunk)

#         # Process images (add watermark)
#         if is_image:
#             with Image.open(file_path) as img:
#                 # Handle transparency if needed
#                 if img.mode in ["P", "RGBA"]:
#                     img = img.convert("RGB")

#                 draw = ImageDraw.Draw(img)

#                 # Define the font and size
#                 try:
#                     font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf')
#                     font = ImageFont.truetype(font_path, 36)
#                 except IOError:
#                     font = ImageFont.load_default()

#                 # Add watermark with current date and time
#                 current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#                 text = f"{current_date}"

#                 # Measure text size
#                 text_bbox = draw.textbbox((0, 0), text, font=font)
#                 text_width = text_bbox[2] - text_bbox[0]
#                 text_height = text_bbox[3] - text_bbox[1]

#                 # Define text position and rectangle background
#                 padding = 10
#                 text_position = (padding, padding)
#                 rectangle_position = (
#                     text_position[0] - padding,
#                     text_position[1] - padding,
#                     text_position[0] + text_width + padding,
#                     text_position[1] + text_height + padding
#                 )

#                 # Draw rectangle and text
#                 draw.rectangle(rectangle_position, fill="#6e6e6e")
#                 draw.text(text_position, text, fill="white", font=font)

#                 # Save the image in the original format
#                 img.save(file_path)

#         # No additional processing for videos; they're saved as-is

#     except Exception as e:
#         # Log error and cleanup
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         print(ValueError(f"Failed to process the file: {e}"))
#         return ''

#     # Get the relative file path for the URL
#     relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
#     file_url = request.build_absolute_uri(settings.MEDIA_URL + relative_file_path.replace("\\", "/"))
#     return file_url


def save_file(folder_path, uploaded_file, request):
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Sanitize the filename
        filename = slugify(Path(uploaded_file.name).stem) + Path(uploaded_file.name).suffix
        file_path = os.path.join(folder_path, filename)

        # Validate MIME type
        mime_type, _ = guess_type(uploaded_file.name)
        if not mime_type:
            return {'msg': 'Invalid file type', 'url': '', 'n': 0}

        # Allowed file types
        allowed_types = ("image/", "video/", "application/pdf", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if not any(mime_type.startswith(t) for t in allowed_types):
            return {'msg': 'Unsupported file type.', 'url': '', 'n': 0}

        # Save the uploaded file
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    except Exception as e:
        logging.error(f"Failed to process the file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return {'msg': f"Failed to process the file: {e}", 'url': '', 'n': 0}

    # Get the relative file path for the URL
    media_root_path = Path(settings.MEDIA_ROOT).resolve()
    file_path_resolved = Path(file_path).resolve()
    
    try:
        relative_file_path = file_path_resolved.relative_to(media_root_path)
    except ValueError:
        logging.error("File path is outside MEDIA_ROOT. Returning absolute URL.")
        relative_file_path = file_path_resolved  # Fall back to absolute path

    file_url = request.build_absolute_uri(settings.MEDIA_URL + str(relative_file_path).replace("\\", "/"))
    return {'msg': 'File saved successfully', 'url': file_url, 'n': 1}






































































