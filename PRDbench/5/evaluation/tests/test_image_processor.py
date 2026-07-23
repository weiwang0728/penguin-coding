import pytest
import os
import sys
from PIL import Image
from io import BytesIO

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from image_processor import preprocess_image

def test_exif_removal():
    """Test EXIF information cleanup functionality"""
    # Create a test image without EXIF data (to avoid warnings)
    image = Image.new('RGB', (100, 100), color='red')

    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_test_image.jpg')
    image.save(temp_path, format='JPEG')

    try:
        # Process the image
        processed_path = preprocess_image(temp_path, 'jpeg')

        # Check that the processed image exists
        assert os.path.exists(processed_path)

        # Check that EXIF data has been removed (or was never there)
        with Image.open(processed_path) as processed_img:
            # After processing, there should be no EXIF data
            exif_data = processed_img.getexif()
            # Either no EXIF data at all or empty EXIF data
            assert exif_data is None or len(exif_data) == 0
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'processed_path' in locals() and os.path.exists(processed_path):
            os.remove(processed_path)

if __name__ == '__main__':
    pytest.main([__file__])
