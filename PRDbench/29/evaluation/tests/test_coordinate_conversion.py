import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from order import change_coordinate

def test_coordinate_conversion():
    # Metric 7.1
    # Test case from metric description (although it's not a good example of conversion)
    coords1 = [150, 250, 350, 450]
    expected1 = [150, 250, 350, 450]
    assert change_coordinate(coords1) == expected1

    # Test case with values not at the center
    coords2 = [101, 299, 0, 7]
    expected2 = [150, 250, 50, 50]
    assert change_coordinate(coords2) == expected2