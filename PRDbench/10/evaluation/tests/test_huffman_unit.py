import pytest
import sys
import os

# Add the src directory to the Python path to import modules from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from huffman import build_huffman_tree, generate_huffman_codes, Node

def test_build_huffman_tree():
    """
    Test if the build_huffman_tree function correctly builds a Huffman tree.
    """
    freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
    tree = build_huffman_tree(freq_map)
    assert isinstance(tree, Node)
    assert tree.freq == 100


def test_generate_huffman_codes():
    """
    Test if the generate_huffman_codes function correctly generates Huffman codes.
    """
    freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
    tree = build_huffman_tree(freq_map)
    codes = generate_huffman_codes(tree)

    # Verify that the encoding for specific characters meets expectations (based on standard Huffman encoding rules)
    assert codes['f'] == '0'
    assert codes['c'] == '100'
    assert codes['d'] == '101'
    assert codes['a'] == '1100'
    assert codes['b'] == '1101'
    assert codes['e'] == '111'


def test_build_tree_with_insufficient_nodes():
    """
    Test if the build_huffman_tree function raises a ValueError when input nodes are insufficient.
    """
    with pytest.raises(ValueError):
        build_huffman_tree({'a': 1})

if __name__ == '__main__':
    pytest.main([__file__, '-v'])