"""
Image Processing Utilities
"""
from PIL import Image
import io
from pathlib import Path

def optimize_image(image_path: Path, max_width: int = 1200, max_height: int = 1200, quality: int = 85):
    """
    Optimize uploaded image: resize if too large and reduce quality
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize if image is too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, quality=quality, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return False

def create_thumbnail(image_path: Path, size: tuple = (300, 300)) -> Path:
    """
    Create a thumbnail version of an image
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            thumb_path = image_path.parent / f"thumb_{image_path.name}"
            img.save(thumb_path, quality=85, optimize=True)
            
            return thumb_path
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None
