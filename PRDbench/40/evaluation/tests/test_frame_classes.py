import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_frame_builder_parser_existence():
    """Test if FrameBuilder and FrameParser classes exist"""
    try:
        # Try to import FrameBuilder and FrameParser classes
        from utils.frame import FrameBuilder, FrameParser

        # Check FrameBuilder class methods
        builder_methods = ['build', 'construct', 'create_frame']
        builder_instance = FrameBuilder()

        builder_found_methods = []
        for method in builder_methods:
            if hasattr(builder_instance, method):
                builder_found_methods.append(method)

        assert len(builder_found_methods) > 0, "FrameBuilder class is missing frame construction method"

        # Check FrameParser class methods
        parser_methods = ['parse', 'decode', 'validate', 'extract']
        parser_instance = FrameParser()

        parser_found_methods = []
        for method in parser_methods:
            if hasattr(parser_instance, method):
                parser_found_methods.append(method)

        assert len(parser_found_methods) > 0, "FrameParser class is missing parsing method"

        # Verify class basic functionality
        assert callable(getattr(builder_instance, builder_found_methods[0])), "FrameBuilder method is not callable"
        assert callable(getattr(parser_instance, parser_found_methods[0])), "FrameParser method is not callable"

    except ImportError as e:
        pytest.fail(f"Unable to import FrameBuilder or FrameParser class: {str(e)}")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")