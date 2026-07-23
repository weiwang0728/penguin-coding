import pytest
import os
import sys
from PIL import Image

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from feature_extractor import extract_dominant_colors, extract_texture_features, analyze_image_features

def test_dominant_colors_extraction():
    """Test dominant color extraction functionality"""
    # Create a test image with known colors
    image = Image.new('RGB', (100, 100), color='red')

    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_color_test_image.jpg')
    image.save(temp_path, format='JPEG')

    try:
        # Extract dominant colors
        colors = extract_dominant_colors(temp_path)

        # Check that we got results
        assert len(colors) > 0

        # Check that the dominant color is red-like (starts with #e or #f)
        dominant_color, percentage = colors[0]
        # Red should be #ff0000, but with color quantization it might be slightly different
        assert dominant_color.startswith('#e') or dominant_color.startswith('#f')
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_texture_extraction():
    """Test texture feature extraction functionality"""
    # Create a test image with a smooth texture
    smooth_image = Image.new('L', (100, 100), color=128)  # Gray image

    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_texture_test_image.jpg')
    smooth_image.save(temp_path, format='JPEG')

    try:
        # Extract texture features
        texture = extract_texture_features(temp_path)

        # For a uniform image, we expect "smooth" texture
        assert texture == "smooth"
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_analyze_image_features():
    """Test overall image feature analysis functionality"""
    # Create a test image
    image = Image.new('RGB', (100, 100), color='blue')

    # Save to temporary file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_analysis_test_image.jpg')
    image.save(temp_path, format='JPEG')

    try:
        # Analyze features
        features = analyze_image_features(temp_path)

        # Check that we got both dominant colors and texture
        assert 'dominant_colors' in features
        assert 'texture' in features

        # Check that dominant colors exist
        assert len(features['dominant_colors']) > 0

        # Check that texture is either "smooth" or "rough"
        assert features['texture'] in ["smooth", "rough"]
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    pytest.main([__file__])
