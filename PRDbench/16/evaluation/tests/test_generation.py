import sys
import os
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from PasswordGenerator import PasswordGenerator
from KeyboardProcessor import KeyboardProcessor

@pytest.fixture
def keyboard():
    """Fixture to provide a loaded KeyboardProcessor instance."""
    # The path is relative to the root of the project, where pytest is run
    kp = KeyboardProcessor('src/keyboard.txt')
    kp.get_keyboard_list()
    return kp.keyboard_list

def is_jump_pattern(password, keyboard_list):
    """
    Helper function to validate if a password follows a 'jump' pattern
    based on knight moves in chess, ignoring whitespace characters.
    """
    # Filter out whitespace characters from the password before validation
    password = "".join(password.split())
    
    if len(password) < 2:
        return True

    # Create a coordinate map only for non-whitespace characters
    coords = {item['key']: (item['x'], item['y']) for item in keyboard_list if item['key'].strip()}
    
    # Define the possible knight moves
    jumps = {
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    }

    for i in range(len(password) - 1):
        p1_char, p2_char = password[i], password[i+1]
        
        if p1_char not in coords or p2_char not in coords:
            # This case should ideally not be hit if the generator works correctly
            return False

        p1 = coords[p1_char]
        p2 = coords[p2_char]
        
        dx = abs(p1[0] - p2[0])
        dy = abs(p1[1] - p2[1])

        if (dx, dy) not in jumps:
            return False  # The move is not a valid knight's jump

    return True


def test_jump_generation(keyboard):
    """
    Tests the generation of 'jump' mode passwords.
    """
    generator = PasswordGenerator(keyboard)
    num_to_generate = 3
    length = 8
    
    passwords = []
    for _ in range(num_to_generate):
        pwd = generator.generate_jump_pwd(length)
        passwords.append(pwd)

    assert len(passwords) == num_to_generate, f"Expected {num_to_generate} passwords, but got {len(passwords)}"
    
    for pwd in passwords:
        assert len(pwd) == length, f"Expected password length {length}, but got {len(pwd)} for password '{pwd}'"
        assert is_jump_pattern(pwd, keyboard), f"Password '{pwd}' does not follow a valid jump pattern."