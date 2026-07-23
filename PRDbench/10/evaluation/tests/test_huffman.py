
import sys
import unittest
from pathlib import Path

# Ensure `.../pass_en/10/src` is importable when running pytest from any cwd.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _PROJECT_ROOT / "src"
if _SRC_DIR.exists():
    sys.path.insert(0, str(_SRC_DIR))

from huffman import build_huffman_tree, generate_huffman_codes, Node

class TestHuffman(unittest.TestCase):

    def test_build_huffman_tree(self):
        freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        tree = build_huffman_tree(freq_map)
        self.assertIsInstance(tree, Node)
        self.assertEqual(tree.freq, 100)

    def test_generate_huffman_codes(self):
        freq_map = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        tree = build_huffman_tree(freq_map)
        codes = generate_huffman_codes(tree)
        self.assertEqual(codes['f'], '0')
        self.assertEqual(codes['c'], '100')
        self.assertEqual(codes['d'], '101')
        self.assertEqual(codes['a'], '1100')
        self.assertEqual(codes['b'], '1101')
        self.assertEqual(codes['e'], '111')

    def test_build_tree_with_insufficient_nodes(self):
        with self.assertRaises(ValueError):
            build_huffman_tree({'a': 1})

if __name__ == '__main__':
    unittest.main()
